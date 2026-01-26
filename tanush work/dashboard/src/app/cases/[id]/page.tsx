type Params = { params: { id: string } };

export default function CasePage({ params }: Params) {
  return (
    <main style={{ padding: "24px", fontFamily: "Inter, sans-serif" }}>
      <h1>Case {params.id}</h1>
      <p>Detail view placeholder.</p>
    </main>
  );
}
