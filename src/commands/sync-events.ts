import { CommandOptionsRunTypeEnum } from '@sapphire/framework';

import { Event } from '@lib/database';
import embeds from '@lib/embeds';
import { findEvent, listEvents } from '@lib/portal';
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
        .setDescription(this.description)
        .addBooleanOption((option) =>
          option
            .setName('all')
            .setDescription('Whether to sync all the events at once (ONLY USE AS A LAST RESORT)')
            .setRequired(false),
        )
        .addStringOption((option) =>
          option.setName('code').setDescription("The event's code to sync").setRequired(false),
        ),
    );
  }

  public override async chatInputRun(interaction: Command.ChatInputCommandInteraction) {
    const syncAll = interaction.options.getBoolean('all', false);
    const eventCode = interaction.options.getString('code', false);

    if (syncAll === null && eventCode === null) {
      return await withSpan('reply', () =>
        interaction.reply({ embeds: [embeds.message('One of `all` or `code` must be provided')], ephemeral: true }),
      );
    }

    await withSpan('reply.defer', () => interaction.deferReply({ ephemeral: true }));

    if (eventCode) await this.syncIndividual(eventCode);
    else if (syncAll) await this.syncAll();

    await withSpan('reply.edit', () =>
      interaction.editReply({ embeds: [embeds.message('Successfully synced event(s) from application portal')] }),
    );
  }

  private async syncIndividual(code: string) {
    const event = await findEvent(code, 'code');
    if (event === null) return;

    const discordId = await withSpan('event.mapping', () => Event.find(event.id));

    const client = this.container.client;
    if (discordId) await scheduledEvents.update(client, event, discordId);
    else await scheduledEvents.create(client, event);
  }

  private async syncAll() {
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
  }

  private async fetchEventMapping(): Promise<Record<string, string>> {
    const events = await Event.list();
    const entries = events.map((e) => [e.id.toString(), e.discord_id]);
    return Object.fromEntries(entries);
  }
}
