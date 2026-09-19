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
    - Fresh dairy (milk, yogurt, soft cheese): 7-10 days
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

  const { image } = req.body || {};
  if (!image) {
    res.status(400).json({ error: 'Missing "image" (base64) in request body', code: 'bad_request' });
    return;
  }

  const imageBytes = Math.round((image.length * 3) / 4);
  console.log(`[analyze] request from ${ip}: image ~${imageBytes} bytes (base64 length ${image.length})`);

  try {
    const model = 'gemini-3.6-flash';
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${process.env.GEMINI_API_KEY}`;

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        system_instruction: { parts: [{ text: AI_SYSTEM_PROMPT }] },
        contents: [{
          role: 'user',
          parts: [
            { text: 'Analyze this photo and return the JSON as instructed.' },
            { inline_data: { mime_type: 'image/jpeg', data: image } },
          ],
        }],
        generationConfig: {
          response_mime_type: 'application/json',
        },
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error(`[analyze] Gemini API error ${response.status}:`, errText);
      res.status(response.status).json({ error: `Gemini API error: ${errText}`, code: 'gemini_error' });
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

    res.status(200).json({ text });
  } catch (err) {
    console.error('[analyze] unexpected error', err);
    res.status(500).json({ error: String(err), code: 'server_error' });
  }
}
