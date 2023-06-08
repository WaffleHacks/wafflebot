import { InteractionHandler, InteractionHandlerTypes, Piece } from '@sapphire/framework';
import { EmbedBuilder, GuildMemberRoleManager, type ModalSubmitInteraction } from 'discord.js';

import { Link, Settings } from '@lib/database';
import embeds from '@lib/embeds';
import { Status, lookupApplicationStatusByEmail } from '@lib/portal';

export class ModalHandler extends InteractionHandler {
  constructor(context: Piece.Context, options: InteractionHandler.Options) {
    super(context, { ...options, interactionHandlerType: InteractionHandlerTypes.ModalSubmit });
  }

  public async run(interaction: ModalSubmitInteraction) {
    if (interaction.member === null) throw new Error('assertion failed: member must not be null');
    if (!(interaction.member.roles instanceof GuildMemberRoleManager))
      throw new Error('assertion failed: member.roles must be instance of GuildMemberRoleManager');

    const roleId = await Settings.getParticipantRole();
    if (roleId === null) {
      await interaction.reply({
        ephemeral: true,
        embeds: [embeds.card(':x: Verification is not setup properly', 'Please contact an organizer')],
      });
      return;
    }

    await interaction.deferReply({ ephemeral: true });

    const email = interaction.fields.getTextInputValue('email');
    const application = await lookupApplicationStatusByEmail(email);

    if (application.status === Status.ACCEPTED) {
      await interaction.member.roles.add(roleId);
      await Link.create(interaction.member.user.id, application.id as number);
    } else await interaction.member.roles.remove(roleId);

    await interaction.editReply({ embeds: [this.messageForStatus(application.status)] });
  }

  public override parse(interaction: ModalSubmitInteraction) {
    if (interaction.customId === 'verifier') return this.some();
    else return this.some();
  }

  private messageForStatus(status: Status | null): EmbedBuilder {
    switch (status) {
      case null:
        return embeds.card(
          ":grey_question: It looks like you haven't submitted an application yet",
          'Go to https://apply.wafflehacks.org to submit one now! It will only take a couple minutes!',
        );
      case Status.PENDING:
        return embeds.card(
          ':grey_question: Your application is still being reviewed',
          'Please wait until you receive your application decision via email and then try again.',
        );
      case Status.REJECTED:
        return embeds.card(
          ':x: Unfortunately it looks like your application was rejected',
          'We are unable to admit you into the event server. Please apply again next year!',
        );
      case Status.ACCEPTED:
        return embeds.card(
          ":white_check_mark: You've been verified!",
          "You've now been given access to the rest of the server! Have fun and good luck!",
        );
    }
  }
}
