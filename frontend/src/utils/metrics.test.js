import { describe, expect, it } from "vitest";

import { buildSourceRows, summaryFromResults } from "./metrics.js";

const results = [
  { tier: "HIGH", score: 0.9, source: "Auth" },
  { tier: "MEDIUM", score: 0.5, source: "Auth" },
  { tier: "LOW", score: 0.1, source: "DNS" }
];

describe("metrics", () => {
  it("summarizes routing results", () => {
    const summary = summaryFromResults(results);
    expect(summary.total).toBe(3);
    expect(summary.high_count).toBe(1);
    expect(summary.siem_savings_pct).toBe(66.7);
  });

  it("builds source rows", () => {
    expect(buildSourceRows(results)).toEqual([
      { source: "Auth", HIGH: 1, MEDIUM: 1, LOW: 0, total: 2 },
      { source: "DNS", HIGH: 0, MEDIUM: 0, LOW: 1, total: 1 }
    ]);
  });
});
