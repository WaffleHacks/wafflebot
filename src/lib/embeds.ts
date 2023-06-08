import { EmbedBuilder } from 'discord.js';

/**
 * The base embed format
 */
function base(): EmbedBuilder {
  return new EmbedBuilder().setColor('#D08132');
}

/**
 * Display a card to the user
 * @param title the card header
 * @param description the optional card body
 */
function card(title: string, description?: string): EmbedBuilder {
  const embed = base().setTitle(title);

  if (description) return embed.setDescription(description);
  else return embed;
}

/**
 * Display an error to the user
 * @param reason the error message
 */
function error(reason: string): EmbedBuilder {
  return card(':x: Error', reason);
}

/**
 * Display a message to the user
 * @param content the message content
 */
function message(content: string): EmbedBuilder {
  return base().setDescription(content);
}

export default { base, card, error, message };
