import { CommandOptionsRunTypeEnum } from '@sapphire/framework';
import { EmbedBuilder } from 'discord.js';

import { Link } from '@lib/database';
import embeds from '@lib/embeds';
import { checkInParticipant } from '@lib/portal';
import { Command } from '@lib/sapphire';
import { withSpan } from '@lib/tracing';

export class CheckInCommand extends Command {
  public constructor(context: Command.Context, options: Command.Options) {
    super(context, {
      ...options,
      description: 'Check yourself into WaffleHacks',
      runIn: CommandOptionsRunTypeEnum.GuildText,
    });
  }

  public override registerApplicationCommands(registry: Command.Registry) {
    registry.registerChatInputCommand((builder) =>
      builder //
        .setName(this.name)
        .setDescription(this.description),
    );
  }

  public override async chatInputRun(interaction: Command.ChatInputCommandInteraction) {
    await withSpan('reply.defer', () => interaction.deferReply({ ephemeral: true }));

    const id = await Link.findParticipantId(interaction.user.id);
    if (id === null) {
      return await withSpan('reply.edit', () =>
        interaction.editReply({
          embeds: [embeds.card(':x: Check-in failed', 'You must be verified before using this command.')],
        }),
      );
    }

    const success = await checkInParticipant(id);

    let embed: EmbedBuilder;
    if (success) embed = embeds.card(":white_check_mark: You're checked in!");
    else
      embed = embeds.card(
        ":x: Check in isn't open yet",
        'Try again after opening ceremony. If you think this is an error, contact an organizer.',
      );

    await withSpan('reply.edit', () => interaction.editReply({ embeds: [embed] }));
  }
}
