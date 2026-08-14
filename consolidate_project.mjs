// Node.js build entry point for environments without a Python runtime.
// It mirrors consolidate_project.py and reads the canonical 5-file map from it.
import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const BASE_DIR = path.dirname(fileURLToPath(import.meta.url));
const SOURCE_DIR = path.join(BASE_DIR, "Not_Required_Upload", "Canonical_Source_84");
const COMPILER_VERSION = "2.0";
const excluded = new Set(["API_KEYS_CONFIG.env", ".env.example", "API_PROVIDERS_AND_FREE_TIERS_GUIDE.md", "test_apis.py"]);
const pythonSource = await readFile(path.join(BASE_DIR, "consolidate_project.py"), "utf8");
const literal = pythonSource.split("FIVE_FILE_MAP = ")[1].split("\n\nNINE_FILE_MAP =")[0];
const five = Function(`"use strict"; return (${literal});`)();
const skills = five["03_Master_Skill_Library.md"];
const fundamentals = five["04_Master_Knowledge_Base_Vol_1_Fundamentals_Valuation_Governance.md"];
const frameworks = five["05_Master_Knowledge_Base_Vol_2_Sectors_Frameworks_Screening.md"];
const nine = {
  "01_System_Core_Instructions_Architecture.md": five["01_Master_System_Core_Instructions_Architecture.md"],
  "02_Engine_Contracts_Schemas_Registries.md": five["02_Master_Engine_Contracts_Schemas_Registries.md"],
  "03_Workflow_Skills_01_to_25.md": [skills[0]],
  "04_Analytical_Lens_Skills_26_to_41.md": skills.slice(1),
  "05_Knowledge_Base_Vol_1_Economics_Financials.md": fundamentals.slice(0, 12),
  "06_Knowledge_Base_Vol_2_Markets_Governance_Macro.md": fundamentals.slice(12),
  "07_Knowledge_Base_Vol_3_Forensics_Moats_Banking.md": frameworks.slice(0, 8),
  "08_Knowledge_Base_Vol_4_Sector_Deep_Dives.md": frameworks.slice(8, 17),
  "09_Knowledge_Base_Vol_5_Screening_Portfolio_Glossaries.md": frameworks.slice(17),
};

const label = (file) => path.basename(file, ".md").replace("_v_0_0", "").replaceAll("_", " ");
const sourceRecord = async (file) => {
  const payload = await readFile(path.join(SOURCE_DIR, file), "utf8");
  return [payload, createHash("sha256").update(payload, "utf8").digest("hex"), Buffer.byteLength(payload, "utf8")];
};
const routing = (mapping) => [
  "| Upload file | Primary use | Sources |", "|---|---|---:|",
  ...Object.entries(mapping).map(([name, files]) => `| \`${name}\` | ${label(name).replace("Master ", "")} | ${files.length} |`),
].join("\n");

async function wrapper(name, files, mapping) {
  const manifest = await Promise.all(files.map(async (file, index) => {
    const [, digest, bytes] = await sourceRecord(file);
    return `| ${index + 1} | \`${path.basename(file)}\` | ${bytes.toLocaleString("en-US")} | \`${digest}\` |`;
  }));
  return `# ${path.basename(name, ".md")}

> **IERL AI Equity OS — curated upload artifact**  
> Compiler: \`consolidate_project.py\` / \`consolidate_project.mjs\` v${COMPILER_VERSION} · Source documents: ${files.length} · Secrets: excluded

## Operating contract

This is a generated, read-only working volume. The separately maintained source documents are authoritative; regenerate this file after changing a source. The wrapper provides navigation and execution discipline, but does not replace a source rule. Embedded source payloads are preserved verbatim between the \`BEGIN\` and \`END\` markers.

1. Route the request to the narrowest relevant upload file, then use the named embedded document(s); do not treat an unrelated volume as evidence.
2. Execute applicable skill steps in order. If a required input, timeframe, benchmark, or source is absent, state the gap and the effect on confidence; never silently invent it.
3. Separate **reported facts**, **calculations**, **assumptions**, and **inference**. Date all market-sensitive claims and identify the data source or user-provided input.
4. Surface disconfirming evidence, governance/forensic risk, liquidity risk, valuation risk, and material uncertainty before a conclusion. A positive screen is not investment advice or a guarantee.
5. When source documents conflict, prefer the more specific, later-versioned requirement; if unresolved, disclose the conflict and use the more conservative interpretation. Never override platform safety requirements.

## Fast task routing

${routing(mapping)}

**Default research sequence:** define decision and horizon → gather dated evidence → run the relevant workflow/analytical skill → apply risk and forensic checks → calculate/compare → present conclusion, counter-case, and confidence. For a company decision, consult core instructions, the applicable skill, fundamentals/valuation, sector context, and risk/forensics rather than relying on one metric.

## Scope and privacy boundary

This bundle contains static methodology and knowledge only. It contains no credentials and cannot by itself read local files, call APIs, fetch live market data, trade, or access private accounts. The following local integration/private files are intentionally excluded: ${[...excluded].sort().map((x) => `\`${x}\``).join(", ")}.

## Embedded source manifest

The SHA-256 values cover the exact UTF-8 source payload, not this wrapper. Use the manifest to audit a rebuild.

| # | Source document | UTF-8 bytes | SHA-256 |
|---:|---|---:|---|
${manifest.join("\n")}

---

`;
}

async function build(mapping, directory) {
  await mkdir(directory, { recursive: true });
  const all = Object.values(mapping).flat();
  if (new Set(all).size !== all.length) throw new Error("Duplicate source document in bundle");
  for (const [name, files] of Object.entries(mapping)) {
    if (files.some((file) => excluded.has(path.basename(file)))) throw new Error(`Private source in ${name}`);
    const chunks = [await wrapper(name, files, mapping)];
    for (const [index, file] of files.entries()) {
      const [payload, digest] = await sourceRecord(file);
      chunks.push(`<!-- BEGIN SYSTEM FILE ${index + 1}: ${path.basename(file)} | SHA256: ${digest} -->\n`);
      chunks.push(`## Embedded source ${index + 1}: ${label(file)}\n\n`, payload, payload.endsWith("\n") ? "" : "\n");
      chunks.push(`<!-- END SYSTEM FILE ${index + 1}: ${path.basename(file)} -->\n\n---\n\n`);
    }
    const output = chunks.join("");
    await writeFile(path.join(directory, name), output, "utf8");
    const markers = (output.match(/<!-- BEGIN SYSTEM FILE /g) || []).length;
    if (markers !== files.length) throw new Error(`${name}: marker validation failed`);
    console.log(`Created: ${name} (${files.length} sources; ${Buffer.byteLength(output, "utf8").toLocaleString("en-US")} bytes)`);
  }
  console.log(`Validated: ${path.basename(directory)} — ${all.length} unique embedded sources`);
}

await build(five, path.join(BASE_DIR, "CONSOLIDATED_5_FILE_SYSTEM"));
await build(nine, path.join(BASE_DIR, "CONSOLIDATED_9_FILE_SYSTEM"));
