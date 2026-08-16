const API_BASE = import.meta.env.VITE_API_URL || "";

export interface Thread {
  id: string;
  title: string;
  created_at: string;
}

export interface Memory {
  id: string;
  content: string;
  category: string;
  saved_at: string;
}

export interface StreamEvent {
  node?: string;
  type: string;
  content?: string;
  tool_calls?: { name: string; args: Record<string, unknown> }[];
}

export async function createThread(title: string): Promise<Thread> {
  const res = await fetch(`${API_BASE}/api/threads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  return res.json();
}

export async function listThreads(): Promise<Thread[]> {
  const res = await fetch(`${API_BASE}/api/threads`);
  return res.json();
}

export async function listMemories(): Promise<Memory[]> {
  const res = await fetch(`${API_BASE}/api/memories`);
  return res.json();
}

export async function saveMemory(
  content: string,
  category: string
): Promise<Memory> {
  const res = await fetch(`${API_BASE}/api/memories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, category }),
  });
  return res.json();
}

export interface HistoryMessage {
  role: "user" | "assistant" | "tool";
  content: string;
  node?: string;
  tool_calls?: { name: string; args: Record<string, unknown> }[];
}

export async function getThreadMessages(
  threadId: string
): Promise<HistoryMessage[]> {
  const res = await fetch(`${API_BASE}/api/threads/${threadId}/messages`);
  if (!res.ok) return [];
  return res.json();
}

export async function deleteThread(threadId: string): Promise<void> {
  await fetch(`${API_BASE}/api/threads/${threadId}`, { method: "DELETE" });
}

export async function renameThread(
  threadId: string,
  title: string
): Promise<Thread> {
  const res = await fetch(`${API_BASE}/api/threads/${threadId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  return res.json();
}

export async function deleteMemory(contentSubstring: string): Promise<void> {
  await fetch(
    `${API_BASE}/api/memories/${encodeURIComponent(contentSubstring)}`,
    { method: "DELETE" }
  );
}

export async function* streamChat(
  message: string,
  threadId: string
): AsyncGenerator<StreamEvent> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId }),
  });

  if (!res.ok) {
    const errBody = await res.text();
    let detail = `Server error (${res.status})`;
    try {
      const parsed = JSON.parse(errBody);
      detail = parsed.detail || detail;
    } catch {
      if (errBody) detail = errBody;
    }
    throw new Error(detail);
  }

  if (!res.body) throw new Error("No response body");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith("data: ")) {
        try {
          const event: StreamEvent = JSON.parse(trimmed.slice(6));
          yield event;
        } catch {
          // skip malformed events
        }
      }
    }
  }
}
