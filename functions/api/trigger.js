// Cloudflare Pages Function — POST /api/trigger
// Fires the Claude Code routine on demand, keeping the secret token server-side.
// Configure two env vars (Cloudflare Pages → Settings → Variables and Secrets):
//   ROUTINE_FIRE_URL  = https://api.anthropic.com/v1/claude_code/routines/<routine_id>/fire
//   ROUTINE_TOKEN     = sk-ant-oat01-...   (mark as a Secret / encrypted)
export async function onRequestPost({ env }) {
  const url = env.ROUTINE_FIRE_URL, token = env.ROUTINE_TOKEN;
  if (!url || !token) {
    return json({ ok: false, error: "Trigger not configured (missing ROUTINE_FIRE_URL / ROUTINE_TOKEN)." }, 501);
  }
  try {
    const r = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "anthropic-beta": "experimental-cc-routine-2026-04-01",
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: "Manual refresh from the dashboard." }),
    });
    const data = await r.json().catch(() => ({}));
    return json({ ok: r.ok, status: r.status, session_url: data.claude_code_session_url || null }, r.ok ? 200 : 502);
  } catch (e) {
    return json({ ok: false, error: String(e) }, 502);
  }
}
// Friendly response for accidental GETs.
export const onRequestGet = () => json({ ok: false, error: "POST to trigger a refresh." }, 405);

function json(obj, status) {
  return new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
}
