import { Command, Option } from 'commander';
import { REST } from 'discord.js';
import 'dotenv/config';

const program = new Command();
program.name('clear-commands').description('Clear the commands registered for the bot');
program
  .addOption(new Option('-t, --token <token>', 'Discord bot token').env('DISCORD_TOKEN').makeOptionMandatory(true))
  .addOption(
    new Option('-a, --application <id>', 'application ID of the bot')
      .env('DISCORD_APPLICATION_ID')
      .makeOptionMandatory(true),
  )
  .addOption(new Option('-g, --guild <id>', 'guild ID to restrict to').env('DISCORD_GUILD_ID'))
  .addOption(new Option('-c, --command <name>', 'command name to delete'));

program.parse();
const options = program.opts();

let basePath;
if (options.guild !== undefined && options.guild.length > 1) {
  console.log(`Removing commands for guild ${options.guild}`);
  basePath = `/applications/${options.application}/guilds/${options.guild}/commands`;
} else {
  console.log(`Removing commands for all guilds`);
  basePath = `/applications/${options.application}/commands`;
}

(async () => {
  try {
    const rest = new REST({ version: '10' }).setToken(options.token);
    const commands = await rest.get(basePath);

    const toDelete = commands.filter((c) => options.command === undefined || c.name === options.command);
    console.log(`Deleting ${toDelete.length} commands... This could take a while.`);

    const tasks = toDelete.map((c) => rest.delete(`${basePath}/${c.id}`));
    await Promise.all(tasks);

    console.log('Done!');
  } catch (error) {
    console.log(error);
  }
})();
