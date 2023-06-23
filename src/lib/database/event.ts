import { prisma } from './client';

interface DatabaseEvent {
  id: number;
  discord_id: string;
}

export class Event {
  /**
   * Get a list of all the mapped discord events
   */
  public static async list(): Promise<DatabaseEvent[]> {
    return prisma.event.findMany();
  }

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
   * @param id the application portal ID
   */
  public static async delete(id: number) {
    await prisma.event.delete({ where: { id } });
  }
}
