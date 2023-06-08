import { InteractionHandler, InteractionHandlerTypes, Piece } from '@sapphire/framework';
import { ActionRowBuilder, type ButtonInteraction, ModalBuilder, TextInputBuilder, TextInputStyle } from 'discord.js';

export class VerifyButtonHandler extends InteractionHandler {
  constructor(context: Piece.Context, options: InteractionHandler.Options) {
    super(context, { ...options, interactionHandlerType: InteractionHandlerTypes.Button });
  }

  public async run(interaction: ButtonInteraction) {
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
}
