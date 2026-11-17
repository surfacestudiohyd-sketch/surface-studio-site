/**
 * Surface Studio drawing reader: a Cloudflare Worker.
 *
 * The website's instant quote sends a drawing (PDF or photo) to POST /read-drawing.
 * This worker passes it to Claude with the estimator prompt below and returns the
 * PU panels it finds as JSON, which the website loads into its editable panel table.
 *
 * The Anthropic API key lives only here, as a Worker secret (ANTHROPIC_API_KEY).
 * It is never sent to the browser.
 */

const MODEL = 'claude-sonnet-5-5';            // good balance of accuracy and cost for drawings
const MAX_BYTES = 20 * 1024 * 1024;           // 20 MB per file
const ALLOWED_TYPES = ['application/pdf', 'image/png', 'image/jpeg', 'image/webp'];

export const SYSTEM_PROMPT = `You are an estimator at Surface Studio, a PU paint and polish workshop in Hyderabad.
You read interior drawings (elevations, shop drawings, 3D views with dimensions, hand sketches with sizes)
and list every panel that will receive a PU finish, so the studio can price it.

How the studio prices work:
- Area: length x width of each panel, for each face that gets PU (1 or 2 faces).
- Edges: the full perimeter of each panel, per running foot, normally charged on every PU panel.
- Design work: panels with grooves, V-grooves, profiles, fluting, CNC patterns or mouldings cost 1.5x.

Rules:
1. Report sizes in millimetres. Convert feet and inches exactly (1 in = 25.4 mm, 1 ft = 304.8 mm).
   If a drawing gives no unit, assume millimetres when numbers are mostly 3 to 4 digits.
2. Use only dimensions written on the drawing or clearly derivable from written dimensions
   (for example a total width split into equal shutters). Never guess a size from the picture scale.
   If a panel's size cannot be worked out, leave it out and mention it in notes.
3. Include shutters, drawer fronts, loft shutters, exposed end panels, filler and skirting strips,
   wall panelling and other visible PU surfaces. Exclude glass, mirrors, hardware, appliances,
   countertops, and anything marked as laminate, veneer-with-laminate, or another finish.
4. faces: 2 for shutters and free-standing panels finished on both sides; 1 when the back is
   laminate, against a wall, or hidden inside a carcass.
5. qty: count identical panels together. Split shutters by the number of doors drawn.
6. design: true only when the drawing shows or names grooves, profiles, fluting, CNC or mouldings.
7. edges: true unless the drawing says edges are banded, laminated or not painted.
8. Give each panel a short name with its unit, for example "Wardrobe shutter" or "TV unit back panel".
9. If the file is not a drawing with sizes, return no panels and explain briefly in notes.

Return your answer only by calling the record_panels tool.`;

const TOOL = {
  name: 'record_panels',
  description: 'Record the PU panels found in the drawing.',
  input_schema: {
    type: 'object',
    properties: {
      panels: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            name: { type: 'string', description: 'Short part name with its unit' },
            length_mm: { type: 'number' },
            width_mm: { type: 'number' },
            qty: { type: 'integer', minimum: 1 },
            faces: { type: 'integer', enum: [1, 2] },
            edges: { type: 'boolean' },
            design: { type: 'boolean' },
            confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
          },
          required: ['name', 'length_mm', 'width_mm', 'qty', 'faces', 'edges', 'design'],
        },
      },
      notes: { type: 'string', description: 'Anything unclear, skipped or assumed, in one or two sentences' },
    },
    required: ['panels'],
  },
};

function cors(env, req) {
  const origin = req.headers.get('Origin') || '';
  const allowed = (env.ALLOWED_ORIGINS || 'https://surfacestudio.co.in').split(',').map((s) => s.trim());
  return {
    'Access-Control-Allow-Origin': allowed.includes(origin) ? origin : allowed[0],
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    Vary: 'Origin',
  };
}

function json(body, status, headers) {
  return new Response(JSON.stringify(body), { status, headers: { ...headers, 'Content-Type': 'application/json' } });
}

function toBase64(buf) {
  const bytes = new Uint8Array(buf);
  let bin = '';
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}

export default {
  async fetch(req, env) {
    const h = cors(env, req);
    const url = new URL(req.url);
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: h });
    if (req.method !== 'POST' || url.pathname !== '/read-drawing') return json({ error: 'not found' }, 404, h);

    const origin = req.headers.get('Origin') || '';
    const allowed = (env.ALLOWED_ORIGINS || 'https://surfacestudio.co.in').split(',').map((s) => s.trim());
    if (!allowed.includes(origin)) return json({ error: 'origin not allowed' }, 403, h);

    // Optional abuse guard: Cloudflare rate-limit binding (see wrangler.toml).
    if (env.RATE_LIMITER) {
      const ip = req.headers.get('CF-Connecting-IP') || 'unknown';
      const { success } = await env.RATE_LIMITER.limit({ key: ip });
      if (!success) return json({ error: 'too many drawings from this connection; please wait a few minutes' }, 429, h);
    }

    let file;
    try { file = (await req.formData()).get('file'); } catch { return json({ error: 'send the drawing as form field "file"' }, 400, h); }
    if (!file || typeof file === 'string') return json({ error: 'no file received' }, 400, h);
    if (file.size > MAX_BYTES) return json({ error: 'file is over 20 MB' }, 413, h);
    const type = file.type || (file.name.toLowerCase().endsWith('.pdf') ? 'application/pdf' : '');
    if (!ALLOWED_TYPES.includes(type)) return json({ error: 'only PDF, PNG, JPG or WEBP drawings' }, 415, h);

    const data = toBase64(await file.arrayBuffer());
    const block = type === 'application/pdf'
      ? { type: 'document', source: { type: 'base64', media_type: type, data } }
      : { type: 'image', source: { type: 'base64', media_type: type, data } };

    const api = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: env.MODEL || MODEL,
        max_tokens: 8000,
        system: SYSTEM_PROMPT,
        tools: [TOOL],
        tool_choice: { type: 'tool', name: 'record_panels' },
        messages: [{ role: 'user', content: [block, { type: 'text', text: 'List the PU panels in this drawing.' }] }],
      }),
    });

    if (!api.ok) {
      console.log('anthropic error', api.status, (await api.text()).slice(0, 500));
      return json({ error: 'the drawing could not be read right now; please send it on WhatsApp' }, 502, h);
    }
    const out = await api.json();
    const use = (out.content || []).find((c) => c.type === 'tool_use' && c.name === 'record_panels');
    const result = use ? use.input : { panels: [], notes: 'No panels returned.' };

    // Keep only sane rows.
    const panels = (result.panels || []).filter((p) =>
      p && p.length_mm > 0 && p.width_mm > 0 && p.length_mm < 6000 && p.width_mm < 6000 && p.qty >= 1 && p.qty <= 500
    ).slice(0, 400);

    return json({ panels, notes: String(result.notes || '').slice(0, 500) }, 200, h);
  },
};
