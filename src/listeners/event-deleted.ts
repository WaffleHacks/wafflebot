import { GUILD_ID } from '@lib/config';
import { Event } from '@lib/database';
import nats, { EventChanged } from '@lib/nats';
import { Listener } from '@lib/sapphire';

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

    try {
      const guild = await this.container.client.guilds.fetch(GUILD_ID);
      await guild.scheduledEvents.delete(discordId);
    } catch {}

    await Event.delete(discordId);
  }
}
