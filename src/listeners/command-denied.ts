import { trace } from '@opentelemetry/api';
import { ChatInputCommandDeniedPayload, Events, UserError } from '@sapphire/framework';

import embeds from '@lib/embeds';
import { Listener } from '@lib/sapphire';

export class CommandDenied extends Listener<typeof Events.ChatInputCommandDenied> {
  public constructor(context: Listener.Context, options: Listener.Options) {
    super(context, {
      ...options,
      event: 'chatInputCommandDenied',
    });
  }

  public override async run(error: UserError, { interaction }: ChatInputCommandDeniedPayload) {
    trace.getActiveSpan()?.setAttributes({
      'user-error.name': error.name,
      'user-error.message': error.message,
      'user-error.context': JSON.stringify(error.context),
      'user-error.identifier': error.identifier,
    });

    await interaction.reply({ embeds: [embeds.card(':x: Command failed', error.message)], ephemeral: true });
  }
}
