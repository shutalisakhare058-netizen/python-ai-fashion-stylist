"""Claude AI service for StyleMate AI.

Uses the official Anthropic Python SDK when ANTHROPIC_API_KEY is set,
and falls back to a clearly labeled DEMO MODE otherwise.
"""
from __future__ import annotations

from typing import Optional

from app.config import settings
from app.services.outfit_service import demo_outfit, format_outfit_text

try:  # SDK is optional so demo mode works without it installed.
    from anthropic import Anthropic
except Exception:  # pragma: no cover
    Anthropic = None  # type: ignore


def build_system_prompt(profile: Optional[dict] = None) -> str:
    lines = [
        "You are StyleMate AI, a friendly, professional, and encouraging "
        "personal fashion stylist.",
        "",
        "Your job:",
        "- Give practical, wearable outfit recommendations.",
        "- Always consider occasion, weather/season, personal style, and "
        "what clothing the user already owns.",
        "- Suggest tops, bottoms (or dresses), shoes, accessories, bags, and "
        "layering when relevant.",
        "- Explain WHY a combination works.",
        "- Offer color combinations and smart color matching.",
        "- Ask a short clarifying question when key details are missing.",
        "- Keep responses clear, warm, and easy to understand.",
        "- Remember relevant preferences mentioned earlier in this "
        "conversation.",
        "",
        "Hard rules:",
        "- NEVER judge or criticize the user's body, weight, or appearance.",
        "- NEVER promote unhealthy body ideals or dieting.",
        "- Focus only on clothing, styling, comfort, and personal preference.",
        "",
        "When giving a specific outfit, format it clearly with lines like "
        "OUTFIT, TOP, BOTTOM, SHOES, ACCESSORIES, BAG, LAYERING, STYLE TIP.",
    ]
    if profile:
        details = []
        mapping = {
            "name": "Name",
            "style_preferences": "Preferred style",
            "favorite_colors": "Favorite colors",
            "disliked_colors": "Colors to avoid",
            "preferred_occasions": "Preferred occasions",
            "clothing_items": "Clothing they own",
        }
        for key, label in mapping.items():
            val = profile.get(key)
            if val:
                details.append(f"- {label}: {val}")
        if details:
            lines.append("")
            lines.append("The user's saved profile (personalize with it):")
            lines.extend(details)
    return "\n".join(lines)


def _demo_reply(message: str, profile: Optional[dict]) -> str:
    m = (message or "").lower()
    banner = (
        "🎭 DEMO MODE (no ANTHROPIC_API_KEY set) — responses are rule-based.\n\n"
        if settings.demo_mode
        else ""
    )
    if "color" in m and ("beige" in m or "go with" in m):
        return (
            banner
            + "Beige is a versatile neutral. It pairs beautifully with white "
            "& cream, navy or chocolate brown, olive green, and burgundy or "
            "rust for a warm pop.\nSTYLE TIP: Vary textures so a neutral "
            "outfit still feels rich."
        )
    card = demo_outfit({"occasion": message}, profile)
    return banner + format_outfit_text(card) + "\n\nWant me to swap any piece?"


def _sanitize_history(history: list[dict]) -> list[dict]:
    """Ensure history starts with user and alternates strictly between user and assistant."""
    clean: list[dict] = []
    for h in history:
        role = h.get("role", "user")
        content = (h.get("content") or "").strip()
        if not content:
            continue
        if role not in ("user", "assistant"):
            role = "user"
        if clean and clean[-1]["role"] == role:
            clean[-1]["content"] += f"\n\n{content}"
        else:
            clean.append({"role": role, "content": content})
    # Anthropic requires the first message to be from the user
    while clean and clean[0]["role"] != "user":
        clean.pop(0)
    return clean


def get_chat_reply(
    history: list[dict],
    profile: Optional[dict] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> dict:
    """history: list of {"role": "user"|"assistant", "content": str}."""
    system = build_system_prompt(profile)
    active_key = (api_key or settings.ANTHROPIC_API_KEY or "").strip()
    active_model = model or settings.ANTHROPIC_MODEL

    clean_history = _sanitize_history(history)
    last_user = next(
        (h["content"] for h in reversed(clean_history) if h["role"] == "user"),
        "",
    )

    if not active_key or Anthropic is None or not clean_history:
        return {"reply": _demo_reply(last_user, profile), "demo": True}

    try:
        client = Anthropic(api_key=active_key)
        resp = client.messages.create(
            model=active_model,
            max_tokens=1024,
            system=system,
            messages=clean_history,
        )
        text = "".join(
            block.text for block in resp.content if block.type == "text"
        ).strip()
        return {"reply": text or "Sorry, please try again.", "demo": False}
    except Exception:
        return {
            "reply": "⚠️ DEMO MODE (Claude unavailable or API key invalid):\n\n"
            + _demo_reply(last_user, profile),
            "demo": True,
        }
