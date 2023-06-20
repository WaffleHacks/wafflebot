import { GuildScheduledEventEntityType, GuildScheduledEventPrivacyLevel } from 'discord-api-types/v10';

import { GUILD_ID } from '@lib/config';
import { Event } from '@lib/database';
import nats, { EventChanged } from '@lib/nats';
import { EventDetails, findEvent } from '@lib/portal';
import { Listener } from '@lib/sapphire';

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

    if (details !== null && discordId === null) await this.create(details);
    else if (details !== null && discordId !== null) await this.update(details, discordId);
    else if (details === null && discordId !== null) await this.delete(discordId);
  }

  private async create(details: EventDetails) {
    const guild = await this.container.client.guilds.fetch(GUILD_ID);
    const created = await guild.scheduledEvents.create({
      name: details.name,
      scheduledStartTime: details.start,
      scheduledEndTime: details.end,
      privacyLevel: GuildScheduledEventPrivacyLevel.GuildOnly,
      entityType: GuildScheduledEventEntityType.External,
      entityMetadata: {
        location: details.url,
      },
    });

    await Event.create(details.id, created.id);
  }

  private async update(details: EventDetails, discordId: string) {
    try {
      const guild = await this.container.client.guilds.fetch(GUILD_ID);
      await guild.scheduledEvents.edit(discordId, {
        name: details.name,
        scheduledStartTime: details.start,
        scheduledEndTime: details.end,
        privacyLevel: GuildScheduledEventPrivacyLevel.GuildOnly,
        entityType: GuildScheduledEventEntityType.External,
        entityMetadata: {
          location: details.url,
        },
      });
    } catch {
      // Delete the mapping if we can't update the event
      await Event.delete(discordId);
    }
  }

  private async delete(discordId: string) {
    try {
      const guild = await this.container.client.guilds.fetch(GUILD_ID);
      await guild.scheduledEvents.delete(discordId);
    } catch {}

    // Delete the mapping no matter what happens with Discord
    await Event.delete(discordId);
  }
}
