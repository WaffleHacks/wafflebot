import { Precondition } from '@sapphire/framework';
import type { ChatInputCommandInteraction } from 'discord.js';

import { Settings } from '@lib/database';

export class ParticipantRoleIsSetPrecondition extends Precondition {
  public override async chatInputRun(interaction: ChatInputCommandInteraction) {
    const roleId = await Settings.getParticipantRole();
    if (roleId === null)
      return this.error({
        message: 'The participant role must be set before using this command. You can set it with `/participant-role`.',
      });

    if (interaction.guild === null)
      return this.error({ message: 'This precondition is only valid for guild commands' });

    const role = await interaction.guild.roles.fetch(roleId);
    if (role === null)
      return this.error({ message: 'The participant role no longer exists. Set it with `/participant-role`.' });

    return this.ok();
  }
}

declare module '@sapphire/framework' {
  interface Preconditions {
    ParticipantRoleIsSet: never;
  }
}
