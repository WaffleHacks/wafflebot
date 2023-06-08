import { Events, Listener } from '@sapphire/framework';

export class ErrorListener extends Listener<typeof Events.Error> {
  public override run(error: Error) {
    this.container.logger.error('an unexpected error occurred', { error });
  }
}
