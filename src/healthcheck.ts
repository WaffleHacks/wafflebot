import { IncomingMessage, ServerResponse, createServer } from 'node:http';

import { HEALTHCHECK_ADDRESS, HEALTHCHECK_PORT } from '@lib/config';
import prisma from '@lib/database';
import logger from '@lib/logger';
import { VERSION } from '@lib/version';

import client from './client';

async function handler(req: IncomingMessage, res: ServerResponse) {
  if (req.url === '/health') {
    await prisma.$executeRaw`SELECT 1`;

    if (client.isReady()) res.writeHead(200);
    else res.writeHead(500);

    res.write(`version: ${VERSION}`);
  } else res.writeHead(404);

  res.end();
}

const server = createServer(handler);

/**
 * Start the healthcheck server
 */
export const startHealthcheckServer = () =>
  server.listen(HEALTHCHECK_PORT, HEALTHCHECK_ADDRESS, () =>
    logger.child('http').info('healthcheck server up and ready to handle requests', {
      host: HEALTHCHECK_ADDRESS,
      port: HEALTHCHECK_PORT,
    }),
  );
