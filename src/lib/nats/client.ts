import { EventEmitter } from 'node:events';

import { JsMsg, NatsConnection, NatsError, connect, consumerOpts, createInbox } from 'nats';

import { NATS_URL } from '@lib/config';
import logger, { Logger } from '@lib/logger';
import { VERSION } from '@lib/version';

export default class NATS extends EventEmitter {
  private server: NatsConnection | null = null;
  private topics: Set<string> = new Set();

  private logger: Logger = logger.child('nats');

  private async connect(): Promise<NatsConnection> {
    return await connect({
      name: `wafflebot/${VERSION}`,
      reconnect: true,
      servers: NATS_URL,
    });
  }

  public override on(eventName: string | symbol, listener: (...args: any[]) => void): this {
    // intentionally ignoring promise
    this.listen(eventName.toString());

    return super.on(eventName, listener);
  }

  public override once(eventName: string | symbol, listener: (...args: any[]) => void): this {
    // intentionally ignoring promise
    this.listen(eventName.toString());

    return super.once(eventName, listener);
  }

  private async listen(topic: string) {
    if (this.server === null) this.server = await this.connect();

    // already registered, nothing to do
    if (this.topics.has(topic)) return;

    try {
      const jetStream = this.server.jetstream();
      await jetStream.subscribe(
        topic,
        consumerOpts()
          .durable(topic.replaceAll('.', '-'))
          .queue(topic.replaceAll('.', '-'))
          .manualAck()
          .ackExplicit()
          .deliverTo(createInbox('wafflebot-'))
          .callback(this.consumerCallback.bind(this)),
      );

      this.topics.add(topic);
    } catch (error) {
      console.log(error);
      this.logger.error('failed to register listener', { event: topic, error });
    }
  }

  private async consumerCallback(err: NatsError | null, msg: JsMsg | null) {
    if (err !== null) {
      this.logger.error('error while receiving message', { error: err });
      return;
    } else if (msg === null) return;

    try {
      // TODO: extract trace parent and add to span context

      const data = await msg.json();
      this.emit(msg.subject, data);
    } catch (e) {
      this.logger.error('failed to deserialize message', { error: e });
    } finally {
      await msg.ack();
    }
  }
}
