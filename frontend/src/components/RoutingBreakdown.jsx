import { Archive, Database, Server } from "lucide-react";

import { TIER_META } from "../utils/constants.js";

const icons = {
  HIGH: Server,
  MEDIUM: Database,
  LOW: Archive
};

export default function RoutingBreakdown({ summary, thresholds }) {
  const total = summary.total || 0;
  const rows = [
    { tier: "HIGH", count: summary.high_count || 0, label: `score >= ${thresholds.high}` },
    {
      tier: "MEDIUM",
      count: summary.medium_count || 0,
      label: `${thresholds.medium} <= score < ${thresholds.high}`
    },
    { tier: "LOW", count: summary.low_count || 0, label: `score < ${thresholds.medium}` }
  ];

  return (
    <section className="rounded-lg border border-border bg-panel p-5">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-text">Routing Breakdown</h2>
        <span className="rounded-full bg-surface px-3 py-1 text-xs font-medium text-muted">{total} logs</span>
      </div>
      <div className="mt-5 space-y-4">
        {rows.map((row) => {
          const meta = TIER_META[row.tier];
          const Icon = icons[row.tier];
          const pct = total ? Math.round((row.count / total) * 100) : 0;
          return (
            <div key={row.tier} className="space-y-2">
              <div className="flex items-center justify-between gap-3">
                <div className="flex min-w-0 items-center gap-3">
                  <span className={`rounded-md border ${meta.borderClass} p-2 ${meta.textClass}`}>
                    <Icon aria-hidden="true" size={16} />
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-text">{meta.label}</p>
                    <p className="truncate text-xs text-muted">{row.label}</p>
                  </div>
                </div>
                <span className="text-sm font-semibold text-text">{row.count}</span>
              </div>
              <div className="h-2 rounded-full bg-[color:var(--color-track)]">
                <div
                  className={`h-full rounded-full ${meta.className}`}
                  style={{ width: `${pct}%` }}
                  aria-label={`${meta.label} ${pct}%`}
                />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
