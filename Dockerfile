FROM node:18-alpine

RUN apk add --no-cache dumb-init

RUN adduser --disabled-password app
USER app

WORKDIR /wafflebot

COPY --chown=app package.json ./
COPY --chown=app yarn.lock ./
COPY --chown=app tsconfig.json ./

RUN yarn install

COPY --chown=app prisma prisma
COPY --chown=app src src
COPY --chown=app tsup.config.ts ./

# Add commit info
ARG COMMIT_SHA=dev
RUN echo "export const VERSION = '$COMMIT_SHA';" > src/lib/version.ts

RUN yarn prisma generate
RUN yarn build

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["yarn", "start"]
