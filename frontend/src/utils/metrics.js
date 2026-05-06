export function emptySummary() {
  return {
    total: 0,
    high_count: 0,
    medium_count: 0,
    low_count: 0,
    siem_savings_pct: 0,
    filtered_count: 0,
    estimated_monthly_savings: 0,
    average_scores: { HIGH: 0, MEDIUM: 0, LOW: 0 }
  };
}

export function summaryFromResults(results) {
  const total = results.length;
  const high = results.filter((item) => item.tier === "HIGH");
  const medium = results.filter((item) => item.tier === "MEDIUM");
  const low = results.filter((item) => item.tier === "LOW");
  const filteredCount = medium.length + low.length;

  return {
    total,
    high_count: high.length,
    medium_count: medium.length,
    low_count: low.length,
    siem_savings_pct: total ? Number(((filteredCount / total) * 100).toFixed(1)) : 0,
    filtered_count: filteredCount,
    estimated_monthly_savings: total ? Number((((filteredCount / total) * 100) / 100 * 12000).toFixed(2)) : 0,
    average_scores: {
      HIGH: averageScore(high),
      MEDIUM: averageScore(medium),
      LOW: averageScore(low)
    }
  };
}

export function buildSourceRows(results) {
  const grouped = new Map();
  for (const result of results) {
    const source = result.source || "Unknown";
    const current = grouped.get(source) || { source, HIGH: 0, MEDIUM: 0, LOW: 0, total: 0 };
    current[result.tier] += 1;
    current.total += 1;
    grouped.set(source, current);
  }
  return Array.from(grouped.values()).sort((a, b) => b.total - a.total);
}

function averageScore(items) {
  if (!items.length) return 0;
  const total = items.reduce((sum, item) => sum + Number(item.score || 0), 0);
  return Number((total / items.length).toFixed(3));
}
