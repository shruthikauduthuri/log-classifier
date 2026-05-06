export const SOURCE_OPTIONS = ["Firewall", "Auth", "Syslog", "DNS", "App", "Network", "Unknown"];

export const TIER_META = {
  HIGH: {
    label: "SIEM",
    destination: "SIEM",
    className: "bg-high text-white",
    borderClass: "border-high",
    textClass: "text-high",
    range: "score >= high"
  },
  MEDIUM: {
    label: "Data Lake",
    destination: "DataLake",
    className: "bg-medium text-white",
    borderClass: "border-medium",
    textClass: "text-medium",
    range: "medium <= score < high"
  },
  LOW: {
    label: "Cold / Archived",
    destination: "ColdStorage",
    className: "bg-low text-[color:var(--color-brand)]",
    borderClass: "border-low",
    textClass: "text-muted",
    range: "score < medium"
  }
};

export const MAX_CLIENT_FILE_BYTES = 5 * 1024 * 1024;
