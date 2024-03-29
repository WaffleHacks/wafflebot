import { trace } from '@opentelemetry/api';
import { CommandOptionsRunTypeEnum } from '@sapphire/framework';
import { APIUser } from 'discord-api-types/v10';
import {
  ApplicationCommandType,
  CommandInteraction,
  ContextMenuCommandInteraction,
  EmbedBuilder,
  User,
  userMention,
} from 'discord.js';

import { Link } from '@lib/database';
import embeds from '@lib/embeds';
import { UserInfo, lookupParticipantByEmail, lookupParticipantByID } from '@lib/portal';
import { Command } from '@lib/sapphire';
import { withSpan } from '@lib/tracing';

export class WhoCommand extends Command {
  public constructor(context: Command.Context, options: Command.Options) {
    super(context, {
      ...options,
      description: 'Lookup who a participant is by Discord username or email',
      runIn: CommandOptionsRunTypeEnum.GuildText,
      generateDashLessAliases: true,
    });
  }

  public override registerApplicationCommands(registry: Command.Registry) {
    registry.registerChatInputCommand((builder) =>
      builder //
        .setName(this.name)
        .setDescription(this.description)
        .setDMPermission(false)
        .addStringOption((option) => option.setName('email').setDescription('The email to lookup').setRequired(false))
        .addUserOption((option) => option.setName('user').setDescription('The user to lookup').setRequired(false)),
    );
    registry.registerContextMenuCommand((builder) =>
      builder.setName('Lookup application').setType(ApplicationCommandType.User).setDMPermission(false),
    );
    registry.registerContextMenuCommand((builder) =>
      builder.setName('Lookup author application').setType(ApplicationCommandType.Message).setDMPermission(false),
    );
  }

  public override async chatInputRun(interaction: Command.ChatInputCommandInteraction) {
    const email = interaction.options.getString('email', false);
    const user = interaction.options.getUser('user', false);

    await this.findAndResponse(interaction, email, user);
  }

  public override async contextMenuRun(interaction: ContextMenuCommandInteraction) {
    let user: User | APIUser;
    if (interaction.isUserContextMenuCommand()) user = interaction.targetUser;
    else if (interaction.isMessageContextMenuCommand()) user = interaction.targetMessage.author;
    else throw new Error('assertion failed: only user and message context menu commands are allowed');

    await this.findAndResponse(interaction, null, user);
  }

  private async findAndResponse(interaction: CommandInteraction, email: string | null, user: User | APIUser | null) {
    const span = trace.getActiveSpan();
    span?.setAttributes({
      'query.email': email ?? undefined,
      'query.user.id': user?.id ?? undefined,
      'query.user.name': this.formatUsername(user),
    });

    await withSpan('reply.defer', () => interaction.deferReply({ ephemeral: true }));

    let embed: EmbedBuilder;
    const info = await this.lookup(email, user);
    if (info === null) {
      span?.setAttributes({ 'participant.id': 'unknown', 'participant.discord': 'unknown' });
      embed = embeds.card(
        ':grey_question: Participant not found',
        "We looked everywhere, but couldn't find any participants matching your query. Please check it is correct and try again.",
      );
    } else {
      span?.setAttribute('participant.id', info.id);

      const userId = await Link.findDiscordId(info.id);
      span?.setAttribute('participant.discord', userId === null ? 'unknown' : userId);

      embed = embeds
        .card(`${info.first_name} ${info.last_name}`)
        .setURL(info.link)
        .addFields(
          { name: 'Email', value: info.email, inline: true },
          { name: 'Discord', value: userId === null ? 'N/A' : userMention(userId), inline: true },
        );
    }

    await withSpan('reply.edit', () => interaction.editReply({ embeds: [embed] }));
  }

  private async lookup(email: string | null, user: User | APIUser | null): Promise<UserInfo | null> {
    if (email !== null) return lookupParticipantByEmail(email);

    if (user !== null) {
      const participantId = await Link.findParticipantId(user.id);
      if (participantId === null) return null;

      return lookupParticipantByID(participantId);
    }

    return null;
  }

  private formatUsername(user: User | APIUser | null): string | undefined {
    if (user === null) return undefined;
    else if (user.discriminator === '0') return user.username;
    else return `${user.username}#${user.discriminator}`;
  }
}
