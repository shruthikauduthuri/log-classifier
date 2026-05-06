import { useCallback, useMemo, useState } from "react";

import { classifyLogsStream } from "../services/api.js";
import { emptySummary, summaryFromResults } from "../utils/metrics.js";

export function useClassify() {
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState(emptySummary());
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [quota, setQuota] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const classify = useCallback(async (payload) => {
    setIsLoading(true);
    setError("");
    setResults([]);
    setSummary(emptySummary());
    setProgress({ current: 0, total: 0 });
    setQuota(null);

    try {
      await classifyLogsStream(payload, (event) => {
        if (event.type === "accepted") {
          setProgress({ current: 0, total: event.batches });
          setQuota(event.quota);
        }
        if (event.type === "batch_complete") {
          setProgress({ current: event.batch, total: event.batches });
          setResults((existing) => [...existing, ...event.results]);
          setSummary(event.summary || summaryFromResults(event.results || []));
        }
        if (event.type === "complete") {
          setProgress((existing) => ({ ...existing, current: existing.total }));
          setResults(event.results);
          setSummary(event.summary);
          setQuota(event.quota);
        }
      });
    } catch (err) {
      const message = err.message || "";
      const isNetworkError = /failed to fetch|load failed|networkerror/i.test(message);
      setError(
        isNetworkError
          ? "Could not reach the Flask API. Start the backend, then make sure VITE_API_BASE_URL or VITE_PROXY_API_TARGET points to that backend port and ALLOWED_ORIGINS includes this frontend URL."
          : message || "Classification failed."
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  const hasResults = results.length > 0;

  return useMemo(
    () => ({
      classify,
      results,
      summary,
      progress,
      quota,
      isLoading,
      error,
      hasResults
    }),
    [classify, results, summary, progress, quota, isLoading, error, hasResults]
  );
}
