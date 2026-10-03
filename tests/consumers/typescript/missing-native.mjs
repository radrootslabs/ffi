import assert from "node:assert/strict";

await assert.rejects(import("radroots"), /Cannot find native binding/);
