export type StreamEvent =
  | { type: "token"; text: string }
  | { type: "block"; block: any }
  | { type: "tool"; name: string; status: string }
  | { type: "done"; message_id?: string; block_count?: number; usage?: any }
  | { type: "error"; code: string; message: string; retryable?: boolean; details?: any }
  | { type: "ping" };

export function parseSSEChunk(chunk: string, buffer: string): { events: StreamEvent[], buffer: string } {
  const combined = buffer + chunk;
  const parts = combined.split("\n\n");
  const events: StreamEvent[] = [];

  // The last part is either empty (if chunk ended with \n\n) or a partial event.
  const newBuffer = parts.pop() || "";

  for (const part of parts) {
    if (!part.trim()) continue;
    
    // Heartbeat ping
    if (part.startsWith(": ping")) {
      events.push({ type: "ping" });
      continue;
    }

    const lines = part.split("\n");
    let eventType = "";
    let data = "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        eventType = line.substring("event: ".length).trim();
      } else if (line.startsWith("data: ")) {
        data += line.substring("data: ".length);
      }
    }

    if (eventType && data) {
      try {
        const parsedData = JSON.parse(data);
        if (eventType === "token" || eventType === "block" || eventType === "tool" || eventType === "done" || eventType === "error") {
          events.push({ type: eventType, ...parsedData } as StreamEvent);
        }
      } catch (e) {
        console.error("Failed to parse SSE data", data, e);
      }
    }
  }

  return { events, buffer: newBuffer };
}
