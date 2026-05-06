import { FileText, Loader2, ShieldCheck, UploadCloud } from "lucide-react";
import { useId, useState } from "react";

import { MAX_CLIENT_FILE_BYTES, SOURCE_OPTIONS } from "../utils/constants.js";

const sampleLogs = [
  "May 05 auth01 sshd[3201]: Failed password for root from 203.0.113.55 port 41220 ssh2",
  "firewall deny src=10.8.4.21 dst=198.51.100.8 dpt=443 proto=tcp reason=policy",
  "nginx access status=404 path=/healthz user_agent=uptime-check",
  "dns query suspicious-domain.example from host=workstation-14",
  "systemd[1]: Started daily cleanup job"
].join("\n");

export default function UploadPanel({ onSubmit, isLoading, progress, quota }) {
  const textId = useId();
  const fileId = useId();
  const [rawText, setRawText] = useState("");
  const [sourceHint, setSourceHint] = useState("Unknown");
  const [highThreshold, setHighThreshold] = useState(0.7);
  const [mediumThreshold, setMediumThreshold] = useState(0.4);
  const [fileName, setFileName] = useState("");
  const [localError, setLocalError] = useState("");

  const lines = rawText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  const isDisabled = isLoading || lines.length === 0 || mediumThreshold >= highThreshold;

  async function handleFile(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setLocalError("");
    if (!/\.(txt|log)$/i.test(file.name)) {
      setLocalError("Only .txt and .log files are supported.");
      return;
    }
    if (file.size > MAX_CLIENT_FILE_BYTES) {
      setLocalError("File must be 5 MB or smaller.");
      return;
    }
    setFileName(file.name);
    setRawText(await file.text());
  }

  function submit(event) {
    event.preventDefault();
    setLocalError("");
    if (mediumThreshold >= highThreshold) {
      setLocalError("Medium threshold must stay below the high threshold.");
      return;
    }
    onSubmit({
      logs: lines,
      source_hint: sourceHint,
      high_threshold: Number(highThreshold),
      medium_threshold: Number(mediumThreshold)
    });
  }

  return (
    <section className="rounded-lg border border-border bg-panel p-5 shadow-soft">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-success">Gemini guarded</p>
          <h1 className="mt-1 text-2xl font-semibold text-text">Log Noise Classifier</h1>
        </div>
        <div className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-2 text-sm text-muted">
          <ShieldCheck aria-hidden="true" size={16} />
          <span>Server-side key only</span>
        </div>
      </div>

      <form className="mt-5 space-y-5" onSubmit={submit}>
        <label
          htmlFor={fileId}
          className="flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface px-4 py-6 text-center transition hover:border-brand"
        >
          <UploadCloud aria-hidden="true" className="text-brand" size={28} />
          <span className="mt-3 text-sm font-semibold text-text">
            {fileName || "Drop in a .log or .txt file"}
          </span>
          <span className="mt-1 text-xs text-muted">5 MB max. Parsed locally before submission.</span>
          <input
            id={fileId}
            className="sr-only"
            type="file"
            accept=".log,.txt,text/plain"
            onChange={handleFile}
            disabled={isLoading}
          />
        </label>

        <div>
          <div className="mb-2 flex items-center justify-between gap-3">
            <label htmlFor={textId} className="text-sm font-semibold text-text">
              Raw log lines
            </label>
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-1.5 text-xs font-semibold text-brand transition hover:bg-surface"
              onClick={() => setRawText(sampleLogs)}
              disabled={isLoading}
            >
              <FileText aria-hidden="true" size={14} />
              Load sample
            </button>
          </div>
          <textarea
            id={textId}
            className="min-h-48 w-full resize-y rounded-lg border border-border bg-surface p-3 font-mono text-sm leading-6 text-text outline-none transition focus:border-brand focus:ring-2 focus:ring-[rgba(26,60,94,0.18)]"
            value={rawText}
            onChange={(event) => setRawText(event.target.value)}
            placeholder="Paste newline-delimited logs here..."
            spellCheck="false"
            disabled={isLoading}
          />
          <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-xs text-muted">
            <span>{lines.length} non-empty lines ready</span>
            {quota ? <span>{quota.calls_required} Gemini batch calls planned</span> : null}
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <label className="space-y-2">
            <span className="text-sm font-semibold text-text">Source hint</span>
            <select
              className="h-11 w-full rounded-md border border-border bg-surface px-3 text-sm text-text"
              value={sourceHint}
              onChange={(event) => setSourceHint(event.target.value)}
              disabled={isLoading}
            >
              {SOURCE_OPTIONS.map((source) => (
                <option key={source} value={source}>
                  {source}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-2">
            <span className="flex items-center justify-between text-sm font-semibold text-text">
              Medium <span className="text-muted">{Number(mediumThreshold).toFixed(2)}</span>
            </span>
            <input
              type="range"
              min="0"
              max="0.95"
              step="0.01"
              value={mediumThreshold}
              onChange={(event) => setMediumThreshold(event.target.value)}
              disabled={isLoading}
              aria-label="Medium threshold"
            />
          </label>

          <label className="space-y-2">
            <span className="flex items-center justify-between text-sm font-semibold text-text">
              High <span className="text-muted">{Number(highThreshold).toFixed(2)}</span>
            </span>
            <input
              type="range"
              min="0.05"
              max="1"
              step="0.01"
              value={highThreshold}
              onChange={(event) => setHighThreshold(event.target.value)}
              disabled={isLoading}
              aria-label="High threshold"
            />
          </label>
        </div>

        {progress.total ? <ProgressInline progress={progress} /> : null}
        {localError ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-high">{localError}</p> : null}

        <button
          type="submit"
          className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-brand px-4 text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-55"
          disabled={isDisabled}
        >
          {isLoading ? <Loader2 className="animate-spin" aria-hidden="true" size={18} /> : null}
          Classify logs
        </button>
      </form>
    </section>
  );
}

function ProgressInline({ progress }) {
  const pct = progress.total ? Math.round((progress.current / progress.total) * 100) : 0;
  return (
    <div className="rounded-lg border border-border bg-surface p-3" aria-label="Classification progress">
      <div className="mb-2 flex items-center justify-between text-xs text-muted">
        <span>Classifying batches</span>
        <span>{pct}%</span>
      </div>
      <div className="h-2 rounded-full bg-[color:var(--color-track)]">
        <div className="h-full rounded-full bg-success transition-all" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
