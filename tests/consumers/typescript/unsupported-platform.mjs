import assert from "node:assert/strict";

Object.defineProperty(process, "platform", { value: "radroots-unsupported" });
await assert.rejects(import("radroots"), (error) => {
  assert.match(error.message, /Cannot find native binding/);
  let cause = error.cause;
  while (cause && !cause.message.includes("Unsupported OS"))
    cause = cause.cause;
  assert.match(cause?.message ?? "", /Unsupported OS: radroots-unsupported/);
  return true;
});
