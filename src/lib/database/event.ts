import { prisma } from './client';

export class Event {
  /**
   * Find the Discord scheduled event ID by an event's application portal id
   * @param id the application portal ID
   */
  public static async find(id: number): Promise<string | null> {
    const event = await prisma.event.findFirst({ where: { id } });
    if (event === null) return null;

    return event.discord_id;
  }

  /**
   * Create a new event mapping from application portal event to Discord scheduled event
   * @param id the application portal ID
   * @param discordId the Discord scheduled event ID
   */
  public static async create(id: number, discordId: string) {
    await prisma.event.upsert({
      create: { id, discord_id: discordId },
      where: { id },
      update: { discord_id: discordId },
    });
  }

  /**
   * Delete an event mapping by an event's scheduled event ID
   * @param discordId the scheduled event ID
   */
  public static async delete(discordId: string) {
    await prisma.event.delete({ where: { discord_id: discordId } });
  }
}
