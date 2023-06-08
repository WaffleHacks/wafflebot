import { TOKEN } from '@lib/config';
import database from '@lib/database';

import client from './client';
import { startHealthcheckServer } from './healthcheck';

client.login(TOKEN).finally(() => database.$disconnect());
startHealthcheckServer();
