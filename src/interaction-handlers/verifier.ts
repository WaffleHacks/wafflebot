import { InteractionHandler, InteractionHandlerTypes, Piece } from '@sapphire/framework';
import { GuildMemberRoleManager, type ModalSubmitInteraction } from 'discord.js';

import { Settings } from '@lib/database';
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
        content: ':x: Verification is not setup properly, please contact an organizer.',
      });
      return;
    }

    await interaction.deferReply({ ephemeral: true });

    const email = interaction.fields.getTextInputValue('email');
    const status = await lookupApplicationStatusByEmail(email);

    if (status === Status.ACCEPTED) await interaction.member.roles.add(roleId);
    else await interaction.member.roles.remove(roleId);

    await interaction.editReply({ content: this.messageForStatus(status) });
  }

  public override parse(interaction: ModalSubmitInteraction) {
    if (interaction.customId === 'verifier') return this.some();
    else return this.some();
  }

  private messageForStatus(status: Status | null): string {
    switch (status) {
      case null:
        return "It looks like you haven't submitted an application yet.\n\nGo to https://apply.wafflehacks.org to submit one now! It will only take a couple minutes!";
      case Status.PENDING:
        return 'We found your application, but it is still being reviewed. Please wait until you get your application decision and then try again.';
      case Status.REJECTED:
        return 'Unfortunately, it looks like your application was rejected. We are unable to admit you into the event server.';
      case Status.ACCEPTED:
        return "You've now been given access to the rest of the server! Have fun and good luck!";
    }
  }
}
