import { trace } from '@opentelemetry/api';
import { CommandOptionsRunTypeEnum } from '@sapphire/framework';
import { roleMention } from 'discord.js';

import { Settings } from '@lib/database';
import embeds from '@lib/embeds';
import { Command } from '@lib/sapphire';

export class ParticipantRoleCommand extends Command {
  public constructor(context: Command.Context, options: Command.Options) {
    super(context, {
      ...options,
      description: 'Get or set the role participants should have',
      runIn: CommandOptionsRunTypeEnum.GuildText,
    });
  }

  public override registerApplicationCommands(registry: Command.Registry) {
    registry.registerChatInputCommand((builder) =>
      builder //
        .setName(this.name)
        .setDescription(this.description)
        .setDMPermission(false)
        .addRoleOption((option) =>
          option.setName('to').setDescription('The role to apply to participants').setRequired(false),
        ),
    );
  }

  public override async chatInputRun(interaction: Command.ChatInputCommandInteraction) {
    const role = interaction.options.getRole('to', false);

    const span = trace.getActiveSpan();

    if (role) {
      span?.setAttributes({ action: 'update', 'role.id': role.id, 'role.name': role.name });

      await Settings.setParticipantRole(role.id);

      const mention = roleMention(role.id);
      return interaction.reply({
        embeds: [
          embeds.message(`Successfully set participant role to ${mention}. You can now run \`/setup-verification\`.`),
        ],
        ephemeral: true,
      });
    } else {
      span?.setAttribute('action', 'query');
      const id = await Settings.getParticipantRole();

      if (id !== null) {
        span?.setAttribute('role.id', id);
        const mention = roleMention(id);
        return interaction.reply({
          embeds: [embeds.message(`The participant role is currently set to ${mention}.`)],
          ephemeral: true,
        });
      } else {
        span?.setAttribute('role.id', 'unknown');
        return interaction.reply({
          embeds: [
            embeds.card(
              'The participant role is not set',
              'You must set the role before setting up verification with `/setup-verification`.',
            ),
          ],
          ephemeral: true,
        });
      }
    }
  }
}
