import { ArrowDownUp } from "lucide-react";
import { useMemo, useState } from "react";

import { TIER_META } from "../utils/constants.js";

export default function ClassificationTable({ results }) {
  const [sort, setSort] = useState({ key: "timestamp", direction: "desc" });

  const sorted = useMemo(() => {
    const copy = [...results];
    copy.sort((a, b) => {
      const left = a[sort.key];
      const right = b[sort.key];
      if (sort.key === "score") {
        return sort.direction === "asc" ? left - right : right - left;
      }
      return sort.direction === "asc"
        ? String(left).localeCompare(String(right))
        : String(right).localeCompare(String(left));
    });
    return copy;
  }, [results, sort]);

  function toggle(key) {
    setSort((current) => ({
      key,
      direction: current.key === key && current.direction === "asc" ? "desc" : "asc"
    }));
  }

  return (
    <section className="rounded-lg border border-border bg-panel p-5">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-text">Recent Classifications</h2>
        <span className="rounded-full bg-surface px-3 py-1 text-xs font-medium text-muted">
          {results.length} rows
        </span>
      </div>
      <div className="mt-4 max-h-[520px] overflow-auto rounded-md border border-border">
        <table className="min-w-full divide-y divide-border text-left text-sm">
          <thead className="sticky top-0 bg-brand text-white">
            <tr>
              <Header label="Timestamp" onClick={() => toggle("timestamp")} />
              <Header label="Source" onClick={() => toggle("source")} />
              <Header label="Event" onClick={() => toggle("event_type")} />
              <Header label="Score" onClick={() => toggle("score")} />
              <Header label="Destination" onClick={() => toggle("destination")} />
              <th className="px-4 py-3 font-semibold">Reason</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border bg-panel">
            {sorted.slice(0, 500).map((item, index) => (
              <tr key={`${item.timestamp}-${index}`} className="align-top">
                <td className="whitespace-nowrap px-4 py-3 text-xs text-muted">
                  {formatTime(item.timestamp)}
                </td>
                <td className="px-4 py-3 font-medium text-text">{item.source}</td>
                <td className="px-4 py-3 text-muted">{item.event_type}</td>
                <td className="px-4 py-3">
                  <Pill tier={item.tier}>{Number(item.score).toFixed(3)}</Pill>
                </td>
                <td className="px-4 py-3">
                  <Pill tier={item.tier}>{item.destination}</Pill>
                </td>
                <td className="max-w-sm px-4 py-3 text-muted">
                  <p>{item.reason}</p>
                  <p className="mt-1 line-clamp-2 font-mono text-xs opacity-75">{item.raw}</p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Header({ label, onClick }) {
  return (
    <th className="px-4 py-3 font-semibold">
      <button type="button" className="inline-flex items-center gap-2" onClick={onClick}>
        {label}
        <ArrowDownUp aria-hidden="true" size={14} />
      </button>
    </th>
  );
}

function Pill({ tier, children }) {
  const meta = TIER_META[tier] || TIER_META.LOW;
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${meta.className}`}>{children}</span>;
}

function formatTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}
