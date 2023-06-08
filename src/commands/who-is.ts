import { Command, CommandOptionsRunTypeEnum } from '@sapphire/framework';
import { EmbedBuilder, User, userMention } from 'discord.js';

import { Link } from '@lib/database';
import embeds from '@lib/embeds';
import { UserInfo, lookupParticipantByEmail, lookupParticipantByID } from '@lib/portal';

export class WhoIsCommand extends Command {
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
  }

  public override async chatInputRun(interaction: Command.ChatInputCommandInteraction) {
    const email = interaction.options.getString('email', false);
    const user = interaction.options.getUser('user', false);

    await interaction.deferReply({ ephemeral: true });

    let embed: EmbedBuilder;
    const info = await this.lookup(email, user);
    if (info === null) {
      embed = embeds.card(
        ':grey_question: Participant not found',
        "We looked everywhere, but couldn't find any participants matching your query. Please check it is correct and try again.",
      );
    } else {
      const userId = await Link.findDiscordId(info.id);

      embed = embeds
        .card(`${info.first_name} ${info.last_name}`)
        .setURL(info.link)
        .addFields(
          { name: 'Email', value: info.email, inline: true },
          { name: 'Discord', value: userId === null ? 'N/A' : userMention(userId), inline: true },
        );
    }

    return interaction.editReply({ embeds: [embed] });
  }

  private async lookup(email: string | null, user: User | null): Promise<UserInfo | null> {
    if (email !== null) return lookupParticipantByEmail(email);

    if (user !== null) {
      const participantId = await Link.findParticipantId(user.id);
      if (participantId === null) return null;

      return lookupParticipantByID(participantId);
    }

    return null;
  }
}
