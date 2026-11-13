import test from "node:test";
import assert from "node:assert/strict";
import { addJs } from "../src/js_calculator.mjs";

test("JavaScript calculator adds two numbers", () => {
  assert.equal(addJs(20, 22), 42);
});