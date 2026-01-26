type Props = { signals: any[] };

export function SignalAlerts({ signals }: Props) {
  return (
    <div>
      <h3>Signal Alerts</h3>
      <ul>
        {signals.map((s, idx) => (
          <li key={idx}>{s?.reasoning || "signal"}</li>
        ))}
      </ul>
    </div>
  );
}
