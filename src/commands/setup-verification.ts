import { Command } from '@sapphire/framework';
import { ButtonStyle, ChannelType } from 'discord-api-types/v10';
import { ActionRowBuilder, ButtonBuilder, Client, TextChannel, channelMention } from 'discord.js';

import { Settings } from '@lib/database';

const UPPER_MESSAGE = `
**Welcome to \u200b :waffle: \u200b WaffleHacks 2023!**
═══════════════════════

You don't yet have full access to all our channels. Just follow these short steps to get verified:

:one: - Agree to our {RULES_CHANNEL}. You should be prompted to do this before sending or reacting to messages on this server.

:two: - Get your application accepted at https://apply.wafflehacks.org

:three: - Click the button below to get verified.

\u200b
`;

const LOWER_MESSAGE = `\u200b
\u200b
:asterisk: - If you're here as a sponsor, judge, or mentor, you'll need to DM one of our directors.

Thanks for joining and happy hacking!!
`;

export class SetupVerificationCommand extends Command {
  public constructor(context: Command.Context, options: Command.Options) {
    super(context, {
      ...options,
      description: 'Setup participant verification in the specified channel',
    });
  }

  public override registerApplicationCommands(registry: Command.Registry) {
    registry.registerChatInputCommand((builder) =>
      builder
        .setName(this.name)
        .setDescription(this.description)
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

    await this.purgeOldChannel(interaction.client);

    await channel.send({
      content: UPPER_MESSAGE.replace('{RULES_CHANNEL}', channelMention(rulesChannel.id)),
      flags: 'SuppressEmbeds',
    });

    const button = new ButtonBuilder()
      .setCustomId('verify')
      .setEmoji('✅')
      .setLabel('Get verified!')
      .setStyle(ButtonStyle.Success);
    const row = new ActionRowBuilder<ButtonBuilder>().addComponents(button);
    await channel.send({ components: [row] });

    await channel.send({ content: LOWER_MESSAGE });

    await Settings.setVerificationChannel(channel.id);

    return interaction.reply({
      content: `Successfully setup the verification channel in ${channelMention(channel.id)}`,
      ephemeral: true,
    });
  }

  private async purgeOldChannel(client: Client): Promise<void> {
    const id = await Settings.getVerificationChannel();
    if (id === null) return;

    const channel = await client.channels.fetch(id);
    if (channel === null || !(channel instanceof TextChannel)) return;

    // We only send 3 messages, so we only need to delete 3
    const last = await channel.messages.fetch({ limit: 3 });
    await channel.bulkDelete(last);
  }
}
