// StyleMate AI — core stylist logic.
// Mirrors the Python `services/claude_service.py`: builds the system prompt,
// calls the Anthropic Claude API when ANTHROPIC_API_KEY is set, and falls back
// to a clearly labeled DEMO MODE otherwise.

export type ChatRole = "user" | "assistant";
export interface ChatTurn {
  role: ChatRole;
  content: string;
}

export interface UserProfile {
  name?: string;
  stylePreferences?: string;
  favoriteColors?: string;
  dislikedColors?: string;
  preferredOccasions?: string;
  clothingItems?: string;
}

export interface OutfitCard {
  outfit: string;
  top: string;
  bottom: string;
  dress?: string;
  shoes: string;
  accessories: string;
  bag: string;
  layering?: string;
  styleTip: string;
}

const MODEL = process.env.ANTHROPIC_MODEL || "claude-3-5-sonnet-20241022";

export function isDemoMode(): boolean {
  return !process.env.ANTHROPIC_API_KEY;
}

export function buildSystemPrompt(profile?: UserProfile): string {
  const lines: string[] = [
    "You are StyleMate AI, a friendly, professional, and encouraging personal fashion stylist.",
    "",
    "Your job:",
    "- Give practical, wearable outfit recommendations.",
    "- Always consider occasion, weather/season, personal style, and what clothing the user already owns.",
    "- Suggest tops, bottoms (or dresses), shoes, accessories, bags, and layering when relevant.",
    "- Explain WHY a combination works (color theory, balance, proportion, formality).",
    "- Offer color combinations and smart color matching.",
    "- Ask a short clarifying question when key details are missing, but still give a helpful suggestion.",
    "- Keep responses clear, warm, and easy to understand.",
    "- Remember relevant preferences mentioned earlier in this conversation.",
    "",
    "Hard rules:",
    "- NEVER judge or criticize the user's body, weight, or appearance.",
    "- NEVER promote unhealthy body ideals or dieting.",
    "- Focus only on clothing, styling, comfort, and personal preference.",
    "",
    "When you give a specific outfit, format it clearly like:",
    "OUTFIT: <name>",
    "TOP: ...",
    "BOTTOM: ...",
    "SHOES: ...",
    "ACCESSORIES: ...",
    "BAG: ...",
    "LAYERING: ... (optional)",
    "STYLE TIP: ...",
  ];

  if (profile) {
    const p: string[] = [];
    if (profile.name) p.push(`Name: ${profile.name}`);
    if (profile.stylePreferences) p.push(`Preferred style: ${profile.stylePreferences}`);
    if (profile.favoriteColors) p.push(`Favorite colors: ${profile.favoriteColors}`);
    if (profile.dislikedColors) p.push(`Colors to avoid: ${profile.dislikedColors}`);
    if (profile.preferredOccasions) p.push(`Preferred occasions: ${profile.preferredOccasions}`);
    if (profile.clothingItems) p.push(`Clothing they own: ${profile.clothingItems}`);
    if (p.length) {
      lines.push("", "The user's saved profile (use it to personalize, but stay flexible):", ...p.map((x) => `- ${x}`));
    }
  }

  return lines.join("\n");
}

