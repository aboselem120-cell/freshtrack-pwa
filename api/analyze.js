// Vercel Serverless Function — acts as a secure proxy to the Google Gemini API.
// The real API key lives only here (server-side, as an environment variable),
// never in the browser code, so it can't be stolen by inspecting the page.
//
// Uses Gemini because it has a genuine free tier (no credit card, no
// expiration) via Google AI Studio — good for prototyping without cost.

import { isRateLimited, clientIp } from './_rateLimit.js';

const RATE_LIMIT = 20; // requests per IP per hour
const RATE_WINDOW_MS = 60 * 60 * 1000;

const AI_SYSTEM_PROMPT = `You are a grocery item recognition assistant. You will be shown a photo — either a single product (package, jar, produce item) or a store receipt listing multiple items.

Identify every distinct food/grocery item clearly visible or listed. Ignore non-food items. For each item return:
- name: short common product name, in English, Arabic, and Spanish
- category: exactly one of "dairy", "meat", "produce", "bakery", "pantry" (pick the closest fit)
- expiry_date: ONLY if an expiry/best-before/"use by" date is printed directly on THAT item's own packaging and is clearly legible. Return it as "YYYY-MM-DD". Otherwise null.

  If the expiry date is printed in dot-matrix, embossed, laser-etched, or any
  low-contrast/hard-to-read font style where individual digits could be
  confused with each other (e.g., distinguishing 3 vs 8, 1 vs 7, 0 vs 8, 5 vs
  6 is genuinely uncertain), do NOT guess — treat it as unreadable and return
  expiry_date null with estimated_days instead. Only return expiry_date when
  you are highly confident in EVERY individual digit. A wrong date with false
  confidence is worse than an honest estimate — never fabricate or guess at
  unclear digits.
- estimated_days: only when expiry_date is null — your best CONSERVATIVE integer
  estimate, in days, of remaining shelf life for THIS item as purchased today (not
  fresh off the production line — assume a few days have already passed in
  transport and on-shelf time before purchase).

  Be specific to the actual product shown, not a generic category default:
  - Distinguish sub-types whenever visible: fresh/pasteurized refrigerated milk vs
    UHT/long-life (shelf-stable) milk; fresh raw meat/poultry/fish vs frozen;
    refrigerated leafy/soft produce vs firmer, less perishable produce (potatoes,
    onions, squash); refrigerated eggs vs shelf-stable pantry items.
  - When uncertain between a shorter and a longer plausible estimate, ALWAYS pick
    the shorter one. It is far better to warn the user a few days too early than
    to have an item spoil before the app warns them.
  - Typical conservative reference ranges for a freshly purchased item (adjust
    down further if the photo shows the package is already open or heavily
    handled):
    - Fresh liquid/spoonable dairy (milk, drinking yogurt, spoonable yogurt): 7-10 days
    - Commercially packaged soft cheese with a sealed tub/wrap and a recent pack
      date (cottage cheese, cream cheese, ricotta, labneh): 14-21 days unopened;
      7-10 days once opened
    - UHT/shelf-stable dairy, unopened: 30-90 days (5-7 days once opened)
    - Eggs: 14-18 days
    - Fresh raw meat/poultry/fish: 2-4 days
    - Frozen meat/poultry/fish: much longer, but still favor the conservative end
    - Fresh leafy/soft produce (herbs, berries, leafy greens): 3-5 days
    - Firmer produce (potatoes, onions, carrots, squash): 14-21 days
    - Bakery (bread, pastries): 4-7 days
    - Shelf-stable pantry (canned goods, dry pasta, rice): 180-365 days
  These ranges are reference points, not hard rules — use the specific product
  visible in the photo to pick the most realistic and conservative number in or
  near the appropriate range.

CRITICAL — receipts do not print per-item expiry dates:
A store receipt's printed date (near the top or bottom, often next to a time, terminal number, or "thank you" line) is the TRANSACTION/PURCHASE date, not an expiry date for any item. NEVER copy a receipt's transaction date into any item's expiry_date field. When scanning a receipt (a list of item names with prices, no individual packaging visible), expiry_date must be null for every item — always use estimated_days instead. Only set expiry_date when you can see an individual product's actual packaging with a date printed on it (a single jar/carton/package photo, not a printed receipt).

Respond with ONLY valid JSON, no markdown fences, no commentary, in exactly this shape:
{"items":[{"name":{"en":"...","ar":"...","es":"..."},"category":"...","expiry_date":"YYYY-MM-DD"|null,"estimated_days":N|null}]}

If you cannot confidently identify any grocery item in the photo, respond with {"items":[]}.`;

