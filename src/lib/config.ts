import 'dotenv/config';

import logger from '@lib/logger';

function load(name: string, defaultValue?: string): string {
  const value = process.env[name];
  if (value !== undefined) return value;

  if (defaultValue === undefined) {
    logger.error(`missing environment variable ${name}`);
    process.exit(1);
  } else return defaultValue;
}

export const TOKEN = load('DISCORD_TOKEN');
