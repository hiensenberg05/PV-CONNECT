"use client";

import { useWebSocket } from "../hooks/useWebSocket";

export default function Home() {
  const { cases, signals } = useWebSocket();

  return (
    <main style={{ padding: "24px", fontFamily: "Inter, sans-serif" }}>
      <h1>PV Connect Dashboard</h1>
      <section>
        <h2>New Cases</h2>
        <ul>
          {cases.map((c, idx) => (
            <li key={idx}>{c?.case_id || "case"} - {c?.status || "pending"}</li>
          ))}
        </ul>
      </section>
      <section>
        <h2>Signals</h2>
        <ul>
          {signals.map((s, idx) => (
            <li key={idx}>{s?.risk_level || "signal"}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