// Groq is a free fallback used only after Gemini exhausts all retry attempts
// (repeated 503 overload or a timeout on every attempt) — see GROQ_API_KEY.
// Groq's /v1/models endpoint has no field indicating vision/image support, so
// this list is the source of truth for which model IDs are known to accept
// images (checked against Groq's docs as of 2026-09-21). Update it if Groq
// changes its vision-capable lineup.
const GROQ_VISION_MODEL_ALLOWLIST = [
  'qwen/qwen3.8-27b',
  'openai/gpt-oss-120b',
  'openai/gpt-oss-20b',
];

function buildUserInstructionText(imageList) {
  if (imageList.length > 1) {
    return `These ${imageList.length} photos show the SAME single grocery item, photographed from ` +
      `different angles (e.g. front and back, or top and bottom) specifically to find a printed ` +
      `expiry date not visible in the first photo. Treat them as ONE item — return exactly one ` +
      `entry in "items", not ${imageList.length}. Look across ALL the photos for a printed ` +
      `expiry/best-before/use-by date; if found in any of them, use it. If genuinely not visible ` +
      `in any, return expiry_date null and use estimated_days as usual.`;
  }
  return 'Analyze this photo and return the JSON as instructed.';
}

async function pickGroqVisionModel() {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);
  try {
    const res = await fetch('https://api.groq.com/openai/v1/models', {
      headers: { Authorization: `Bearer ${process.env.GROQ_API_KEY}` },
      signal: controller.signal,
    });
    if (!res.ok) return null;
    const data = await res.json();
    const availableIds = new Set((data.data || []).filter((m) => m.active !== false).map((m) => m.id));
    return GROQ_VISION_MODEL_ALLOWLIST.find((id) => availableIds.has(id)) || null;
  } catch {
    return null;
  } finally {
    clearTimeout(timeoutId);
  }
}

