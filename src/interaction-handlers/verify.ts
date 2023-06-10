import { InteractionHandlerTypes, Piece } from '@sapphire/framework';
import { ActionRowBuilder, type ButtonInteraction, ModalBuilder, TextInputBuilder, TextInputStyle } from 'discord.js';

import { Settings } from '@lib/database';
import embeds from '@lib/embeds';
import { InteractionHandler } from '@lib/sapphire';
import { withSpan } from '@lib/tracing';

export class VerifyButtonHandler extends InteractionHandler {
  constructor(context: Piece.Context, options: InteractionHandler.Options) {
    super(context, { ...options, interactionHandlerType: InteractionHandlerTypes.Button });
  }

  public async run(interaction: ButtonInteraction) {
    if (await this.verificationNotSetup(interaction)) {
      return withSpan(
        'reply.failure',
        async () =>
          await interaction.reply({
            ephemeral: true,
            embeds: [embeds.card(':x: Verification is not setup properly', 'Please contact an organizer')],
          }),
      );
    }

    const modal = new ModalBuilder()
      .setCustomId('verifier')
      .setTitle('Get verified!')
      .addComponents(
        new ActionRowBuilder<TextInputBuilder>().addComponents(
          new TextInputBuilder()
            .setCustomId('email')
            .setLabel("What's the email you applied with?")
            .setRequired(true)
            .setStyle(TextInputStyle.Short),
        ),
      );
    await withSpan('modal', async () => await interaction.showModal(modal));
  }

  public override parse(interaction: ButtonInteraction) {
    if (interaction.customId === 'verify') return this.some();
    else return this.none();
  }

  private async verificationNotSetup(interaction: ButtonInteraction): Promise<boolean> {
    return withSpan('check.verification-not-setup', async () => {
      const participantRoleId = await Settings.getParticipantRole();
      if (participantRoleId === null) return true;

      const participantRole = await withSpan('role.fetch', async (span) => {
        span.setAttribute('role.id', participantRoleId);
        return interaction.guild?.roles.fetch(participantRoleId);
      });
      if (participantRole === null || participantRole == undefined) return true;

      const verification = await Settings.getVerificationMessage();
      return verification === null;
    });
  }
}
