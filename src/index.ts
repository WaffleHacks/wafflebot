import { LogLevel, SapphireClient } from '@sapphire/framework';
import { GatewayIntentBits } from 'discord.js';

import CONFIG from '@lib/config';
import logger from '@lib/logger';

const client = new SapphireClient({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages],
  logger: {
    level: process.env.NODE_ENV === 'development' ? LogLevel.Debug : LogLevel.Info,
    instance: logger.child('discord'),
  },
  typing: true,
});

client.login(CONFIG.token);
