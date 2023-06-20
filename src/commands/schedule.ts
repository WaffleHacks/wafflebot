import { CommandOptionsRunTypeEnum } from '@sapphire/framework';
import { getUnixTime, parseISO } from 'date-fns';

import { GUILD_ID } from '@lib/config';
import { Event } from '@lib/database';
import embeds from '@lib/embeds';
import { EventDetails, listEvents } from '@lib/portal';
import { Command } from '@lib/sapphire';
import { withSpan } from '@lib/tracing';

// Cache for an hour
const CACHE_DURATION = 60 * 60;

export class ScheduleCommand extends Command {
  // Allow caching event list for an hour
  private events = '';
  private lastFetched = 0;

  public constructor(context: Command.Context, options: Command.Options) {
    super(context, {
      ...options,
      description: 'Get the schedule for the hackathon',
      runIn: CommandOptionsRunTypeEnum.GuildText,
    });
  }

  public override registerApplicationCommands(registry: Command.Registry) {
    registry.registerChatInputCommand((builder) =>
      builder.setName(this.name).setDescription(this.description).setDMPermission(false),
    );
  }

  public override async chatInputRun(interaction: Command.ChatInputCommandInteraction) {
    await withSpan('reply.defer', () => interaction.deferReply());

    const events = await withSpan('fetch-events', async () => await this.fetchEvents());
    await withSpan('reply.edit', () => interaction.editReply({ embeds: [embeds.card('Events', events)] }));
  }

  private async fetchEvents(): Promise<string> {
    if (Date.now() < this.lastFetched + CACHE_DURATION) return this.events;

    const events = await listEvents();
    const formatted = await Promise.all(
      events.map((event) =>
        withSpan('format', (span) => {
          span.setAttribute('event.id', event.id);
          return this.formatEvent(event);
        }),
      ),
    );
    this.events = formatted.join('\n');

    this.lastFetched = Date.now();

    return this.events;
  }

  private async formatEvent(event: EventDetails): Promise<string> {
    const start = parseISO(event.start);
    const timestamp = getUnixTime(start);

    const discordId = await Event.find(event.id);
    if (discordId) return `<t:${timestamp}:f> - [${event.name}](https://discord.com/events/${GUILD_ID}/${discordId})`;
    else return `<t:${timestamp}:f> - ${event.name}`;
  }
}
