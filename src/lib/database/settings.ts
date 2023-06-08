import { prisma } from './client';

interface VerificationMessage {
  channelId: string;
  headerId: string;
  buttonId: string;
  footerId: string;
}

export class Settings {
  /**
   * Get the verification message information
   */
  public static async getVerificationMessage(): Promise<VerificationMessage | null> {
    const setting = await prisma.setting.findFirst({ where: { key: 'VERIFICATION_MESSAGE' } });
    if (setting === null) return null;

    return JSON.parse(setting.value);
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
  }

  /**
   * Get the ID of the participant role
   */
  public static async getParticipantRole(): Promise<string | null> {
    const setting = await prisma.setting.findFirst({ where: { key: 'PARTICIPANT_ROLE' } });
    if (setting === null) return null;

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
  }
}
