import { ChannelCredentials, credentials } from '@grpc/grpc-js';
import { DiagConsoleLogger, DiagLogLevel, diag } from '@opentelemetry/api';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-grpc';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { WinstonInstrumentation } from '@opentelemetry/instrumentation-winston';
import {
  Resource,
  detectResourcesSync,
  envDetectorSync,
  hostDetectorSync,
  osDetectorSync,
  processDetectorSync,
} from '@opentelemetry/resources';
import { BatchSpanProcessor, NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { PrismaInstrumentation } from '@prisma/instrumentation';
import { NodeCacheInstrumentation } from 'opentelemetry-instrumentation-node-cache';

import { OTEL_ENABLE, OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME } from '@lib/config';
import { VERSION } from '@lib/version';

function credentialsForEndpoint(): ChannelCredentials {
  if (OTEL_EXPORTER_OTLP_ENDPOINT.startsWith('https://')) return credentials.createSsl();
  else return credentials.createInsecure();
}

if (OTEL_ENABLE) {
  diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.INFO);

  const exporter = new OTLPTraceExporter({
    url: OTEL_EXPORTER_OTLP_ENDPOINT,
    credentials: credentialsForEndpoint(),
  });
  const processor = new BatchSpanProcessor(exporter);

  const detectedResource = detectResourcesSync({
    detectors: [envDetectorSync, processDetectorSync, osDetectorSync, hostDetectorSync],
  });
  const resource = new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: OTEL_SERVICE_NAME,
    [SemanticResourceAttributes.SERVICE_VERSION]: VERSION,
  });

  const provider = new NodeTracerProvider({ resource: detectedResource.merge(resource) });
  provider.addSpanProcessor(processor);

  registerInstrumentations({
    tracerProvider: provider,
    instrumentations: [new NodeCacheInstrumentation(), new PrismaInstrumentation(), new WinstonInstrumentation()],
  });

  provider.register();

  process.on('SIGINT', () => provider.shutdown().catch(console.error));
  process.on('SIGTERM', () => provider.shutdown().catch(console.error));
}
