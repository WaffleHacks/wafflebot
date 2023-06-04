import { ILogger, LogLevel } from '@sapphire/framework';
import { Logger as WinstonLogger, createLogger, format, transports } from 'winston';

export class Logger implements ILogger {
  readonly logger: WinstonLogger;

  constructor(namespace?: string, parent?: WinstonLogger) {
    if (parent) {
      this.logger = parent.child({ namespace });
    } else {
      this.logger = createLogger({
        transports: [new transports.Console()],
        format: format.combine(
          format.timestamp(),
          format.errors({ stack: true }),
          process.env.NODE_ENV === 'production' ? format.json() : format.combine(format.colorize(), format.simple()),
        ),
        handleExceptions: true,
        handleRejections: true,
      });
    }
  }

  public child(namespace: string): Logger {
    return new Logger(namespace, this.logger);
  }

  has(level: LogLevel): boolean {
    return this.logger.isLevelEnabled(this.logLevelName(level));
  }

  trace(...values: readonly unknown[]): void {
    this.write(LogLevel.Trace, ...values);
  }

  debug(...values: readonly unknown[]): void {
    this.write(LogLevel.Debug, ...values);
  }

  info(...values: readonly unknown[]): void {
    this.write(LogLevel.Info, ...values);
  }

  warn(...values: readonly unknown[]): void {
    this.write(LogLevel.Warn, ...values);
  }

  error(...values: readonly unknown[]): void {
    this.write(LogLevel.Error, ...values);
  }

  fatal(...values: readonly unknown[]): void {
    this.write(LogLevel.Fatal, ...values);
  }

  write(level: LogLevel, ...values: readonly unknown[]): void {
    const levelName = this.logLevelName(level);

    if (values.length >= 1) {
      if (typeof values[0] === 'string') {
        const [message, ...meta] = values;
        this.logger.log(levelName, message, ...meta);
      } else {
        this.logger.log(levelName, values);
      }
    }
  }

  private logLevelName(level: LogLevel): string {
    switch (level) {
      case LogLevel.Trace:
        return 'trace';
      case LogLevel.Debug:
        return 'debug';
      case LogLevel.Info:
        return 'info';
      case LogLevel.Warn:
        return 'warn';
      case LogLevel.Error:
        return 'error';
      case LogLevel.Fatal:
        return 'fatal';
      default:
        return 'unknown';
    }
  }
}

const logger = new Logger();

export default logger;
