import NodeCache from 'node-cache';

import { prisma } from './client';

interface VerificationMessage {
  channelId: string;
  headerId: string;
  buttonId: string;
  footerId: string;
}

// Cache settings for 6 hours by default
const cache = new NodeCache({ stdTTL: 6 * 60 * 60 });

export class Settings {
  /**
   * Get the verification message information
   */
  public static async getVerificationMessage(): Promise<VerificationMessage | null> {
    const cached = cache.get<VerificationMessage>('verification-message');
    if (cached) return cached;

    const setting = await prisma.setting.findFirst({ where: { key: 'VERIFICATION_MESSAGE' } });
    if (setting === null) return null;

    const deserialized = JSON.parse(setting.value);
    cache.set('verification-message', deserialized);
    return deserialized;
  }

  /**
   * Set the verification message information
   * @param message the message and channel IDs
   */
  public static async setVerificationMessage(message: VerificationMessage): Promise<void> {
    const serialized = JSON.stringify(message);
    await prisma.setting.upsert({
      create: { key: 'VERIFICATION_MESSAGE', value: serialized },
      update: { value: serialized },
      where: { key: 'VERIFICATION_MESSAGE' },
    });
    cache.set('verification-message', message);
  }

  /**
   * Get the ID of the participant role
   */
  public static async getParticipantRole(): Promise<string | null> {
    const cached = cache.get<string>('participant-role');
    if (cached) return cached;

    const setting = await prisma.setting.findFirst({ where: { key: 'PARTICIPANT_ROLE' } });
    if (setting === null) return null;

    cache.set('participant-role', setting.value);
    return setting.value;
  }

  /**
   * Store the participant role ID
   * @param id the role's ID
   */
  public static async setParticipantRole(id: string): Promise<void> {
    await prisma.setting.upsert({
      create: { key: 'PARTICIPANT_ROLE', value: id },
      update: { value: id },
      where: { key: 'PARTICIPANT_ROLE' },
    });
    cache.set('participant-role', id);
  }
}
