import { Listener as BaseListener } from '@sapphire/framework';
import { ClientEvents } from 'discord.js';

import { withSpan } from '@lib/tracing';

export abstract class Listener<
  E extends keyof ClientEvents | symbol = '',
  O extends BaseListener.Options = BaseListener.Options,
> extends BaseListener<E, O> {
  protected constructor(context: BaseListener.Context, options?: O) {
    super(context, options);

    this.run = this.instrumentedRun(this.run.bind(this));
  }

  private instrumentedRun(
    fn: (...args: E extends keyof ClientEvents ? ClientEvents[E] : unknown[]) => unknown,
  ): (...args: E extends keyof ClientEvents ? ClientEvents[E] : unknown[]) => unknown {
    return (...args) =>
      withSpan('listener.' + this.name, async (span) => {
        span.setAttributes({
          'discord.route': 'listener.' + this.name,
          'listener.event': this.event.toString(),
        });
        return await fn(...args);
      });
  }
}

export namespace Listener {
  export type Options = BaseListener.Options;
  export type JSON = BaseListener.JSON;
  export type Context = BaseListener.Context;
}
