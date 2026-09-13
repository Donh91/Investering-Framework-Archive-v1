import { copyFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
await copyFile(
  resolve(siteDir, "apple-prototype.html"),
  resolve(siteDir, "dist/apple-prototype.html")
);
console.log("Added hidden Apple-level Cycle Navigator design prototype to public bundle");
