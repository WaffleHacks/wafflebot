import { Attributes, Span, trace } from '@opentelemetry/api';
import { APIUser, ChannelType, InteractionType } from 'discord-api-types/v10';
import { Channel, Guild, GuildChannel, ThreadChannel, User } from 'discord.js';

export const tracer = trace.getTracer('@sapphire/framework');

export function setUserAttributes(span: Span, user: User | APIUser) {
  span.setAttributes({
    'user.id': user.id,
    'user.name': user.discriminator === '0' ? user.username : `${user.username}#${user.discriminator}`,
    'user.bot': user.bot,
  });
}

export function setGuildAttributes(span: Span, guild: Guild | null) {
  if (guild) {
    span.setAttributes({
      'guild.id': guild.id,
      'guild.name': guild.name,
      'guild.locale': guild.preferredLocale,
    });
  }
}

export function setChannelAttributes(span: Span, channel: Channel | null) {
  if (channel === null) return;

  const attributes: Attributes = {
    'channel.id': channel.id,
    'channel.type': formatChannelType(channel.type),
  };

  if (channel instanceof GuildChannel) attributes['channel.name'] = channel.name;
  else if (channel instanceof ThreadChannel) {
    attributes['channel.name'] = channel.name;

    if (channel.parent) {
      attributes['channel.parent.id'] = channel.parent.id;
      attributes['channel.parent.name'] = channel.parent.name;
      attributes['channel.parent.type'] = formatChannelType(channel.parent.type);
    }
  }

  span.setAttributes(attributes);
}

export function formatChannelType(type: ChannelType): string {
  switch (type) {
    case ChannelType.GuildText:
      return 'guild.text';
    case ChannelType.DM:
      return 'dm';
    case ChannelType.GuildVoice:
      return 'guild.voice';
    case ChannelType.GroupDM:
      return 'dm.group';
    case ChannelType.GuildCategory:
      return 'guild.category';
    case ChannelType.GuildAnnouncement:
      return 'guild.announcement';
    case ChannelType.AnnouncementThread:
      return 'guild.announcement.thread';
    case ChannelType.GuildPublicThread:
    case ChannelType.PublicThread:
      return 'guild.thread.public';
    case ChannelType.GuildPrivateThread:
    case ChannelType.PrivateThread:
      return 'guild.thread.private';
    case ChannelType.GuildStageVoice:
      return 'guild.stage';
    case ChannelType.GuildDirectory:
      return 'guild.directory';
    case ChannelType.GuildForum:
      return 'guild.forum';
    case ChannelType.GuildNews:
      return 'guild.news';
    case ChannelType.GuildNewsThread:
      return 'guild.thread.news';
  }
}

export function formatInteractionType(type: InteractionType): string {
  switch (type) {
    case InteractionType.Ping:
      return 'ping';
    case InteractionType.ApplicationCommand:
      return 'command';
    case InteractionType.MessageComponent:
      return 'message-component';
    case InteractionType.ApplicationCommandAutocomplete:
      return 'command.autocomplete';
    case InteractionType.ModalSubmit:
      return 'modal-submit';
  }
}
