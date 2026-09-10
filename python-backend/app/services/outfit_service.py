"""Structured outfit generation with Claude, plus demo-mode logic."""
from __future__ import annotations

import json
from typing import Optional

from app.config import settings

try:
    from anthropic import Anthropic
except Exception:  # pragma: no cover
    Anthropic = None  # type: ignore


def _pick_colors(profile: Optional[dict]) -> str:
    if profile and profile.get("favorite_colors"):
        return profile["favorite_colors"]
    return "navy, white, and soft beige"


def demo_outfit(data: dict, profile: Optional[dict] = None) -> dict:
    occ = (
        data.get("occasion")
        or (profile or {}).get("preferred_occasions")
        or "casual"
    ).lower()
    colors = data.get("colors") or _pick_colors(profile)

    if any(k in occ for k in ("interview", "formal", "office")):
        return {
            "outfit": "Polished Professional",
            "top": "Crisp white button-down shirt",
            "bottom": "Tailored navy or charcoal trousers",
            "dress": "Alternatively, a structured knee-length sheath dress",
            "shoes": "Clean leather loafers or closed-toe heels",
            "accessories": "Minimal watch, small stud earrings",
            "bag": "Structured neutral tote or slim briefcase",
            "layering": "A tailored blazer for extra polish",
            "styleTip": f"Keep a tidy, low-contrast palette ({colors}). "
            "A neat fit signals confidence.",
        }
    if any(k in occ for k in ("party", "birthday", "date", "function")):
        return {
            "outfit": "Evening Standout",
            "top": "Satin or sequined cami top",
            "bottom": "High-waisted black trousers or a flowy midi skirt",
            "dress": "Alternatively, a wrap dress in a rich jewel tone",
            "shoes": "Strappy heels or sleek ankle boots",
            "accessories": "Statement earrings and a delicate bracelet stack",
            "bag": "Compact clutch in metallic or a bold accent color",
            "layering": "A cropped jacket if the evening cools down",
            "styleTip": f"Let one piece be the star. Metallics lift {colors}.",
        }
    if "travel" in occ:
        return {
            "outfit": "Comfy Traveler",
            "top": "Soft breathable tee or long-sleeve",
            "bottom": "Stretch joggers or relaxed straight-leg jeans",
            "dress": "",
            "shoes": "Cushioned white sneakers",
            "accessories": "Crossbody phone pouch, comfy cap",
            "bag": "Lightweight backpack",
            "layering": "A zip hoodie or packable jacket",
            "styleTip": f"Prioritize layers and stretch fabrics in {colors}.",
        }
    return {
        "outfit": "Smart Casual",
        "top": "White or striped cotton tee",
        "bottom": "Blue slim or straight jeans",
        "dress": "",
        "shoes": "White sneakers",
        "accessories": "Minimal watch and a simple chain",
        "bag": "Neutral crossbody or canvas backpack",
        "layering": "A light overshirt or denim jacket",
        "styleTip": f"Balance relaxed and neat. Works great with {colors}.",
    }


def format_outfit_text(c: dict) -> str:
    lines = [
        f"OUTFIT: {c['outfit']}",
        f"TOP: {c['top']}",
        f"BOTTOM: {c['bottom']}",
    ]
    if c.get("dress"):
        lines.append(f"DRESS/ALT: {c['dress']}")
    lines += [
        f"SHOES: {c['shoes']}",
        f"ACCESSORIES: {c['accessories']}",
        f"BAG: {c['bag']}",
    ]
    if c.get("layering"):
        lines.append(f"LAYERING: {c['layering']}")
    lines.append(f"STYLE TIP: {c['styleTip']}")
    return "\n".join(lines)


def generate_outfit(
    data: dict,
    profile: Optional[dict] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> dict:
    active_key = (api_key or settings.ANTHROPIC_API_KEY or "").strip()
    active_model = model or settings.ANTHROPIC_MODEL

    if not active_key or Anthropic is None:
        return {"outfit": demo_outfit(data, profile), "demo": True}

    from app.services.claude_service import build_system_prompt

    system = (
        build_system_prompt(profile)
        + '\n\nReturn ONLY a JSON object with keys: "outfit", "top", '
        '"bottom", "dress", "shoes", "accessories", "bag", "layering", '
        '"styleTip". No prose outside the JSON.'
    )
    user_msg = (
        f"Occasion: {data.get('occasion') or 'any'}\n"
        f"Weather/Season: {data.get('season') or 'any'}\n"
        f"Style: {data.get('style') or 'any'}\n"
        f"Available clothes: {data.get('clothes') or 'unspecified'}\n"
        f"Preferred colors: {data.get('colors') or 'any'}\n\n"
        "Generate one complete outfit as JSON."
    )
    try:
        client = Anthropic(api_key=active_key)
        resp = client.messages.create(
            model=active_model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = "".join(
            b.text for b in resp.content if b.type == "text"
        )
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            parsed = json.loads(raw[start : end + 1])
            card = demo_outfit(data, profile)
            if "style_tip" in parsed and "styleTip" not in parsed:
                parsed["styleTip"] = parsed["style_tip"]
            card.update({k: str(v) for k, v in parsed.items() if v is not None})
            return {"outfit": card, "demo": False}
        return {"outfit": demo_outfit(data, profile), "demo": True}
    except Exception:
        return {"outfit": demo_outfit(data, profile), "demo": True}
