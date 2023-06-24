import { Args, Awaitable, Command as BaseCommand, ChatInputCommand, MessageCommand } from '@sapphire/framework';
import { ApplicationCommandType } from 'discord-api-types/v10';
import { CacheType, CommandInteraction, Message } from 'discord.js';

import { withSpan } from '@lib/tracing';

import { setChannelAttributes, setGuildAttributes, setUserAttributes } from './utils';

export class Command<PreParseRun = Args, O extends BaseCommand.Options = BaseCommand.Options> extends BaseCommand<
  PreParseRun,
  O
> {
  constructor(context: BaseCommand.Context, options: O = {} as O) {
    super(context, options);

    if (this.messageRun) this.messageRun = this.instrumentedMessageRun(this.messageRun.bind(this));
    if (this.chatInputRun) this.chatInputRun = this.instrumentedInteractionRun(this.chatInputRun.bind(this));
    if (this.contextMenuRun) this.contextMenuRun = this.instrumentedInteractionRun(this.contextMenuRun.bind(this));
  }

  private instrumentedMessageRun(
    fn: (message: Message, args: PreParseRun, context: MessageCommand.RunContext) => Awaitable<unknown>,
  ): (message: Message, args: PreParseRun, context: MessageCommand.RunContext) => Awaitable<unknown> {
    return (message, args, context) =>
      withSpan('command.' + this.name, async (span) => {
        span.setAttributes({
          'discord.route': 'command.' + this.name,
          'message.id': message.id,
        });
        setUserAttributes(span, message.author);
        setChannelAttributes(span, message.channel);
        setGuildAttributes(span, message.guild);

        return fn(message, args, context);
      });
  }

  private instrumentedInteractionRun<T extends CommandInteraction>(
    fn: (interaction: T, context: ChatInputCommand.RunContext) => Awaitable<unknown>,
  ): (interaction: T, context: ChatInputCommand.RunContext) => Awaitable<unknown> {
    return (interaction, context) =>
      withSpan('command.' + this.name, async (span) => {
        span.setAttributes({
          'discord.route': 'command.' + this.name,
          'command.id': interaction.commandId,
          'command.name': interaction.commandName,
          'command.type': this.formatCommandType(interaction.commandType),
        });
        setUserAttributes(span, interaction.user);
        setGuildAttributes(span, interaction.guild);
        setChannelAttributes(span, interaction.channel);

        return fn(interaction, context);
      });
  }

  private formatCommandType(type: ApplicationCommandType): string {
    switch (type) {
      case ApplicationCommandType.ChatInput:
        return 'slash';
      case ApplicationCommandType.User:
        return 'context-menu.user';
      case ApplicationCommandType.Message:
        return 'context-menu.message';
    }
  }
}

export namespace Command {
  export type Options = BaseCommand.Options;
  export type JSON = BaseCommand.JSON;
  export type Context = BaseCommand.Context;
  export type RunInTypes = BaseCommand.RunInTypes;
  export type ChatInputCommandInteraction<Cached extends CacheType = CacheType> =
    BaseCommand.ChatInputCommandInteraction<Cached>;
  export type ContextMenuCommandInteraction<Cached extends CacheType = CacheType> =
    BaseCommand.ContextMenuCommandInteraction<Cached>;
  export type AutocompleteInteraction<Cached extends CacheType = CacheType> =
    BaseCommand.AutocompleteInteraction<Cached>;
  export type Registry = BaseCommand.Registry;
}
