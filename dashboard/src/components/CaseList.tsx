type Props = { cases: any[] };

export function CaseList({ cases }: Props) {
  return (
    <div>
      <h3>Cases</h3>
      <ul>
        {cases.map((c, idx) => (
          <li key={idx}>{c?.case_id || "case"} - {c?.status || "pending"}</li>
        ))}
      </ul>
    </div>
  );
}
