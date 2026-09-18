// Vercel Serverless Function — acts as a secure proxy to the Google Gemini API.
// The real API key lives only here (server-side, as an environment variable),
// never in the browser code, so it can't be stolen by inspecting the page.
//
// Uses Gemini because it has a genuine free tier (no credit card, no
// expiration) via Google AI Studio — good for prototyping without cost.

const AI_SYSTEM_PROMPT = `You are a grocery item recognition assistant. You will be shown a photo — either a single product (package, jar, produce item) or a store receipt listing multiple items.

Identify every distinct food/grocery item clearly visible or listed. Ignore non-food items. For each item return:
- name: short common product name, in English, Arabic, and Spanish
- category: exactly one of "dairy", "meat", "produce", "bakery", "pantry" (pick the closest fit)
- expiry_date: ONLY if an expiry/best-before/"use by" date is printed directly on THAT item's own packaging and is clearly legible. Return it as "YYYY-MM-DD". Otherwise null.
- estimated_days: only when expiry_date is null — a reasonable integer estimate of typical remaining shelf life in days for a freshly bought item of this type. Otherwise null.

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

  if (!process.env.GEMINI_API_KEY) {
    res.status(500).json({
      error: 'Server is missing GEMINI_API_KEY. Get a free key at aistudio.google.com, add it in your Vercel project settings under Environment Variables, then redeploy.'
    });
    return;
  }

  const { image } = req.body || {};
  if (!image) {
    res.status(400).json({ error: 'Missing "image" (base64) in request body' });
    return;
  }

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
      res.status(response.status).json({ error: `Gemini API error: ${errText}` });
      return;
    }

    const data = await response.json();
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
    res.status(200).json({ text });
  } catch (err) {
    res.status(500).json({ error: String(err) });
  }
}
