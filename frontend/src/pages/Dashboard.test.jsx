import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import Dashboard from "./Dashboard.jsx";

vi.mock("../services/api.js", () => ({
  classifyLogsStream: vi.fn()
}));

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }) => <div>{children}</div>,
  BarChart: ({ children }) => <div>{children}</div>,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  Bar: () => <div />
}));

describe("Dashboard", () => {
  it("renders the tool surface and empty state", () => {
    render(<Dashboard />);
    expect(screen.getAllByText("Log Noise Classifier").length).toBeGreaterThan(0);
    expect(screen.getByText("Awaiting first classification")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Classify logs/i })).toBeDisabled();
  });

  it("disables exports without results", () => {
    render(<Dashboard />);
    expect(screen.getByRole("button", { name: "CSV" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "PDF" })).toBeDisabled();
  });
});
