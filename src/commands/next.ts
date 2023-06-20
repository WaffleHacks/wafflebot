import { CommandOptionsRunTypeEnum } from '@sapphire/framework';
import { formatDistance, getUnixTime, millisecondsToSeconds, parseISO } from 'date-fns';
import { EmbedBuilder } from 'discord.js';

import { GUILD_ID } from '@lib/config';
import { Event } from '@lib/database';
import embeds from '@lib/embeds';
import { EventDetails, listEvents } from '@lib/portal';
import { Command } from '@lib/sapphire';
import { withSpan, withSyncSpan } from '@lib/tracing';

// Cache for an hour
const CACHE_DURATION = 60 * 60;

export class NextCommand extends Command {
  // Allow caching event list for an hour
  private events: EventDetails[] = [];
  private lastFetched = 0;

  public constructor(context: Command.Context, options: Command.Options) {
    super(context, {
      ...options,
      description: 'Get details about the next event',
      runIn: CommandOptionsRunTypeEnum.GuildText,
    });
  }

  public override registerApplicationCommands(registry: Command.Registry) {
    registry.registerChatInputCommand((builder) =>
      builder //
        .setName(this.name)
        .setDescription(this.description),
    );
  }

  public override async chatInputRun(interaction: Command.ChatInputCommandInteraction) {
    await withSpan('reply.defer', () => interaction.deferReply());

    const events = await withSpan('fetch-events', () => this.fetchEvents());

    const next: EventDetails | undefined = withSyncSpan('find-next', () => {
      const now = millisecondsToSeconds(Date.now());
      return events.find((e) => getUnixTime(parseISO(e.start)) > now);
    });

    let embed: EmbedBuilder;
    if (next) {
      embed = embeds.card(next.name, next.description || undefined);

      const discordId = await Event.find(next.id);
      if (discordId) embed.setURL(`https://discord.com/events/${GUILD_ID}/${discordId}`);

      const start = parseISO(next.start);
      const end = parseISO(next.end);

      embed.addFields(
        { name: 'Starts', value: `<t:${getUnixTime(start)}:R>`, inline: true },
        { name: 'Duration', value: formatDistance(end, start), inline: true },
      );
    } else {
      embed = embeds.card(
        'WaffleHacks has ended!',
        'Unfortunately there are no more workshops or panels. We look forward to seeing you again next year!',
      );
    }

    await withSpan('reply.edit', () => interaction.editReply({ embeds: [embed] }));
  }

  private async fetchEvents(): Promise<EventDetails[]> {
    if (Date.now() < this.lastFetched + CACHE_DURATION) return this.events;

    this.events = await listEvents();
    this.lastFetched = Date.now();

    return this.events;
  }
}
