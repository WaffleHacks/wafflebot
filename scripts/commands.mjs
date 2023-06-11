import { Command, Option } from 'commander';
import { REST } from 'discord.js';
import 'dotenv/config';

const program = new Command();
program.name('commands').description('Manage the commands registered for the bot');
program
  .configureHelp({ showGlobalOptions: true })
  .addOption(new Option('-t, --token <token>', 'Discord bot token').env('DISCORD_TOKEN').makeOptionMandatory(true))
  .addOption(
    new Option('-a, --application <id>', 'application ID of the bot')
      .env('DISCORD_APPLICATION_ID')
      .makeOptionMandatory(true),
  )
  .addOption(new Option('-g, --guild <id>', 'guild ID to restrict to').env('DISCORD_GUILD_ID'));

program
  .command('remove')
  .argument('[name]', 'command name to remove')
  .description('delete one or more commands')
  .action(remove);

program.command('list').description('list the registered commands').action(list);

program.parse();

async function list(_, cmd) {
  const options = cmd.optsWithGlobals();

  const path = basePath(options);
  const rest = createRest(options);

  try {
    const commands = await rest.get(path);

    for (const command of commands) {
      console.log(`${command.name} (${commandType(command.type)})`);
      if (command.description) console.log(`  ${command.description}`);
      if (command.options && command.options.length > 0) {
        console.log('  Options:');
        for (const option of command.options)
          console.log(`    ${option.name} (${optionType(option.type)}) - ${option.description}`);
      }
    }
  } catch (error) {
    console.error(error);
  }
}

async function remove(name, _, cmd) {
  const options = cmd.optsWithGlobals();

  const path = basePath(options);
  const rest = createRest(options);

  try {
    const commands = await rest.get(path);

    const toDelete = commands.filter((c) => name === undefined || c.name === name);
    console.log(`Deleting ${toDelete.length} commands...`);

    await Promise.allSettled(
      toDelete.map(async (c) => {
        console.log(`  - ${c.name}`);
        await rest.delete(`${path}/${c.id}`);
      }),
    );

    console.log('Done!');
  } catch (error) {
    console.log(error);
  }
}

function createRest(options) {
  return new REST({ version: '10' }).setToken(options.token);
}

function basePath(options) {
  if (options.guild !== undefined && options.guild.length > 1) {
    console.log(`Using commands for guild ${options.guild}`);
    return `/applications/${options.application}/guilds/${options.guild}/commands`;
  } else {
    console.log(`Using commands for all guilds`);
    return `/applications/${options.application}/commands`;
  }
}

function commandType(type) {
  switch (type) {
    case 1:
      return 'chat input';
    case 2:
      return 'user context menu';
    case 3:
      return 'message context menu';
  }
}

function optionType(type) {
  switch (type) {
    case 1:
      return 'subcommand';
    case 2:
      return 'subcommand group';
    case 3:
      return 'string';
    case 4:
      return 'integer';
    case 5:
      return 'boolean';
    case 6:
      return 'user';
    case 7:
      return 'channel';
    case 8:
      return 'role';
    case 9:
      return 'mentionable';
    case 10:
      return 'number';
    case 11:
      return 'attachment';
  }
}
