import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { FileBlob, PresentationFile } from "/Users/jiayiwang0106/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const input = path.join(root, "site/generated/case-competition-profissional-preview.pptx");
const output = path.join(root, "site/generated/case-competition-profissional-preview.watermarked.pptx");
const previewDir = path.join(root, "site/previews/case-profissional");
const qaDir = path.join(root, ".tmp/case-pptx-qa");

async function writeBlob(target, blob) {
  await fs.writeFile(target, new Uint8Array(await blob.arrayBuffer()));
}

const presentation = await PresentationFile.importPptx(await FileBlob.load(input));
const proto = presentation.toProto();

for (const [index, slide] of presentation.slides.items.entries()) {
  const slideProto = proto.slides[index];
  const width = Number(slideProto.widthEmu) / 9525;
  const height = Number(slideProto.heightEmu) / 9525;
  const mark = slide.shapes.add({
    geometry: "rect",
    name: `joy-copyright-watermark-${index + 1}`,
    position: { left: (width - 246) / 2, top: height - 24, width: 246, height: 17 },
    fill: "#071A33",
    line: { style: "solid", fill: "#071A33", width: 0 },
  });
  mark.text = "COPYRIGHT RESERVED BY JOY";
  mark.text.style = {
    fontSize: 9,
    fontFamily: "Arial",
    bold: true,
    color: "#FFFFFF",
    alignment: "center",
    verticalAlignment: "middle",
  };
}

await fs.mkdir(qaDir, { recursive: true });
for (const [index, slide] of presentation.slides.items.entries()) {
  const stem = `slide-${String(index + 1).padStart(2, "0")}`;
  await writeBlob(path.join(previewDir, `${stem}.png`), await presentation.export({ slide, format: "png", scale: 2 }));
  await writeBlob(path.join(qaDir, `${stem}.png`), await presentation.export({ slide, format: "png", scale: 1 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(qaDir, `${stem}.layout.json`), await layout.text());
}
await writeBlob(path.join(qaDir, "montage.webp"), await presentation.export({ format: "webp", montage: true, scale: 1 }));

const after = await presentation.inspect({ kind: "slide,textbox,shape", search: "COPYRIGHT RESERVED BY JOY", maxChars: 8000 });
await fs.writeFile(path.join(qaDir, "watermark-inspect.ndjson"), after.ndjson);
const count = after.ndjson.split("\n").filter((line) => line.includes("COPYRIGHT RESERVED BY JOY")).length;
if (count !== presentation.slides.items.length) {
  throw new Error(`Expected ${presentation.slides.items.length} watermark records, found ${count}`);
}

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(output);
console.log(`Watermarked ${presentation.slides.items.length} slides: ${output}`);
