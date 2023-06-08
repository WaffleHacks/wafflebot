import { InteractionHandler, InteractionHandlerTypes, Piece } from '@sapphire/framework';
import { ActionRowBuilder, type ButtonInteraction, ModalBuilder, TextInputBuilder, TextInputStyle } from 'discord.js';

import { Settings } from '@lib/database';
import embeds from '@lib/embeds';

export class VerifyButtonHandler extends InteractionHandler {
  constructor(context: Piece.Context, options: InteractionHandler.Options) {
    super(context, { ...options, interactionHandlerType: InteractionHandlerTypes.Button });
  }

  public async run(interaction: ButtonInteraction) {
    if (await this.verificationNotSetup(interaction)) {
      await interaction.reply({
        ephemeral: true,
        embeds: [embeds.card(':x: Verification is not setup properly', 'Please contact an organizer')],
      });
      return;
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
    await interaction.showModal(modal);
  }

  public override parse(interaction: ButtonInteraction) {
    if (interaction.customId === 'verify') return this.some();
    else return this.none();
  }

  private async verificationNotSetup(interaction: ButtonInteraction): Promise<boolean> {
    const participantRoleId = await Settings.getParticipantRole();
    if (participantRoleId === null) return true;

    const participantRole = await interaction.guild?.roles.fetch(participantRoleId);
    if (participantRole === null || participantRole == undefined) return true;

    const verification = await Settings.getVerificationMessage();
    return verification === null;
  }
}
