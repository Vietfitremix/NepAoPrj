export async function aiApi<T>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  const r = await fetch('/ai' + path, body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal } : { signal });
  if (!r.ok) {
    const e = await r.json().catch(() => ({} as Record<string, unknown>));
    throw new Error(String(e.message || (e.detail ? JSON.stringify(e.detail) : `Lỗi ${r.status}`)));
  }
  return r.json() as Promise<T>;
}
export async function saveLook(payload: unknown): Promise<string> {
  const r = await fetch('/api/shared-looks', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!r.ok) throw new Error('Không lưu được look. Vui lòng thử lại.');
  return ((await r.json()) as { id: string }).id;
}
export async function loadLook<T>(id: string): Promise<T> {
  const r = await fetch(`/api/shared-looks/${encodeURIComponent(id)}`);
  if (!r.ok) throw new Error('Không tìm thấy look này.');
  return r.json() as Promise<T>;
}
