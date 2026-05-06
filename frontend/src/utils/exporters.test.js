import { describe, expect, it } from "vitest";

import { buildCsv } from "./exporters.js";

describe("exporters", () => {
  it("escapes CSV values", () => {
    const csv = buildCsv([
      {
        timestamp: "now",
        source: "Auth",
        event_type: "Authentication",
        score: 0.9,
        tier: "HIGH",
        destination: "SIEM",
        reason: 'Contains "failed" login',
        raw: "sshd failed login"
      }
    ]);
    expect(csv).toContain('"Contains ""failed"" login"');
  });
});
