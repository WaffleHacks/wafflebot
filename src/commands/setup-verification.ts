import { trace } from '@opentelemetry/api';
import { CommandOptionsRunTypeEnum } from '@sapphire/framework';
import { ButtonStyle, ChannelType } from 'discord-api-types/v10';
import { ActionRowBuilder, ButtonBuilder, Client, TextChannel, channelMention } from 'discord.js';

import { Settings } from '@lib/database';
import embeds from '@lib/embeds';
import { Command } from '@lib/sapphire';
import { withSpan } from '@lib/tracing';

const HEADER_MESSAGE = `
**Welcome to \u200b :waffle: \u200b WaffleHacks 2023!**
═══════════════════════

You don't yet have full access to all our channels. Just follow these short steps to get verified:

:one: - Agree to our {RULES_CHANNEL}. You should be prompted to do this before sending or reacting to messages on this server.

:two: - Get your application accepted at https://apply.wafflehacks.org

:three: - Click the button below to get verified.

\u200b
`;

const FOOTER_MESSAGE = `\u200b
\u200b
:asterisk: - If you're here as a sponsor, judge, or mentor, you'll need to DM one of our directors.

Thanks for joining and happy hacking!!
`;

export class SetupVerificationCommand extends Command {
  public constructor(context: Command.Context, options: Command.Options) {
    super(context, {
      ...options,
      description: 'Setup participant verification in the specified channel',
      preconditions: ['ParticipantRoleIsSet'],
      runIn: CommandOptionsRunTypeEnum.GuildText,
    });
  }

  public override registerApplicationCommands(registry: Command.Registry) {
    registry.registerChatInputCommand((builder) =>
      builder
        .setName(this.name)
        .setDescription(this.description)
        .setDMPermission(false)
        .addChannelOption((option) =>
          option
            .setName('channel')
            .setDescription('Channel to setup verification in, defaults to current channel if omitted')
            .setRequired(true),
        )
        .addChannelOption((option) =>
          option.setName('rules').setDescription('Channel where the rules are displayed').setRequired(true),
        ),
    );
  }

  public override async chatInputRun(interaction: Command.ChatInputCommandInteraction) {
    const channel = interaction.options.getChannel('channel', true, [ChannelType.GuildText]);
    const rulesChannel = interaction.options.getChannel('rules', true, [ChannelType.GuildText]);

    const span = trace.getActiveSpan();
    span?.setAttributes({
      'channel.id': channel.id,
      'channel.name': channel.name,
      'rules.id': rulesChannel.id,
      'rules.name': rulesChannel.name,
    });

    await this.purgeOldChannel(interaction.client);

    const headerMessage = await withSpan('send.header', () =>
      channel.send({
        content: HEADER_MESSAGE.replace('{RULES_CHANNEL}', channelMention(rulesChannel.id)),
        flags: 'SuppressEmbeds',
      }),
    );

    const button = new ButtonBuilder()
      .setCustomId('verify')
      .setEmoji('✅')
      .setLabel('Get verified!')
      .setStyle(ButtonStyle.Success);
    const row = new ActionRowBuilder<ButtonBuilder>().addComponents(button);
    const buttonMessage = await withSpan('send.button', () => channel.send({ components: [row] }));

    const footerMessage = await withSpan('send.footer', () => channel.send({ content: FOOTER_MESSAGE }));

    await Settings.setVerificationMessage({
      channelId: channel.id,
      headerId: headerMessage.id,
      buttonId: buttonMessage.id,
      footerId: footerMessage.id,
    });

    return withSpan('reply', () =>
      interaction.reply({
        embeds: [embeds.message(`Successfully setup the verification channel in ${channelMention(channel.id)}`)],
        ephemeral: true,
      }),
    );
  }

  private async purgeOldChannel(client: Client): Promise<void> {
    await withSpan('purge-old-channels', async () => {
      const message = await Settings.getVerificationMessage();
      if (message === null) return;

      const { channelId, headerId, buttonId, footerId } = message;

      const channel = await withSpan('channel.fetch', () => client.channels.fetch(channelId));
      if (channel === null || !(channel instanceof TextChannel)) return;

      await withSpan('channel.bulkDelete', () => channel.bulkDelete([headerId, buttonId, footerId]));
    });
  }
}
