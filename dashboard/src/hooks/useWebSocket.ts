import { useEffect, useState } from "react";

type CaseUpdate = any;
type Signal = any;

export function useWebSocket() {
  const [cases, setCases] = useState<CaseUpdate[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/dashboard");
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "case_update") {
        setCases((prev) => [message.data, ...prev]);
      } else if (message.type === "new_signal") {
        setSignals((prev) => [message.data, ...prev]);
      }
    };
    return () => ws.close();
  }, []);

  return { cases, signals };
}
