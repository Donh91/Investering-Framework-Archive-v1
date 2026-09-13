import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
const outputPath = resolve(siteDir, "dist/social-card.png");
const EXPECTED_BYTES = 7416;
const EXPECTED_SHA256 = "131b7096f3a144333e977a236d0b1bae2a0c6aaff7df3a83e1715aeb70bf9f86";

const chunks = [];
for (let index = 1; index <= 4; index += 1) {
  chunks.push((await readFile(resolve(siteDir, `social-card.part${index}.b64`), "utf8")).trim());
}

const png = Buffer.from(chunks.join(""), "base64");
const digest = createHash("sha256").update(png).digest("hex");
const signature = png.subarray(0, 8).toString("hex");

if (png.length !== EXPECTED_BYTES || digest !== EXPECTED_SHA256 || signature !== "89504e470d0a1a0a") {
  throw new Error(`Social card verification failed: bytes=${png.length}, sha256=${digest}, signature=${signature}`);
}

await writeFile(outputPath, png);
console.log(`Built verified Cycle Navigator social card: ${png.length} bytes, sha256=${digest}`);
