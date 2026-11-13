import test from "node:test";
import assert from "node:assert/strict";
import { add } from "../dist/calculator.js";

test("TypeScript calculator adds two numbers", () => {
  assert.equal(add(20, 22), 42);
});