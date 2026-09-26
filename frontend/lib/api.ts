
const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export async function checkBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) throw new Error("Backend health check failed");

  return response.json();
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) throw new Error("Document upload failed");

  return response.json();
}

export async function deleteDocument(documentId: number) {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: "DELETE",
  });

  if (!response.ok) throw new Error("Document deletion failed");

  return response.json().catch(() => null);
}

export async function createConversation(documentId: number) {
  const response = await fetch(
    `${API_BASE_URL}/conversations/${documentId}`,
    {
      method: "POST",
    }
  );

  if (!response.ok) throw new Error("Conversation creation failed");

  return response.json();
}

export async function askQuestion(
  documentId: number,
  conversationId: number,
  question: string
) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}/ask`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        conversation_id: conversationId,
      }),
    }
  );

  if (!response.ok) throw new Error("Question request failed");

  return response.json();
}

export async function getConversationMessages(conversationId: number) {
  const response = await fetch(
    `${API_BASE_URL}/conversations/${conversationId}/messages`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch conversation messages");
  }

  return response.json();
}