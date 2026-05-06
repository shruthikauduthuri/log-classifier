import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { buildSourceRows } from "../utils/metrics.js";

export default function SourceChart({ results }) {
  const data = buildSourceRows(results);

  return (
    <section className="rounded-lg border border-border bg-panel p-5">
      <h2 className="text-base font-semibold text-text">Volume by Source</h2>
      <div className="mt-4 h-64" aria-label="Volume by log source chart">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 12, bottom: 0, left: -20 }}>
            <CartesianGrid stroke="var(--color-border)" vertical={false} />
            <XAxis dataKey="source" tick={{ fill: "var(--color-muted)", fontSize: 12 }} />
            <YAxis allowDecimals={false} tick={{ fill: "var(--color-muted)", fontSize: 12 }} />
            <Tooltip
              cursor={{ fill: "rgba(26,60,94,0.06)" }}
              contentStyle={{
                background: "var(--color-panel)",
                color: "var(--color-text)",
                border: "1px solid var(--color-border)",
                borderRadius: 8
              }}
            />
            <Bar dataKey="HIGH" stackId="tier" fill="var(--color-high)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="MEDIUM" stackId="tier" fill="var(--color-medium)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="LOW" stackId="tier" fill="var(--color-low)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
