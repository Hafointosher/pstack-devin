// Minimal commander-compatible surface used by cli.ts — zero external dependencies.
// Implements: Command, Option, CommanderError, InvalidArgumentError.
export class CommanderError extends Error {
  readonly exitCode: number;
  readonly code: string;
  constructor(exitCode: number, code: string, message: string) {
    super(message);
    this.name = "CommanderError";
    this.exitCode = exitCode;
    this.code = code;
  }
}
export class InvalidArgumentError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "InvalidArgumentError";
  }
}
interface OptSpec {
  flags: string;
  long: string;
  key: string;
  takesValue: boolean;
  parser?: (v: string) => unknown;
  deflt?: unknown;
  conflicts?: string[];
}
const camel = (s: string) => s.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
function parseFlags(flags: string): OptSpec {
  const long = flags.split(/[ ,|]+/).find((f) => f.startsWith("--"))!;
  const name = long.replace(/^--/, "");
  return {
    flags,
    long,
    key: camel(name),
    takesValue: /<[^>]+>/.test(flags),
  };
}
export class Option {
  readonly spec: OptSpec;
  constructor(flags: string, _description?: string) {
    this.spec = parseFlags(flags);
  }
  default(v: unknown): this {
    this.spec.deflt = v;
    return this;
  }
  conflicts(keys: string | string[]): this {
    this.spec.conflicts = Array.isArray(keys) ? keys : [keys];
    return this;
  }
}
export class Command {
  private optSpecs: OptSpec[] = [];
  private out: (v: string) => void = (v) => process.stdout.write(v);
  private err: (v: string) => void = (v) => process.stderr.write(v);
  private desc = "";
  private values: Record<string, unknown> = {};
  private programName: string;
  constructor(programName: string) { this.programName = programName; }
  description(d: string): this {
    this.desc = d;
    return this;
  }
  configureOutput(o: { writeOut: (v: string) => void; writeErr: (v: string) => void }): this {
    this.out = o.writeOut;
    this.err = o.writeErr;
    return this;
  }
  exitOverride(): this {
    return this;
  }
  option(flags: string, _desc?: string, parserOrDef?: unknown, deflt?: unknown): this {
    const spec = parseFlags(flags);
    if (typeof parserOrDef === "function") {
      spec.parser = parserOrDef as (v: string) => unknown;
      spec.deflt = deflt;
    } else if (parserOrDef !== undefined) spec.deflt = parserOrDef;
    this.optSpecs.push(spec);
    return this;
  }
  addOption(o: Option): this {
    this.optSpecs.push(o.spec);
    return this;
  }
  helpText(): string {
    const lines = [`Usage: ${this.programName} [options]`, "", this.desc, "", "Options:"];
    for (const o of this.optSpecs) lines.push(`  ${o.flags}`);
    return lines.join("\n") + "\n";
  }
  error(message: string): never {
    this.err(message + "\n");
    throw new CommanderError(1, "commander.error", message);
  }
  parse(argv: readonly string[], _opts?: { from: string }): this {
    const values: Record<string, unknown> = {};
    for (const o of this.optSpecs) if (o.deflt !== undefined) values[o.key] = o.deflt;
    const args = [...argv];
    const byLong = new Map(this.optSpecs.map((o) => [o.long, o]));
    if (args.includes("--help") || args.includes("-h")) {
      this.out(this.helpText());
      throw new CommanderError(0, "commander.help", "help");
    }
    for (let i = 0; i < args.length; i++) {
      const arg = args[i];
      if (!arg.startsWith("--")) continue;
      const eq = arg.indexOf("=");
      const flag = eq >= 0 ? arg.slice(0, eq) : arg;
      const spec = byLong.get(flag);
      if (!spec) this.error(`error: unknown option '${flag}'`);
      if (!spec!.takesValue) {
        values[spec!.key] = true;
        continue;
      }
      const raw = eq >= 0 ? arg.slice(eq + 1) : args[++i];
      if (raw === undefined) this.error(`error: option '${flag}' requires a value`);
      try {
        values[spec!.key] = spec!.parser ? spec!.parser(raw) : raw;
      } catch (e) {
        if (e instanceof InvalidArgumentError)
          this.error(`error: option '${spec!.flags}' argument '${raw}' is invalid. ${e.message}`);
        throw e;
      }
    }
    for (const o of this.optSpecs)
      if (o.conflicts)
        for (const c of o.conflicts)
          if (values[o.key] && values[c])
            this.error(`error: option '${o.long}' conflicts with another option`);
    this.values = values;
    return this;
  }
  opts<T>(): T {
    return this.values as T;
  }
}
