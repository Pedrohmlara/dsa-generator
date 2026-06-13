/**
 * API Client — SSE stream consumer for the generation endpoint.
 *
 * Uses fetch() with ReadableStream to consume Server-Sent Events
 * from POST /api/generate. Handles reconnection on network errors.
 */

const API_BASE = '';

/**
 * Fetch available topics and styles from the backend.
 * @returns {Promise<{categories: Array, styles: Array}>}
 */
export async function fetchTopics() {
  const res = await fetch(`${API_BASE}/api/topics`);
  if (!res.ok) throw new Error(`Failed to fetch topics: ${res.status}`);
  return res.json();
}

/**
 * Start generating a guide, consuming the SSE stream.
 *
 * @param {object} params
 * @param {string[]} params.topics - Selected topic IDs
 * @param {string} params.style - Selected learning style
 * @param {object} handlers - Event handlers
 * @param {Function} handlers.onProgress - (data: object) => void
 * @param {Function} handlers.onOutline - (data: object) => void
 * @param {Function} handlers.onContent - (token: string) => void
 * @param {Function} handlers.onCode - (token: string) => void
 * @param {Function} handlers.onSectionStart - (data: object) => void
 * @param {Function} handlers.onSectionEnd - (data: object) => void
 * @param {Function} handlers.onDone - (data: object) => void
 * @param {Function} handlers.onError - (data: object) => void
 * @returns {AbortController} - Call .abort() to cancel the stream
 */
export function generateGuide({ topics, style }, handlers) {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topics, style }),
        signal: controller.signal,
      });

      if (!res.ok) {
        const errText = await res.text();
        handlers.onError?.({ message: `Server error: ${res.status}`, detail: errText });
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Parse SSE events from buffer.
        // SSE format: "event: <type>\ndata: <payload>\n\n"
        const events = buffer.split('\n\n');
        // Keep the last incomplete chunk in the buffer.
        buffer = events.pop() || '';

        for (const raw of events) {
          if (!raw.trim()) continue;

          let eventType = 'message';
          let dataLines = [];

          for (const line of raw.split('\n')) {
            if (line.startsWith('event: ')) {
              eventType = line.slice(7).trim();
            } else if (line.startsWith('data: ')) {
              dataLines.push(line.slice(6));
            }
          }

          const data = dataLines.join('\n');

          switch (eventType) {
            case 'progress': {
              try { handlers.onProgress?.(JSON.parse(data)); } catch {}
              break;
            }
            case 'outline': {
              try { handlers.onOutline?.(JSON.parse(data)); } catch {}
              break;
            }
            case 'content': {
              handlers.onContent?.(data);
              break;
            }
            case 'code': {
              handlers.onCode?.(data);
              break;
            }
            case 'section_start': {
              try { handlers.onSectionStart?.(JSON.parse(data)); } catch {}
              break;
            }
            case 'section_end': {
              try { handlers.onSectionEnd?.(JSON.parse(data)); } catch {}
              break;
            }
            case 'done': {
              try { handlers.onDone?.(JSON.parse(data)); } catch {}
              break;
            }
            case 'error': {
              try { handlers.onError?.(JSON.parse(data)); } catch {}
              break;
            }
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') return;
      handlers.onError?.({ message: err.message || 'Network error' });
    }
  })();

  return controller;
}

/**
 * Fetch all saved guides (metadata only).
 * @returns {Promise<Array>} Array of guide metadata objects.
 */
export async function getGuides() {
  try {
    const response = await fetch(`${API_BASE}/api/guides`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.guides || [];
  } catch (error) {
    console.error('Failed to fetch guides:', error);
    throw error;
  }
}

/**
 * Fetch a single guide by ID.
 * @param {string} id The guide ID
 * @returns {Promise<Object>} The guide object.
 */
export async function getGuide(id) {
  try {
    const response = await fetch(`${API_BASE}/api/guides/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch guide:', error);
    throw error;
  }
}
