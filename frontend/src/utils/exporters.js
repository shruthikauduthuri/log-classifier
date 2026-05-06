import jsPDF from "jspdf";

const csvHeaders = ["timestamp", "source", "event_type", "score", "tier", "destination", "reason", "raw"];

export function buildCsv(results) {
  const rows = [csvHeaders.join(",")];
  for (const result of results) {
    rows.push(csvHeaders.map((field) => escapeCsv(result[field] ?? "")).join(","));
  }
  return rows.join("\n");
}

export function downloadCsv(results) {
  const blob = new Blob([buildCsv(results)], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `classified-logs-${Date.now()}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

export function downloadPdfSummary(summary, results) {
  const doc = new jsPDF({ unit: "pt", format: "letter" });
  const margin = 48;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(20);
  doc.text("Log Noise Classifier Summary", margin, 60);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(11);
  doc.text(`Generated: ${new Date().toLocaleString()}`, margin, 84);

  const metrics = [
    ["Logs processed", summary.total],
    ["Sent to SIEM", summary.high_count],
    ["Data Lake", summary.medium_count],
    ["Cold / Archived", summary.low_count],
    ["SIEM reduction", `${summary.siem_savings_pct}%`],
    ["Estimated monthly savings", `$${Number(summary.estimated_monthly_savings || 0).toLocaleString()}`]
  ];

  let y = 130;
  doc.setFont("helvetica", "bold");
  doc.text("Routing Metrics", margin, y);
  y += 24;
  doc.setFont("helvetica", "normal");
  for (const [label, value] of metrics) {
    doc.text(label, margin, y);
    doc.text(String(value), 300, y);
    y += 20;
  }

  y += 18;
  doc.setFont("helvetica", "bold");
  doc.text("Recent Classifications", margin, y);
  y += 24;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  for (const item of results.slice(0, 12)) {
    const line = `${item.tier.padEnd(6)} ${String(item.score).padEnd(5)} ${item.source}: ${item.reason}`;
    doc.text(line.slice(0, 96), margin, y);
    y += 16;
  }

  doc.save(`log-classifier-summary-${Date.now()}.pdf`);
}

function escapeCsv(value) {
  const text = String(value).replaceAll('"', '""');
  return `"${text}"`;
}
