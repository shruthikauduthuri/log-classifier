import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: {
    "Content-Type": "application/json"
  }
});

export async function fetchHealth() {
  const response = await api.get("/api/health");
  return response.data;
}

export async function classifyLogs(payload) {
  const response = await api.post("/api/classify", payload);
  return response.data;
}

export async function classifyLogsStream(payload, onEvent) {
  const response = await fetch(`${API_BASE}/api/classify/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok || !response.body) {
    let message = "Classification request failed.";
    try {
      const body = await response.json();
      message = body?.error?.message || message;
    } catch {
      // Keep the sanitized fallback.
    }
    throw new Error(message);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  let streamComplete = false;
  while (!streamComplete) {
    const { value, done } = await reader.read();
    streamComplete = done;
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (!line.trim()) continue;
      const event = JSON.parse(line);
      onEvent(event);
      if (event.type === "error") {
        throw new Error(event.message || "Classification failed.");
      }
    }
  }

  if (buffer.trim()) {
    onEvent(JSON.parse(buffer));
  }
}
