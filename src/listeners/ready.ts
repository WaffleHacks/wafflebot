import notifier from '@lib/notifier';
import { Listener } from '@lib/sapphire';

export class ReadyListener extends Listener {
  public constructor(context: Listener.Context, options: Listener.Options) {
    super(context, {
      ...options,
      event: 'ready',
    });
  }

  public override async run() {
    await notifier.start();
  }
}