async function analyzeWithGroq(imageList) {
  const model = await pickGroqVisionModel();
  if (!model) return null; // no known vision-capable model available on this account

  const content = [{ type: 'text', text: buildUserInstructionText(imageList) }];
  imageList.forEach((img) => content.push({
    type: 'image_url',
    image_url: { url: `data:image/jpeg;base64,${img}` },
  }));

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 25000);
  try {
    const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${process.env.GROQ_API_KEY}` },
      body: JSON.stringify({
        model,
        messages: [
          { role: 'system', content: AI_SYSTEM_PROMPT },
          { role: 'user', content },
        ],
        response_format: { type: 'json_object' },
      }),
      signal: controller.signal,
    });
    if (!res.ok) throw new Error(`Groq API error ${res.status}: ${await res.text()}`);
    const data = await res.json();
    const text = data?.choices?.[0]?.message?.content || '';
    if (!text) throw new Error('Groq returned an empty response');
    return { text, model };
  } finally {
    clearTimeout(timeoutId);
  }
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const ip = clientIp(req);
  if (isRateLimited(ip, RATE_LIMIT, RATE_WINDOW_MS)) {
    console.warn(`[analyze] rate limit hit for ${ip}`);
    res.status(429).json({ error: 'Too many requests. Please try again later.', code: 'rate_limited' });
    return;
  }

  if (!process.env.GEMINI_API_KEY) {
    res.status(500).json({
      error: 'Server is missing GEMINI_API_KEY. Get a free key at aistudio.google.com, add it in your Vercel project settings under Environment Variables, then redeploy.',
      code: 'missing_api_key',
    });
    return;
  }

  const { image, images } = req.body || {};
  const imageList = Array.isArray(images) ? images : (image ? [image] : []);
  if (imageList.length === 0) {
    res.status(400).json({ error: 'Missing "image" or "images" (base64) in request body', code: 'bad_request' });
    return;
  }

  const totalBytes = imageList.reduce((sum, img) => sum + Math.round((img.length * 3) / 4), 0);
  console.log(`[analyze] request from ${ip}: ${imageList.length} image(s), ~${totalBytes} bytes total`);

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  try {
    const model = 'gemini-3.6-flash';
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${process.env.GEMINI_API_KEY}`;

    const userParts = [{ text: buildUserInstructionText(imageList) }];
    imageList.forEach((img) => userParts.push({ inline_data: { mime_type: 'image/jpeg', data: img } }));

    const requestBody = JSON.stringify({
      system_instruction: { parts: [{ text: AI_SYSTEM_PROMPT }] },
      contents: [{ role: 'user', parts: userParts }],
      generationConfig: {
        response_mime_type: 'application/json',
      },
    });

    // Gemini occasionally returns 503 ("model overloaded") under high demand,
    // or sometimes hangs entirely without responding — both are transient,
    // not a bug in our code, so retry a couple of times with backoff. Each
    // attempt gets its own timeout so a hung attempt can't stall the whole
    // request indefinitely; the caller (index.html) waits longer than the
    // worst case of all attempts combined so it never gives up first.
    const MAX_ATTEMPTS = 3;
    const BACKOFF_MS = [1000, 2000];
    const ATTEMPT_TIMEOUT_MS = 25000;
    let response = null;
    let lastErrText = '';
    let timedOut = false;

    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), ATTEMPT_TIMEOUT_MS);

      try {
        response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: requestBody,
          signal: controller.signal,
        });
        timedOut = false;
      } catch (err) {
        clearTimeout(timeoutId);
        if (err.name !== 'AbortError') throw err; // genuine network error — handled by the outer catch
        console.warn(`[analyze] Gemini attempt ${attempt}/${MAX_ATTEMPTS} timed out after ${ATTEMPT_TIMEOUT_MS}ms`);
        response = null;
        timedOut = true;
        if (attempt < MAX_ATTEMPTS) await sleep(BACKOFF_MS[attempt - 1]);
        continue;
      }
      clearTimeout(timeoutId);

      if (response.ok) break;

      lastErrText = await response.text();
      if (response.status !== 503) break; // not a transient overload — don't retry

      console.warn(`[analyze] Gemini 503 (overloaded), attempt ${attempt}/${MAX_ATTEMPTS}`);
      if (attempt < MAX_ATTEMPTS) await sleep(BACKOFF_MS[attempt - 1]);
    }

    const geminiRetryableFailure = timedOut || (!response.ok && response.status === 503);

    if (geminiRetryableFailure && process.env.GROQ_API_KEY) {
      console.warn(`[analyze] Gemini exhausted retries (${timedOut ? 'timeout' : '503 overloaded'}); trying Groq fallback`);
      const groqResult = await analyzeWithGroq(imageList).catch((err) => {
        console.error('[analyze] Groq fallback failed', err);
        return null;
      });
      if (groqResult) {
        console.error(`[analyze] provider used: groq (model ${groqResult.model}, fallback after Gemini failure)`);
        res.status(200).json({ text: groqResult.text });
        return;
      }
      console.error('[analyze] Groq fallback unavailable — returning original Gemini error');
    }

    if (timedOut) {
      console.error('[analyze] Gemini did not respond within the timeout on every attempt');
      res.status(504).json({ error: 'Gemini did not respond in time. Please try again.', code: 'timeout' });
      return;
    }

    if (!response.ok) {
      if (response.status === 503) {
        console.error('[analyze] Gemini still overloaded after retries:', lastErrText);
        res.status(503).json({ error: 'Gemini is currently overloaded. Please try again in a minute.', code: 'busy' });
        return;
      }
      console.error(`[analyze] Gemini API error ${response.status}:`, lastErrText);
      res.status(response.status).json({ error: `Gemini API error: ${lastErrText}`, code: 'gemini_error' });
      return;
    }

    const data = await response.json();
    const blockReason = data?.promptFeedback?.blockReason;
    const candidate = data?.candidates?.[0];
    const text = candidate?.content?.parts?.[0]?.text || '';

    if (!text) {
      console.error('[analyze] empty response from Gemini', {
        blockReason,
        finishReason: candidate?.finishReason,
        promptFeedback: data?.promptFeedback,
      });
      res.status(502).json({
        error: blockReason
          ? `Gemini blocked the response (reason: ${blockReason})`
          : 'Gemini returned an empty response',
        code: blockReason ? 'blocked' : 'empty_response',
      });
      return;
    }

    console.error('[analyze] provider used: gemini');
    res.status(200).json({ text });
  } catch (err) {
    console.error('[analyze] unexpected error', err);
    res.status(500).json({ error: String(err), code: 'server_error' });
  }
}
