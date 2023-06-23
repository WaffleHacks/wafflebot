import { getUnixTime, minutesToMilliseconds, parseISO } from 'date-fns';
import { TextChannel } from 'discord.js';

import { ANNOUNCEMENTS_CHANNEL_ID, GUILD_ID } from '@lib/config';
import { Event } from '@lib/database';
import { EventDetails, listEvents } from '@lib/portal';

import client from '../client';

const STARTING_OFFSET = minutesToMilliseconds(1);

class Notifier {
  // Mapping of event ID to timeout ID
  private readonly timeouts: Map<number, NodeJS.Timeout> = new Map();

  /**
   * Seed and start the notifier
   */
  public async start() {
    const events = await listEvents();

    for (const event of events) this.upsert(event);
  }

  /**
   * Create/update an event notification
   * @param details the event's details
   */
  public upsert(details: EventDetails) {
    clearTimeout(this.timeouts.get(details.id));

    const start = getUnixTime(parseISO(details.start)) * 1000;
    const now = Date.now();

    const jitter = Math.floor(Math.random() * 30 * 1000);
    const msUntilStarting = start - now - STARTING_OFFSET + jitter;
    if (msUntilStarting <= 0) return;

    const timeout = setTimeout(this.generateNotifier(details), msUntilStarting);
    this.timeouts.set(details.id, timeout);
  }

  /**
   * Remove an event notification
   * @param id the event's ID
   */
  public remove(id: number) {
    clearTimeout(this.timeouts.get(id));
    this.timeouts.delete(id);
  }

  private generateNotifier(details: EventDetails): () => void {
    return async () => {
      const guild = await client.guilds.fetch(GUILD_ID);
      const channel = await guild.channels.fetch(ANNOUNCEMENTS_CHANNEL_ID);
      if (channel === null || !(channel instanceof TextChannel)) return;

      let content = `@everyone Join us for **${details.name}** now!\n${details.url}`;

      const event = await Event.find(details.id);
      if (event !== null) content += `\n\nhttps://discord.com/events/${GUILD_ID}/${event}`;

      await channel.send({
        content,
        allowedMentions: { parse: ['everyone'] },
      });
    };
  }
}

const notifier = new Notifier();

export default notifier;
