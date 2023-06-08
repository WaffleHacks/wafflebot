import { prisma } from './client';

export class Link {
  /**
   * Create a new Discord-application link
   * @param discordId a Discord ID
   * @param participantId the participant's ID
   */
  public static async create(discordId: string, participantId: number) {
    await prisma.link.create({
      data: {
        discord_id: discordId,
        participant_id: participantId,
      },
    });
  }

  /**
   * Find a participant's Discord ID by their application portal ID
   * @param id the application portal ID to search for
   */
  public static async findDiscordId(id: number): Promise<string | null> {
    const link = await prisma.link.findFirst({ where: { participant_id: id } });
    if (link === null) return null;

    return link.discord_id;
  }

  /**
   * Find a participant's ID by their Discord ID
   * @param id the Discord ID to search for
   */
  public static async findParticipantId(id: string): Promise<number | null> {
    const link = await prisma.link.findFirst({ where: { discord_id: id } });
    if (link === null) return null;

    return link.participant_id;
  }
}
