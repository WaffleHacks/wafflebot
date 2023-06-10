import { Span, SpanStatusCode, trace } from '@opentelemetry/api';

export const tracer = trace.getTracer('wafflebot');

export const withSyncSpan = <F extends (span: Span) => T, T>(name: string, fn: F): T =>
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

export const withSpan = async <F extends (span: Span) => Promise<unknown>>(
  name: string,
  fn: F,
): Promise<ReturnType<F>> =>
  await tracer.startActiveSpan(name, async (span) => {
    try {
      const result = await fn(span);
      return result as ReturnType<F>;
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
