import { ChatInputCommandDeniedPayload, Events, Listener, UserError } from '@sapphire/framework';

import embeds from '@lib/embeds';

export class CommandDenied extends Listener<typeof Events.ChatInputCommandDenied> {
  public constructor(context: Listener.Context, options: Listener.Options) {
    super(context, {
      ...options,
      event: 'chatInputCommandDenied',
    });
  }

  public override async run(error: UserError, { interaction }: ChatInputCommandDeniedPayload) {
    await interaction.reply({ embeds: [embeds.card(':x: Command failed', error.message)], ephemeral: true });
  }
}
