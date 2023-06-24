import { InteractionHandler as BaseInteractionHandler } from '@sapphire/framework';
import { Interaction } from 'discord.js';

import { withSpan } from '@lib/tracing';

import { formatInteractionType, setChannelAttributes, setGuildAttributes, setUserAttributes, tracer } from './utils';

export abstract class InteractionHandler<
  O extends BaseInteractionHandler.Options = BaseInteractionHandler.Options,
> extends BaseInteractionHandler<O> {
  protected constructor(context: BaseInteractionHandler.Context, options: O = {} as O) {
    super(context, options);

    this.run = this.instrumentedRun(this.run.bind(this));
  }

  private instrumentedRun(
    fn: (interaction: Interaction, parsedData?: unknown) => unknown,
  ): (interaction: Interaction, parsedData?: unknown) => unknown {
    return (interaction, parsedData) =>
      withSpan(
        'interaction.' + this.name,
        async (span) => {
          span.setAttributes({
            'discord.route': 'interaction.' + this.name,
            'interaction.id': interaction.id,
            'interaction.type': formatInteractionType(interaction.type),
          });
          setUserAttributes(span, interaction.user);
          setGuildAttributes(span, interaction.guild);
          setChannelAttributes(span, interaction.channel);

          return await fn(interaction, parsedData);
        },
        tracer,
      );
  }
}

export namespace InteractionHandler {
  export type Context = BaseInteractionHandler.Context;
  export type Options = BaseInteractionHandler.Options;
  export type JSON = BaseInteractionHandler.JSON;
  export type ParseResult<Instance extends BaseInteractionHandler> = BaseInteractionHandler.ParseResult<Instance>;
}
