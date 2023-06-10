import { SpanStatusCode, trace } from '@opentelemetry/api';
import { Events } from '@sapphire/framework';

import { Listener } from '@lib/sapphire';

export class ErrorListener extends Listener<typeof Events.Error> {
  public override run(error: Error) {
    const span = trace.getActiveSpan();
    if (span) {
      span.setStatus({ code: SpanStatusCode.ERROR });
      span.recordException(error);
    }

    this.container.logger.error('an unexpected error occurred', { error });
  }
}
