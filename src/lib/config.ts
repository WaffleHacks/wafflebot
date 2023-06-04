import 'dotenv/config';

import logger from '@lib/logger';

class Config {
  readonly token: string;

  constructor() {
    this.token = Config.load('DISCORD_TOKEN');
  }

  private static load(name: string, defaultValue?: string): string {
    const value = process.env[name];
    if (value !== undefined) return value;

    if (defaultValue === undefined) {
      logger.error(`missing environment variable ${name}`);
      process.exit(1);
    } else return defaultValue;
  }
}

const CONFIG = new Config();

export default CONFIG;
