import { prisma } from './client';

export class Settings {
  /**
   * Get the verification channel ID
   */
  public static async getVerificationChannel(): Promise<string | null> {
    const setting = await prisma.setting.findFirst({ where: { key: 'VERIFICATION_CHANNEL' } });
    if (setting === null) return null;

    return setting.value;
  }

  /**
   * Store the verification channel ID
   * @param id the channel's ID
   */
  public static async setVerificationChannel(id: string): Promise<void> {
    await prisma.setting.upsert({
      create: { key: 'VERIFICATION_CHANNEL', value: id },
      update: { value: id },
      where: { key: 'VERIFICATION_CHANNEL' },
    });
  }
}
