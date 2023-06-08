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

export const APPLICATION_PORTAL_URL = load('APPLICATION_PORTAL_BASE_URL');
export const APPLICATION_PORTAL_TOKEN = load('APPLICATION_PORTAL_TOKEN');

export const HEALTHCHECK_ADDRESS = load('HEALTHCHECK_ADDRESS', '0.0.0.0');
export const HEALTHCHECK_PORT = parseInt(load('HEALTHCHECK_PORT', '8888'));
