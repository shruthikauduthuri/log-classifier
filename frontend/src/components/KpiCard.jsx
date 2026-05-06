export default function KpiCard({ label, value, tone = "brand", helper }) {
  const toneClass = {
    brand: "text-brand",
    high: "text-high",
    medium: "text-medium",
    low: "text-muted",
    success: "text-success"
  }[tone];

  return (
    <section className="rounded-lg border border-border bg-panel p-4 shadow-sm" aria-label={label}>
      <p className="text-sm font-medium text-muted">{label}</p>
      <p className={`mt-3 text-3xl font-semibold ${toneClass}`}>{value}</p>
      {helper ? <p className="mt-2 text-xs text-muted">{helper}</p> : null}
    </section>
  );
}
