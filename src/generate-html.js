/* src/generate-html.js */

"use strict";

const fs = require("fs");
const path = require("path");
const Mustache = require("mustache");

function readUtf8(filePath) {
  try {
    return fs.readFileSync(filePath, "utf-8");
  } catch (err) {
    const msg = err && err.message ? err.message : String(err);
    throw new Error(`Failed to read file: ${filePath}\n${msg}`);
  }
}

function readJson(filePath) {
  const raw = readUtf8(filePath);
  try {
    return JSON.parse(raw);
  } catch (err) {
    const msg = err && err.message ? err.message : String(err);
    throw new Error(`Failed to parse JSON: ${filePath}\n${msg}`);
  }
}

function writeUtf8(filePath, contents) {
  try {
    fs.writeFileSync(filePath, contents, "utf-8");
  } catch (err) {
    const msg = err && err.message ? err.message : String(err);
    throw new Error(`Failed to write file: ${filePath}\n${msg}`);
  }
}

function formatHumanEt(date) {
  // America/New_York (handles DST correctly)
  const dtf = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/New_York",
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZoneName: "short",
  });
  return dtf.format(date);
}

function getLastUpdatedFromFileMtime(filePath) {
  try {
    const st = fs.statSync(filePath);
    // mtime is when data.json was last modified (i.e., data generation completed)
    return st.mtime instanceof Date ? st.mtime : new Date(st.mtime);
  } catch {
    return null;
  }
}

function main() {
  const rootDir = __dirname;
  const dataPath = path.join(rootDir, "data.json");
  const templatePath = path.join(rootDir, "index.html.mustache");
  const outputPath = path.join(rootDir, "index.html");

  const data = readJson(dataPath);

  // Mustache renders missing keys as empty strings; that can hide data issues.
  // We do a small sanity check on expected keys to catch broken pipelines early.
  const requiredKeys = [
    "agencies_with_agreement",
    "total_sandbox_orgs",
    "total_domain_instances",
    "total_apps",
    "total_users",
    "total_database_instances",
    "total_s3_instances",
    "total_es_instances",
    "total_redis_instances",
  ];

  const missing = requiredKeys.filter((k) => !(k in data));
  if (missing.length > 0) {
    throw new Error(
      `data.json is missing required keys:\n- ${missing.join("\n- ")}\n\n` +
        "This usually means the data generation step failed or wrote unexpected output."
    );
  }

  // “Last updated” should reflect data freshness, not build time.
  const lastUpdated = getLastUpdatedFromFileMtime(dataPath) ?? new Date();

  const lastUpdatedUtcIso = new Date(lastUpdated.getTime()).toISOString();

  const view = Object.assign({}, data, {
    // Metadata fields for templates / future JS enhancements
    last_updated_epoch_ms: lastUpdated.getTime(),
    last_updated_utc: lastUpdatedUtcIso,
    last_updated_human: formatHumanEt(lastUpdated),
  });

  const template = readUtf8(templatePath);

  const output = Mustache.render(template, view);
  if (!output || output.trim().length === 0) {
    throw new Error("Template rendered empty output (unexpected).");
  }

  writeUtf8(outputPath, output);
  process.stdout.write(`Wrote ${outputPath}\n`);
}

try {
  main();
} catch (err) {
  const msg = err && err.message ? err.message : String(err);
  process.stderr.write(`${msg}\n`);
  process.exit(1);
}
