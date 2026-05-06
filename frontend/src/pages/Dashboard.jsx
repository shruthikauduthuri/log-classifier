import { Download, FileDown, ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";

import ClassificationTable from "../components/ClassificationTable.jsx";
import EmptyState from "../components/EmptyState.jsx";
import KpiCard from "../components/KpiCard.jsx";
import RoutingBreakdown from "../components/RoutingBreakdown.jsx";
import SavingsPanel from "../components/SavingsPanel.jsx";
import SourceChart from "../components/SourceChart.jsx";
import UploadPanel from "../components/UploadPanel.jsx";
import { useClassify } from "../hooks/useClassify.js";
import { downloadCsv, downloadPdfSummary } from "../utils/exporters.js";

export default function Dashboard() {
  const {
    classify,
    results,
    summary,
    progress,
    quota,
    isLoading,
    error,
    hasResults
  } = useClassify();
  const [thresholds, setThresholds] = useState({ high: "0.70", medium: "0.40" });

  const kpis = useMemo(
    () => [
      { label: "Logs Processed", value: summary.total, tone: "brand", helper: "Current session" },
      { label: "Sent to SIEM", value: summary.high_count, tone: "high", helper: "High fidelity" },
      { label: "Data Lake", value: summary.medium_count, tone: "medium", helper: "Queryable retention" },
      { label: "Cold / Archived", value: summary.low_count, tone: "low", helper: "Noise retained cheaply" }
    ],
    [summary]
  );

  function handleSubmit(payload) {
    setThresholds({
      high: Number(payload.high_threshold).toFixed(2),
      medium: Number(payload.medium_threshold).toFixed(2)
    });
    classify(payload);
  }

  return (
    <main className="min-h-screen bg-surface text-text">
      <header className="border-b border-border bg-panel/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-2 text-sm text-muted">
              <ShieldCheck aria-hidden="true" size={16} />
            </div>
            <div>
              <p className="text-sm font-semibold text-text">Log Noise Classifier</p>
              <p className="text-xs text-muted">SIEM routing</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              className="inline-flex h-10 items-center gap-2 rounded-md border border-border px-3 text-sm font-semibold text-text transition hover:bg-surface disabled:cursor-not-allowed disabled:opacity-50"
              disabled={!hasResults}
              onClick={() => downloadCsv(results)}
            >
              <Download aria-hidden="true" size={16} />
              CSV
            </button>
            <button
              type="button"
              className="inline-flex h-10 items-center gap-2 rounded-md border border-border px-3 text-sm font-semibold text-text transition hover:bg-surface disabled:cursor-not-allowed disabled:opacity-50"
              disabled={!hasResults}
              onClick={() => downloadPdfSummary(summary, results)}
            >
              <FileDown aria-hidden="true" size={16} />
              PDF
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[390px_minmax(0,1fr)] lg:px-8">
        <aside className="space-y-4 lg:sticky lg:top-6 lg:self-start">
          <UploadPanel
            onSubmit={handleSubmit}
            isLoading={isLoading}
            progress={progress}
            quota={quota}
          />
        </aside>

        <section className="space-y-6">
          {error ? (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-high">
              {error}
            </div>
          ) : null}

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {kpis.map((kpi) => (
              <KpiCard key={kpi.label} {...kpi} />
            ))}
          </div>

          {hasResults ? (
            <>
              <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(360px,0.8fr)]">
                <RoutingBreakdown summary={summary} thresholds={thresholds} />
                <SavingsPanel summary={summary} />
              </div>
              <SourceChart results={results} />
              <ClassificationTable results={results} />
            </>
          ) : (
            <EmptyState />
          )}
        </section>
      </div>
    </main>
  );
}