// ---- Anthropic API call ----
async function callClaude(
  system: string,
  history: ChatTurn[]
): Promise<string> {
  const apiKey = process.env.ANTHROPIC_API_KEY as string;
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 1024,
      system,
      messages: history.map((m) => ({ role: m.role, content: m.content })),
    }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Claude API error ${res.status}: ${body.slice(0, 300)}`);
  }

  const data = (await res.json()) as {
    content?: Array<{ type: string; text?: string }>;
  };
  const text = (data.content || [])
    .filter((c) => c.type === "text")
    .map((c) => c.text || "")
    .join("\n")
    .trim();
  return text || "Sorry, I couldn't generate a response. Please try again.";
}

// ---- Public: chat ----
export async function getChatReply(
  history: ChatTurn[],
  profile?: UserProfile
): Promise<{ reply: string; demo: boolean }> {
  const system = buildSystemPrompt(profile);
  if (isDemoMode()) {
    const last = [...history].reverse().find((h) => h.role === "user");
    return { reply: demoReply(last?.content || "", profile), demo: true };
  }
  try {
    const reply = await callClaude(system, history);
    return { reply, demo: false };
  } catch {
    const last = [...history].reverse().find((h) => h.role === "user");
    return {
      reply:
        "⚠️ **Demo Mode (Claude unavailable)** — I couldn't reach the AI service, so here's a rule-based suggestion:\n\n" +
        demoReply(last?.content || "", profile),
      demo: true,
    };
  }
}

// ---- Public: structured outfit generation ----
export interface GenerateOutfitInput {
  occasion?: string;
  season?: string;
  style?: string;
  clothes?: string;
  colors?: string;
}

export async function generateOutfit(
  input: GenerateOutfitInput,
  profile?: UserProfile
): Promise<{ outfit: OutfitCard; demo: boolean }> {
  if (isDemoMode()) {
    return { outfit: demoOutfit(input, profile), demo: true };
  }
  const system =
    buildSystemPrompt(profile) +
    '\n\nReturn ONLY a JSON object with these exact keys: "outfit", "top", "bottom", "dress", "shoes", "accessories", "bag", "layering", "styleTip". No markdown, no prose outside the JSON.';
  const userMsg = [
    `Occasion: ${input.occasion || "any"}`,
    `Weather/Season: ${input.season || "any"}`,
    `Style: ${input.style || profile?.stylePreferences || "any"}`,
    `Available clothes: ${input.clothes || profile?.clothingItems || "unspecified"}`,
    `Preferred colors: ${input.colors || profile?.favoriteColors || "any"}`,
    "",
    "Generate one complete outfit as JSON.",
  ].join("\n");

  try {
    const raw = await callClaude(system, [{ role: "user", content: userMsg }]);
    const match = raw.match(/\{[\s\S]*\}/);
    if (!match) throw new Error("no json");
    const parsed = JSON.parse(match[0]) as Partial<OutfitCard>;
    return {
      outfit: {
        outfit: parsed.outfit || "Custom Outfit",
        top: parsed.top || "-",
        bottom: parsed.bottom || "-",
        dress: parsed.dress || "",
        shoes: parsed.shoes || "-",
        accessories: parsed.accessories || "-",
        bag: parsed.bag || "-",
        layering: parsed.layering || "",
        styleTip: parsed.styleTip || "Keep it simple and balanced.",
      },
      demo: false,
    };
  } catch {
    return { outfit: demoOutfit(input, profile), demo: true };
  }
}

// ===================== DEMO MODE =====================

function pickColors(profile?: UserProfile): string {
  if (profile?.favoriteColors) return profile.favoriteColors;
  return "navy, white, and soft beige";
}

function demoOutfit(input: GenerateOutfitInput, profile?: UserProfile): OutfitCard {
  const occ = (input.occasion || profile?.preferredOccasions || "casual").toLowerCase();
  const colors = input.colors || pickColors(profile);

  if (occ.includes("interview") || occ.includes("formal") || occ.includes("office")) {
    return {
      outfit: "Polished Professional",
      top: "Crisp white button-down shirt",
      bottom: "Tailored navy or charcoal trousers",
      dress: "Alternatively, a structured knee-length sheath dress",
      shoes: "Clean leather loafers or closed-toe heels",
      accessories: "Minimal watch, small stud earrings",
      bag: "Structured neutral tote or slim briefcase",
      layering: "A tailored blazer for extra polish",
      styleTip: `Stick to a tidy, low-contrast palette (${colors}). Neat fit signals confidence and competence.`,
    };
  }
  if (occ.includes("party") || occ.includes("birthday") || occ.includes("date") || occ.includes("function")) {
    return {
      outfit: "Evening Standout",
      top: "Satin or sequined cami top",
      bottom: "High-waisted black trousers or a flowy midi skirt",
      dress: "Alternatively, a wrap dress in a rich jewel tone",
      shoes: "Strappy heels or sleek ankle boots",
      accessories: "Statement earrings and a delicate bracelet stack",
      bag: "Compact clutch in metallic or a bold accent color",
      layering: "A cropped jacket if the evening cools down",
      styleTip: `Let one piece be the star and keep the rest simple. Metallic accents lift ${colors}.`,
    };
  }
  if (occ.includes("travel")) {
    return {
      outfit: "Comfy Traveler",
      top: "Soft breathable tee or long-sleeve",
      bottom: "Stretch joggers or relaxed straight-leg jeans",
      dress: "",
      shoes: "Cushioned white sneakers",
      accessories: "Crossbody phone pouch, comfy cap",
      bag: "Lightweight backpack",
      layering: "A zip hoodie or packable jacket for changing temps",
      styleTip: `Prioritize layers and stretch fabrics in easy-to-mix ${colors}.`,
    };
  }
  // default: casual / college
  return {
    outfit: "Smart Casual",
    top: "White or striped cotton tee",
    bottom: "Blue slim or straight jeans",
    dress: "",
    shoes: "White sneakers",
    accessories: "Minimal watch and a simple chain",
    bag: "Neutral crossbody or canvas backpack",
    layering: "A light overshirt or denim jacket",
    styleTip: `Balance relaxed and neat. This easily works with ${colors} for an effortless everyday look.`,
  };
}

export function demoReply(message: string, profile?: UserProfile): string {
  const m = message.toLowerCase();
  const banner = isDemoMode()
    ? "🎭 **DEMO MODE** (no ANTHROPIC_API_KEY set) — responses are rule-based.\n\n"
    : "";

  if (m.includes("color") && (m.includes("beige") || m.includes("go with"))) {
    return (
      banner +
      "Great question! Beige is a versatile neutral. It pairs beautifully with:\n\n" +
      "- **White & cream** for a soft, elegant monochrome look\n" +
      "- **Navy or chocolate brown** for grounded contrast\n" +
      "- **Olive green** for an earthy, modern combo\n" +
      "- **Burgundy or rust** for a warm seasonal pop\n\n" +
      "STYLE TIP: Keep textures interesting (linen, knit, suede) so a neutral outfit still feels rich."
    );
  }

  const card = demoOutfit({ occasion: message }, profile);
  return (
    banner +
    formatOutfitText(card) +
    "\n\nWant me to swap any piece, or dress this up/down? Just ask! 💬"
  );
}

export function formatOutfitText(c: OutfitCard): string {
  const lines = [
    `OUTFIT: ${c.outfit}`,
    `TOP: ${c.top}`,
    `BOTTOM: ${c.bottom}`,
  ];
  if (c.dress) lines.push(`DRESS/ALT: ${c.dress}`);
  lines.push(`SHOES: ${c.shoes}`);
  lines.push(`ACCESSORIES: ${c.accessories}`);
  lines.push(`BAG: ${c.bag}`);
  if (c.layering) lines.push(`LAYERING: ${c.layering}`);
  lines.push(`STYLE TIP: ${c.styleTip}`);
  return lines.join("\n");
}
