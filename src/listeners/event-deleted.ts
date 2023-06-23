import { Event } from '@lib/database';
import nats, { EventChanged } from '@lib/nats';
import { Listener } from '@lib/sapphire';
import * as scheduledEvents from '@lib/scheduled-events';

export class EventDeleted extends Listener {
  public constructor(context: Listener.Context, options: Listener.Options) {
    super(context, {
      ...options,
      emitter: nats,
      event: 'workshops.automated.deleted',
    });
  }

  public override async run(data: EventChanged) {
    const discordId = await Event.find(data.event_id);
    if (discordId === null) return;

    await scheduledEvents.remove(this.container.client, data.event_id, discordId);
  }
}
