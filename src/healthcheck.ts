import { IncomingMessage, ServerResponse, createServer } from 'node:http';

import { HEALTHCHECK_ADDRESS, HEALTHCHECK_PORT } from '@lib/config';
import logger from '@lib/logger';
import { VERSION } from '@lib/version';

function handler(req: IncomingMessage, res: ServerResponse) {
  if (req.url === '/health') {
    res.writeHead(200);
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
