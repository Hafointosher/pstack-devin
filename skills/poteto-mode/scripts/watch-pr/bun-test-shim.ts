// Minimal bun:test-compatible shim over node:test so upstream watch-pr tests
// run unmodified (except their import path) on Node — no Bun required.
import { describe, it } from "node:test";
import assert from "node:assert/strict";

export { describe, it };

function matchObject(received: unknown, expected: unknown): boolean {
  if (expected === null || typeof expected !== "object") return Object.is(received, expected);
  if (received === null || typeof received !== "object") return false;
  if (Array.isArray(expected)) {
    if (!Array.isArray(received) || received.length < expected.length) return false;
    return expected.every((e, i) => matchObject((received as unknown[])[i], e));
  }
  return Object.entries(expected as Record<string, unknown>).every(([k, v]) =>
    matchObject((received as Record<string, unknown>)[k], v)
  );
}

function makeExpect(received: unknown) {
  const api = {
    toBe(expected: unknown) {
      assert.ok(Object.is(received, expected), `expected ${JSON.stringify(received)} to be ${JSON.stringify(expected)}`);
    },
    toEqual(expected: unknown) {
      assert.deepEqual(received, expected);
    },
    toMatchObject(expected: unknown) {
      assert.ok(matchObject(received, expected), `expected ${JSON.stringify(received)?.slice(0, 300)} to match ${JSON.stringify(expected)?.slice(0, 300)}`);
    },
    toContain(expected: unknown) {
      if (typeof received === "string") assert.ok((received as string).includes(String(expected)), `expected string to contain ${String(expected)}`);
      else assert.ok((received as unknown[]).includes(expected), `expected array to contain ${JSON.stringify(expected)}`);
    },
    toHaveLength(expected: number) {
      assert.equal((received as { length: number }).length, expected);
    },
    toBeUndefined() {
      assert.equal(received, undefined);
    },
    toBeNull() {
      assert.equal(received, null);
    },
    toBeInstanceOf(expected: new (...args: never[]) => unknown) {
      assert.ok(received instanceof expected, `expected instance of ${expected.name}`);
    },
    toThrow(expected?: string | RegExp) {
      assert.equal(typeof received, "function", "toThrow requires a function");
      assert.throws(received as () => void, expected ? (typeof expected === "string" ? new RegExp(expected.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")) : expected) : undefined);
    },
    get not() {
      return {
        toContain(expected: unknown) {
          if (typeof received === "string") assert.ok(!(received as string).includes(String(expected)), `expected string not to contain ${String(expected)}`);
          else assert.ok(!(received as unknown[]).includes(expected), `expected array not to contain value`);
        },
        toBe(expected: unknown) {
          assert.ok(!Object.is(received, expected));
        },
      };
    },
    get rejects() {
      return {
        async toBeInstanceOf(expected: new (...args: never[]) => unknown) {
          try {
            await (received as Promise<unknown>);
          } catch (e) {
            assert.ok(e instanceof expected, `expected rejection to be instance of ${expected.name}, got ${(e as Error)?.constructor?.name}`);
            return;
          }
          assert.fail("expected promise to reject");
        },
        async toThrow(expected?: string | RegExp) {
          assert.equal(typeof (received as Promise<unknown>)?.then, "function", "rejects requires a promise");
          await assert.rejects(received as Promise<unknown>, expected ? (typeof expected === "string" ? new RegExp(expected.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")) : expected) : undefined);
        },
      };
    },
  };
  return api;
}

export function expect(received: unknown) {
  return makeExpect(received);
}
