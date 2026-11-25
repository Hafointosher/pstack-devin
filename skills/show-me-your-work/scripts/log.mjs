#!/usr/bin/env node
// Cross-platform decision-log appender for show-me-your-work. Adapted from Lauren Tan pstack (MIT).
// Usage: node log.mjs LOGFILE PHASE DECISION WHY EVIDENCE RESULT
import fs from "node:fs";
import path from "node:path";

const HEADER = "ts\tphase\tdecision\twhy\tevidence\tresult\n";
// One-for-one replacement, like `tr '\t\n\r' '   '`: control characters become
// single spaces so cells stay on one line. A cell whose first character a
// spreadsheet would parse as a formula (=, +, -, @) gets a single-quote prefix,
// because attacker-controlled evidence must not execute when a reviewer opens
// the log in a spreadsheet.
const clean = (v) =>
  v.replace(/[\t\n\r]/g, " ").replace(/^([=+\-@])/, "'$1");

function main(argv) {
  if (argv.length !== 6 || argv.includes("--help")) {
    console.error("Usage: node log.mjs LOGFILE PHASE DECISION WHY EVIDENCE RESULT");
    return argv.includes("--help") && argv.length === 1 ? 0 : 1;
  }
  const [file, ...fields] = argv;
  const dir = path.dirname(path.resolve(file));
  fs.mkdirSync(dir, { recursive: true });
  // Append, never write: on some network mounts the exists/size probe can
  // false-negative for a log that exists, and a truncating write would destroy
  // existing rows. The worst case here is one stray header line.
  if (!fs.existsSync(file) || fs.statSync(file).size === 0)
    fs.appendFileSync(file, HEADER, "utf8");
  const ts = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const row = [ts, ...fields.map(clean)].join("\t") + "\n";
  fs.appendFileSync(file, row, "utf8");
  return 0;
}
process.exitCode = main(process.argv.slice(2));
