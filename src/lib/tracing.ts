import { Span, SpanStatusCode, trace } from '@opentelemetry/api';

export const tracer = trace.getTracer('wafflebot');

export const inSpan = <F extends (span: Span) => T, T>(name: string, fn: F): T =>
  tracer.startActiveSpan(name, (span) => {
    try {
      return fn(span);
    } catch (e) {
      if (e instanceof Error) {
        span.setStatus({ code: SpanStatusCode.ERROR });
        span.recordException(e);
      }

      throw e;
    } finally {
      span.end();
    }
  });
