#!/usr/bin/env node
// Cross-platform decision-log appender for show-me-your-work. Adapted from Lauren Tan pstack (MIT).
// Usage: node log.mjs LOGFILE DECISION WHY EVIDENCE NEXT
import fs from "node:fs";
import path from "node:path";

const HEADER = "ts\tdecision\twhy\tevidence\tnext\n";
const clean = (v) =>
  v.replace(/[\t\r\n]+/g, " ").replace(/^([=+\-@])/, "'$1");

function main(argv) {
  if (argv.length !== 5 || argv.includes("--help")) {
    console.error("Usage: node log.mjs LOGFILE DECISION WHY EVIDENCE NEXT");
    return argv.includes("--help") && argv.length === 1 ? 0 : 1;
  }
  const [file, ...fields] = argv;
  const dir = path.dirname(path.resolve(file));
  fs.mkdirSync(dir, { recursive: true });
  if (!fs.existsSync(file) || fs.statSync(file).size === 0)
    fs.writeFileSync(file, HEADER, "utf8");
  const row = [new Date().toISOString(), ...fields.map(clean)].join("\t") + "\n";
  fs.appendFileSync(file, row, "utf8");
  return 0;
}
process.exitCode = main(process.argv.slice(2));
