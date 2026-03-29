const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

export async function uploadFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  
  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });
  
  if (!res.ok) throw new Error("File upload failed");
  return res.json();
}

export async function sendChat(query: string, currentState?: any) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_query: query, current_state: currentState }),
  });
  
  if (!res.ok) throw new Error("Chat sequence failed");
  return res.json();
}

export async function calculateWhatIf(params: {
  monthly_income: number;
  monthly_expense: number;
  current_corpus: number;
  age: number;
  extra_sip?: number;
  retire_early_years?: number;
}) {
  const queryParams = new URLSearchParams(params as any).toString();
  const res = await fetch(`${BASE_URL}/calculate?${queryParams}`);
  
  if (!res.ok) throw new Error("Calculation failed");
  return res.json();
}
