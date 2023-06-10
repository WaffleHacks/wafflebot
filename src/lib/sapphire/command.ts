import { SpanStatusCode, trace } from '@opentelemetry/api';
import { Args, Awaitable, Command as BaseCommand, ChatInputCommand, MessageCommand } from '@sapphire/framework';
import { APIUser, ApplicationCommandType, ChannelType } from 'discord-api-types/v10';
import { CacheType, CommandInteraction, DMChannel, Message, TextChannel, ThreadChannel, User } from 'discord.js';

const tracer = trace.getTracer('@sapphire/framework');

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
      tracer.startActiveSpan(this.name, async (span) => {
        span.setAttributes({
          'message.id': message.id,
          'channel.id': message.channelId,
          'channel.type': this.formatChannelType(message.channel.type),
          'user.id': message.author.id,
          'user.name': this.extractUserName(message.author),
          'user.bot': message.author.bot,
        });
        if (message.guild)
          span.setAttributes({
            'guild.id': message.guild.id,
            'guild.name': message.guild.name,
            'guild.locale': message.guild.preferredLocale,
          });

        try {
          return await fn(message, args, context);
        } catch (e) {
          if (e instanceof Error) {
            span.recordException(e);
            span.setStatus({ code: SpanStatusCode.ERROR });
          }

          throw e;
        } finally {
          span.end();
        }
      });
  }

  private instrumentedInteractionRun<T extends CommandInteraction>(
    fn: (interaction: T, context: ChatInputCommand.RunContext) => Awaitable<unknown>,
  ): (interaction: T, context: ChatInputCommand.RunContext) => Awaitable<unknown> {
    return (interaction, context) =>
      tracer.startActiveSpan(this.name, async (span) => {
        span.setAttributes({
          'command.id': interaction.commandId,
          'command.name': interaction.commandName,
          'command.type': this.formatCommandType(interaction.commandType),
          'channel.id': interaction.channelId,
          'user.id': interaction.user.id,
          'user.name': this.extractUserName(interaction.user),
          'user.bot': interaction.user.bot,
        });
        if (interaction.guild)
          span.setAttributes({
            'guild.id': interaction.guild.id,
            'guild.name': interaction.guild.name,
            'guild.locale': interaction.guild.preferredLocale,
          });
        if (interaction.channel) {
          span.setAttribute('channel.type', this.formatChannelType(interaction.channel.type));
          if (interaction.channel instanceof TextChannel) span.setAttribute('channel.name', interaction.channel.name);
          else if (interaction.channel instanceof DMChannel) span.setAttribute('channel.type', 'dm');
          else if (interaction.channel instanceof ThreadChannel && interaction.channel.parent)
            span.setAttributes({
              'channel.parent.id': interaction.channel.parent.id,
              'channel.parent.name': interaction.channel.parent.name,
              'channel.parent.type': this.formatChannelType(interaction.channel.parent.type),
            });
        }

        try {
          return await fn(interaction, context);
        } catch (e) {
          if (e instanceof Error) {
            span.recordException(e);
            span.setStatus({ code: SpanStatusCode.ERROR });
          }

          throw e;
        } finally {
          span.end();
        }
      });
  }

  private extractUserName(user: User | APIUser): string {
    if (user.discriminator === '0') return user.username;
    else return `${user.username}#${user.discriminator}`;
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

  private formatChannelType(type: ChannelType): string {
    switch (type) {
      case ChannelType.GuildText:
        return 'guild.text';
      case ChannelType.DM:
        return 'dm';
      case ChannelType.GuildVoice:
        return 'guild.voice';
      case ChannelType.GroupDM:
        return 'dm.group';
      case ChannelType.GuildCategory:
        return 'guild.category';
      case ChannelType.GuildAnnouncement:
        return 'guild.announcement';
      case ChannelType.AnnouncementThread:
        return 'guild.announcement.thread';
      case ChannelType.GuildPublicThread:
      case ChannelType.PublicThread:
        return 'guild.thread.public';
      case ChannelType.GuildPrivateThread:
      case ChannelType.PrivateThread:
        return 'guild.thread.private';
      case ChannelType.GuildStageVoice:
        return 'guild.stage';
      case ChannelType.GuildDirectory:
        return 'guild.directory';
      case ChannelType.GuildForum:
        return 'guild.forum';
      case ChannelType.GuildNews:
        return 'guild.news';
      case ChannelType.GuildNewsThread:
        return 'guild.thread.news';
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
