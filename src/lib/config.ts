import 'dotenv/config';

function load(name: string, defaultValue?: string): string {
  const value = process.env[name];
  if (value !== undefined) return value;

  if (defaultValue === undefined) {
    console.log(`ERROR: missing environment variable ${name}`);
    process.exit(1);
  } else return defaultValue;
}

export const TOKEN = load('DISCORD_TOKEN');

export const APPLICATION_PORTAL_URL = load('APPLICATION_PORTAL_BASE_URL');
export const APPLICATION_PORTAL_TOKEN = load('APPLICATION_PORTAL_TOKEN');

export const NATS_URL = load('NATS_URL');

export const HEALTHCHECK_ADDRESS = process.env.HEALTHCHECK_ADDRESS;
export const HEALTHCHECK_PORT = parseInt(load('HEALTHCHECK_PORT', '8888'));

export const OTEL_ENABLE = ['yes', 'y', 'true', 't', '1'].includes(load('OTEL_ENABLE', 'yes').toLowerCase());
export const OTEL_SERVICE_NAME = load('OTEL_SERVICE_NAME', 'wafflebot');
export const OTEL_EXPORTER_OTLP_ENDPOINT = load('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://127.0.0.1:9217');
