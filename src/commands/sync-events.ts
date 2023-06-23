import { CommandOptionsRunTypeEnum } from '@sapphire/framework';

import { Event } from '@lib/database';
import embeds from '@lib/embeds';
import { listEvents } from '@lib/portal';
import { Command } from '@lib/sapphire';
import * as scheduledEvents from '@lib/scheduled-events';
import { withSpan } from '@lib/tracing';

export class SyncEventsCommand extends Command {
  public constructor(context: Command.Context, options: Command.Options) {
    super(context, {
      ...options,
      description: 'Sync the events in the application portal with the Discord events',
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
    await withSpan('reply.defer', () => interaction.deferReply({ ephemeral: true }));

    const eventMappings = await withSpan('event-mappings', () => this.fetchEventMapping());
    const events = await listEvents();

    const client = this.container.client;

    for (const event of events) {
      const discordId = eventMappings[event.id.toString()];

      if (discordId) await scheduledEvents.update(client, event, discordId);
      else await scheduledEvents.create(client, event);

      delete eventMappings[event.id.toString()];
    }

    for (const [eventId, scheduledEventId] of Object.entries(eventMappings))
      await scheduledEvents.remove(client, parseInt(eventId), scheduledEventId);

    await withSpan('reply.edit', () =>
      interaction.editReply({ embeds: [embeds.message('Successfully synced events from application portal')] }),
    );
  }

  private async fetchEventMapping(): Promise<Record<string, string>> {
    const events = await Event.list();
    const entries = events.map((e) => [e.id.toString(), e.discord_id]);
    return Object.fromEntries(entries);
  }
}
