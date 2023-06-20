import { GuildScheduledEventEntityType, GuildScheduledEventPrivacyLevel } from 'discord-api-types/v10';
import { Client } from 'discord.js';

import { GUILD_ID } from '@lib/config';
import { Event } from '@lib/database';
import { EventDetails } from '@lib/portal';

/**
 * Create a new scheduled event
 * @param client the discord client
 * @param details the event details
 */
export async function create(client: Client, details: EventDetails) {
  const guild = await client.guilds.fetch(GUILD_ID);
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

/**
 * Update a scheduled event
 * @param client the discord client
 * @param details the changed event details
 * @param scheduledEventId the scheduled event id
 */
export async function update(client: Client, details: EventDetails, scheduledEventId: string) {
  const guild = await client.guilds.fetch(GUILD_ID);

  const eventOptions = {
    name: details.name,
    scheduledStartTime: details.start,
    scheduledEndTime: details.end,
    privacyLevel: GuildScheduledEventPrivacyLevel.GuildOnly,
    entityType: GuildScheduledEventEntityType.External,
    entityMetadata: {
      location: details.url,
    },
  };

  try {
    await guild.scheduledEvents.edit(scheduledEventId, eventOptions);
  } catch {
    const created = await guild.scheduledEvents.create(eventOptions);
    await Event.create(details.id, created.id);
  }
}

/**
 * Delete a scheduled event
 * @param client the discord client
 * @param scheduledEventId the scheduled event id
 */
export async function remove(client: Client, scheduledEventId: string) {
  try {
    const guild = await client.guilds.fetch(GUILD_ID);
    await guild.scheduledEvents.delete(scheduledEventId);
  } catch {}

  // Delete the mapping no matter what happens with Discord
  await Event.delete(scheduledEventId);
}
