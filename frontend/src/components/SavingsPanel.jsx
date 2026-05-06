import { CircleDollarSign, TrendingDown } from "lucide-react";

export default function SavingsPanel({ summary }) {
  return (
    <section className="rounded-lg border border-border bg-panel p-5">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-text">SIEM Cost Savings</h2>
        <CircleDollarSign aria-hidden="true" className="text-success" size={20} />
      </div>
      <div className="mt-6 flex items-end gap-3">
        <p className="text-5xl font-semibold text-success">{summary.siem_savings_pct || 0}%</p>
        <p className="pb-2 text-sm text-muted">reduction vs. routing all logs to SIEM</p>
      </div>
      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        <Metric label="Filtered logs" value={summary.filtered_count || 0} />
        <Metric
          label="Avg HIGH score"
          value={Number(summary.average_scores?.HIGH || 0).toFixed(3)}
        />
        <Metric
          label="Est. monthly"
          value={`$${Number(summary.estimated_monthly_savings || 0).toLocaleString()}`}
        />
      </div>
      <div className="mt-5 inline-flex items-center gap-2 rounded-full bg-[rgba(46,125,50,0.1)] px-3 py-1.5 text-sm font-medium text-success">
        <TrendingDown aria-hidden="true" size={16} />
        <span>Lower SIEM ingestion with full forensic visibility retained</span>
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-md bg-surface p-3">
      <p className="text-xs text-muted">{label}</p>
      <p className="mt-1 text-lg font-semibold text-text">{value}</p>
    </div>
  );
}
