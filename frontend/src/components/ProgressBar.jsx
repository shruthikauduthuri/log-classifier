export default function ProgressBar({ progress }) {
  const total = progress.total || 0;
  const current = progress.current || 0;
  const pct = total ? Math.round((current / total) * 100) : 0;

  return (
    <div className="space-y-2" aria-live="polite">
      <div className="flex items-center justify-between text-xs font-medium text-muted">
        <span>Batch progress</span>
        <span>
          {current}/{total || 0}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-[color:var(--color-track)]">
        <div
          className="h-full rounded-full bg-success transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
