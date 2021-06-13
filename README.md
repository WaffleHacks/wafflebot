# WaffleBot

A general purpose Discord bot for the WaffleHacks hackathon.


## Development

The backend and bot are built in Python using [FastAPI](https://fastapi.tiangolo.com/) and [discord.py](https://discordpy.readthedocs.io/).
The frontend is built in Node.js using [Svelte 3](https://svelte.dev).

### Bot

1. Install Python 3 and [Poetry](https://python-poetry.org)
2. Install the dependencies
```shell
$ poetry install
```
3. Get a Discord bot token following [this guide](https://discordpy.readthedocs.io/en/stable/discord.html) and invite the bot to a server for testing.
4. Run the database migrations
```shell
$ python3 manage.py migrations run
```
5. Start the bot
```shell
$ python3 manage.py run bot
```

### Backend

1. Install Python 3 and [Poetry](https://python-poetry.org)
2. Install the dependencies
```shell
$ poetry install
```
3. Get Discord OAuth credentials from the OAuth2 section in the [Discord Developer Portal](https://discord.com/developers/applications).
4. Run the database migrations
```shell
$ python3 manage.py migrations run
```
5. Start the server
```shell
$ python3 manage.py run backend
```

### Frontend

1. Install the latest LTS release of Node.js with [nvm](https://github.com/nvm-sh/nvm) or from the [official releases](https://nodejs.org/en/).
2. Install the dependencies
```shell
$ cd frontend
$ yarn install
```
3. Start the development server
```shell
$ python3 manage.py run frontend
```
