import { Event } from '@lib/database';
import nats, { EventChanged } from '@lib/nats';
import { findEvent } from '@lib/portal';
import { Listener } from '@lib/sapphire';
import * as scheduledEvents from '@lib/scheduled-events';

export class EventUpdated extends Listener {
  public constructor(context: Listener.Context, options: Listener.Options) {
    super(context, {
      ...options,
      emitter: nats,
      event: 'workshops.automated.updated',
    });
  }

  public override async run(data: EventChanged) {
    const details = await findEvent(data.event_id);
    const discordId = await Event.find(data.event_id);

    // portal | discord | action
    //    y   |    n    | create
    //    n   |    n    | do nothing
    //    y   |    y    | update
    //    n   |    y    | delete

    const client = this.container.client;

    if (details !== null && discordId === null) await scheduledEvents.create(client, details);
    else if (details !== null && discordId !== null) await scheduledEvents.update(client, details, discordId);
    else if (details === null && discordId !== null) await scheduledEvents.remove(client, discordId);
  }
}
