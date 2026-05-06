import { ShieldAlert } from "lucide-react";

export default function EmptyState() {
  return (
    <section className="rounded-lg border border-dashed border-border bg-panel p-8 text-center">
      <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-surface">
        <ShieldAlert aria-hidden="true" className="text-brand" size={34} />
      </div>
      <h2 className="mt-5 text-lg font-semibold text-text">Awaiting first classification</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-muted">
        Upload or paste logs to generate routing metrics, source volume, cost savings, and a complete
        audit trail of AI decisions.
      </p>
    </section>
  );
}
