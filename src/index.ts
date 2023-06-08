import { LogLevel, SapphireClient } from '@sapphire/framework';
import { GatewayIntentBits } from 'discord.js';

import { TOKEN } from '@lib/config';
import database from '@lib/database';
import logger from '@lib/logger';

import { startHealthcheckServer } from './healthcheck';

const client = new SapphireClient({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages],
  logger: {
    level: process.env.NODE_ENV === 'development' ? LogLevel.Debug : LogLevel.Info,
    instance: logger.child('discord'),
  },
  typing: true,
});

client.login(TOKEN).finally(() => database.$disconnect());
startHealthcheckServer();
