"""
👗 StyleMate AI — Personal AI Fashion Stylist
Streamlit Application for local and Streamlit Community Cloud deployment.
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ==========================================
# 1. KEY RESOLUTION & AI CLIENT
# ==========================================
def get_api_key() -> str:
    """
    Resolves API key (OpenAI or Anthropic) directly from environment or Streamlit secrets:
    1. Streamlit Secrets (st.secrets["OPENAI_API_KEY"] / st.secrets["ANTHROPIC_API_KEY"])
    2. Environment variables (OPENAI_API_KEY or ANTHROPIC_API_KEY from .env / OS)
    """
    # 1. Streamlit Secrets (for Streamlit Community Cloud)
    try:
        if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
            return str(st.secrets["OPENAI_API_KEY"]).strip()
        if "ANTHROPIC_API_KEY" in st.secrets and st.secrets["ANTHROPIC_API_KEY"]:
            return str(st.secrets["ANTHROPIC_API_KEY"]).strip()
    except Exception:
        pass

    # 2. Environment variables (.env or system)
    env_openai = os.getenv("OPENAI_API_KEY", "").strip()
    if env_openai:
        return env_openai

    env_anthropic = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if env_anthropic:
        return env_anthropic

    return ""


def get_api_provider() -> str:
    """Returns 'openai', 'anthropic', or 'none' based on available key."""
    key = get_api_key()
    if not key:
        return "none"
    if key.startswith("sk-proj") or key.startswith("sk-admin") or (key.startswith("sk-") and not key.startswith("sk-ant")):
        return "openai"
    if key.startswith("sk-ant"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return "anthropic"


def is_demo_mode() -> bool:
    return len(get_api_key()) == 0



# ==========================================
# 2. STYLIST LOGIC & PROMPTS
# ==========================================
def build_system_prompt(profile: Dict[str, Any]) -> str:
    lines = [
        "You are StyleMate AI, a friendly, warm, professional, and encouraging personal fashion stylist.",
        "",
        "Your job:",
        "- Give practical, wearable outfit recommendations.",
        "- Always consider occasion, weather/season, personal style, and clothing the user already owns.",
        "- Suggest tops, bottoms (or dresses), shoes, accessories, bags, and layering when relevant.",
        "- Explain WHY a combination works (color theory, balance, proportion, silhouette).",
        "- Offer smart color combinations and complementary pairings.",
        "- Ask a short clarifying question when key details are missing.",
        "- Keep responses clear, warm, conversational, and easy to understand.",
        "- Remember relevant preferences mentioned earlier in this conversation.",
        "",
        "Hard rules:",
        "- NEVER judge or criticize the user's body, weight, or appearance.",
        "- NEVER promote unhealthy body ideals or dieting.",
        "- Focus only on clothing, styling, comfort, and personal preference.",
        "",
        "When giving a specific outfit recommendation, format it clearly with labels:",
        "OUTFIT: <Name>",
        "TOP: <Top piece>",
        "BOTTOM: <Bottom piece>",
        "DRESS/ALT: <If dress or alternative>",
        "SHOES: <Footwear>",
        "ACCESSORIES: <Jewelry/Watches/Hats>",
        "BAG: <Bag style>",
        "LAYERING: <Jacket/Cardigan/Coat>",
        "STYLE TIP: <Styling advice & why it works>",
    ]
    if profile:
        details = []
        mapping = {
            "name": "Name",
            "style_preferences": "Preferred fashion style",
            "favorite_colors": "Favorite colors",
            "disliked_colors": "Colors to avoid",
            "preferred_occasions": "Preferred occasions",
            "clothing_items": "Clothes already owned",
        }
        for k, label in mapping.items():
            val = profile.get(k)
            if val:
                details.append(f"- {label}: {val}")
        if details:
            lines.append("")
            lines.append("User's Personal Style Profile (use to personalize):")
            lines.extend(details)
    return "\n".join(lines)


def rule_based_demo_reply(message: str, profile: Dict[str, Any]) -> str:
    m = (message or "").lower()
    
    # Check if user is asking specifically about API key
    if any(w in m for w in ("api key", "key", "anthropic", "openai", "claude key", "which api")):
        return (
            "### 🔑 API Key Status for StyleMate AI\n\n"
            "StyleMate AI automatically detects and uses your API key directly from your `.env` file or environment variables!\n\n"
            "- **Supported Providers**: OpenAI (`OPENAI_API_KEY`) and Anthropic (`ANTHROPIC_API_KEY`).\n"
            "- **Configuration**: Simply add your key in your `.env` file (e.g. `OPENAI_API_KEY=sk-...` or `ANTHROPIC_API_KEY=sk-ant-...`).\n"
            "- **Dashboard Input Removed**: You no longer need to enter an API key manually in the app sidebar—it remains active automatically whenever the app starts!\n"
        )

    fav_colors = profile.get("favorite_colors") or "navy, cream, and olive"

    if any(w in m for w in ("color", "match", "pair", "beige", "palette")):
        return (
            "### 🎨 Color Styling Advice\n"
            "Neutral tones like beige, ivory, and taupe create effortless elegance. "
            "They pair wonderfully with **navy, chocolate brown, sage green**, or a pop of **terracotta**.\n\n"
            f"- **For your palette ({fav_colors}):** Try matching a crisp cream top with dark bottoms for a slimming, high-contrast look.\n"
            "- **Texture Tip:** When mixing neutrals, vary textures (e.g. chunky knit + tailored linen or denim) so the look stays interesting!\n"
        )

    outfit = rule_based_demo_outfit({"occasion": message}, profile)
    return (
        f"### 👗 {outfit['outfit']}\n"
        f"- **👕 Top:** {outfit['top']}\n"
        f"- **👖 Bottom:** {outfit['bottom']}\n"
        + (f"- **👗 Dress / Alt:** {outfit['dress']}\n" if outfit.get("dress") else "")
        + f"- **👟 Shoes:** {outfit['shoes']}\n"
        + f"- **⌚ Accessories:** {outfit['accessories']}\n"
        + f"- **👜 Bag:** {outfit['bag']}\n"
        + (f"- **🧥 Layering:** {outfit['layering']}\n" if outfit.get("layering") else "")
        + f"\n> 💡 **Style Tip:** {outfit['styleTip']}\n"
    )



def rule_based_demo_outfit(data: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, str]:
    occ_raw = data.get("occasion") or profile.get("preferred_occasions") or "casual"
    occ = occ_raw.lower()
    colors = data.get("colors") or profile.get("favorite_colors") or "navy, white, and soft camel"
    aesthetic = data.get("style") or profile.get("style_preferences") or "smart casual"

    # 1. Ganesh Chaturthi / Ganesh Utsav / Puja
    if any(k in occ for k in ("ganesh", "ganpati", "vinayaka", "chaturthi", "utsav")):
        return {
            "outfit": f"Vibrant Festive Traditional Look ({occ_raw.title()})",
            "top": "Silk or Fine Cotton Kurta in Marigold Yellow, Warm Orange, or Crimson Red",
            "bottom": "Comfortable Silk Churidar, Dhoti Pants, or Pleated Palazzo",
            "dress": "Embellished Chanderi Kurti Set with Zari Dupatta Drape",
            "shoes": "Handcrafted Tan Kolhapuri Sandals or Embellished Mojaris",
            "accessories": "Temple Gold Jewelry, Minimal Brass Bangles, & fresh Mogra (Jasmine) hair accents",
            "bag": "Embroidered Potli Bag or Small Silk Sling",
            "layering": "Jacquard Silk Nehru Jacket or Contrast Zari Dupatta",
            "styleTip": "Ganesh Chaturthi celebrates vibrant, auspicious colors (yellow, orange, gold, red). Opt for breathable festive silks to stay comfortable during Aarti and Visarjan celebrations.",
        }

    # 2. Navratri / Garba / Dandiya Nights
    elif any(k in occ for k in ("navratri", "garba", "dandiya", "durga puja", "pandal")):
        return {
            "outfit": f"High-Energy Garba & Dandiya Look ({occ_raw.title()})",
            "top": "Mirror-Work Choli or Embroidered Kediyu / Kurta with Gota Patti details",
            "bottom": "Multi-Flared (80-Kali) Chaniya Choli or Patiala / Dhoti Pants",
            "dress": "Vibrant Bandhani or Leheriya Print Lehenga Choli Set",
            "shoes": "Cushioned Embellished Juttis or Flat Mojaris (built for Garba dancing!)",
            "accessories": "Heavy Oxidized Silver Necklace, Stacked Ghungroo Bangles, Maangtikka, & Mirror Kamarbandh",
            "bag": "Kutch Embroidered Mirror-work Potli",
            "layering": "Vibrant Contrast Bandhani Dupatta pinned securely for dancing",
            "styleTip": "Navratri styling is all about movement, oxidized silver jewelry, and mirror-work. Ensure your outfit is lightweight enough to dance Garba freely all night!",
        }

    # 3. Diwali / Deepavali / Laxmi Puja
    elif any(k in occ for k in ("diwali", "deepavali", "laxmi puja", "lakshmi puja", "dhanteras")):
        return {
            "outfit": f"Royal Festive Elegance for Diwali ({occ_raw.title()})",
            "top": "Raw Silk Kurta or Brocade Blouse in Royal Blue, Emerald Green, or Deep Crimson",
            "bottom": "Zari-Border Silk Lehenga, Flared Sharara, or Tailored Silk Pyjama",
            "dress": "Kanjeevaram / Banarasi Silk Saree or Floor-Length Anarkali Suit",
            "shoes": "Velvet Embellished Mojaris or Metallic Block Heels",
            "accessories": "Kundan or Polki Statement Neckpiece, Gold Jhumkas, & Statement Rings",
            "bag": "Zardozi Clutch or Velvet Structured Potli",
            "layering": "Heavy Brocade Nehru Jacket or Rich Organza Tissue Dupatta",
            "styleTip": "Diwali calls for rich, luminous textures (Banarasi, Brocade, Raw Silk) and warm metallic jewelry that catch the festive diya lights!",
        }

    # 4. Eid / Ramadan / Festive Feast
    elif any(k in occ for k in ("eid", "ramadan", "ramzan", "iftar")):
        return {
            "outfit": f"Refined Festive Grace for Eid ({occ_raw.title()})",
            "top": "Fine Lucknowi Chikankari Kurta or Embellished Anarkali Top",
            "bottom": "Flared Sharara, Gharara, or Straight Silk Trousers",
            "dress": "Floor-Length Chikankari Anarkali with Gota Patti Dupatta",
            "shoes": "Embellished Kolhapuri Slippers or Metallic Heel Sandals",
            "accessories": "Passa / Jhumar, Statement Chaandbalis, and Pearl Bangles",
            "bag": "Silk Embroidered Clutch",
            "layering": "Sheer Net or Organza Dupatta with Zari Borders",
            "styleTip": "Pastel tones (mint green, ivory, blush pink, sky blue) with intricate Chikankari or Zardozi work bring timeless elegance for Eid gatherings.",
        }

    # 5. Wedding / Gala / Formal Reception / Black Tie
    elif any(k in occ for k in ("wedding", "gala", "reception", "festive", "traditional", "black tie", "ceremony")):
        return {
            "outfit": f"Sophisticated Celebration Look ({occ_raw.title()})",
            "top": "Silk wrap blouse, embellished bodice, or Kurta set",
            "bottom": "Tailored wide-leg fluid trousers, Silk Lehenga, or Dhoti",
            "dress": "Elegant floor-length Saree or Cowl Evening Dress",
            "shoes": "Sleek metallic heels or polished leather dress shoes",
            "accessories": "Statement drop earrings or Polki necklace",
            "bag": "Structured satin or metallic clutch",
            "layering": "Tailored velvet tuxedo blazer or tissue silk shawl",
            "styleTip": f"Formal celebrations call for elevated fabrics (satin, silk, velvet). Complement nicely with {colors}.",
        }

    # 2. Beach / Resort / Summer Vacation
    elif any(k in occ for k in ("beach", "resort", "pool", "summer", "vacation", "cruise", "tropical")):
        return {
            "outfit": f"Breezy Resort Chic ({occ_raw.title()})",
            "top": "Breathable linen button-down shirt or ribbed tank top",
            "bottom": "Relaxed linen drawstring trousers or tailored denim shorts",
            "dress": "Tiered cotton maxi sun dress in a warm tone",
            "shoes": "Woven leather slides or comfortable espadrille sandals",
            "accessories": "Wide-brim straw hat, polarized tortoiseshell sunglasses, gold layered chain",
            "bag": "Woven raffia tote or canvas beach bag",
            "layering": "Lightweight unbuttoned linen overshirt",
            "styleTip": f"Prioritize breathable natural fibers (linen, cotton) in light tones ({colors}) to stay cool and stylish.",
        }
    # 3. Gym / Workout / Activewear / Sports
    elif any(k in occ for k in ("gym", "workout", "fitness", "active", "run", "sport", "yoga", "athletic")):
        return {
            "outfit": f"Performance Activewear ({occ_raw.title()})",
            "top": "Moisture-wicking seamless athletic tee or tank",
            "bottom": "High-waisted compression leggings or lightweight running shorts",
            "dress": "",
            "shoes": "Cushioned road-running or cross-training sneakers",
            "accessories": "Fitness smartwatch, breathable sweat-wicking cap, insulated water bottle",
            "bag": "Compact gym duffel or sport sling backpack",
            "layering": "Full-zip performance track jacket or fleece hoodie",
            "styleTip": "Match your top and bottom colors for a sleek, monochromatic activewear silhouette.",
        }
    # 4. Funeral / Memorial / Solemn
    elif any(k in occ for k in ("funeral", "memorial", "solemn", "sympathy", "condolence")):
        return {
            "outfit": f"Respectful Classic Attire ({occ_raw.title()})",
            "top": "Modest black or dark navy high-neck blouse or dress shirt",
            "bottom": "Tailored black straight-leg trousers",
            "dress": "Knee-length conservative black midi dress",
            "shoes": "Matte black leather pumps or polished dark loafers",
            "accessories": "Subtle pearl studs or minimal matte silver watch",
            "bag": "Simple black leather shoulder bag",
            "layering": "Tailored dark trench coat or structured dark blazer",
            "styleTip": "Keep silhouettes classic, coverage modest, and accessories minimal and matte.",
        }
    # 5. Job Interview / Formal Corporate
    elif any(k in occ for k in ("interview", "formal", "office", "work", "corporate", "presentation", "meeting")):
        return {
            "outfit": f"Polished Executive ({occ_raw.title()})",
            "top": "Crisp white button-down or silk-blend blouse",
            "bottom": "Tailored charcoal or navy straight-leg trousers",
            "dress": "Structured knee-length sheath dress as an alternative",
            "shoes": "Clean leather pointed-toe loafers or block heels",
            "accessories": "Minimal gold watch and subtle pearl or bar studs",
            "bag": "Structured neutral laptop tote or slim leather briefcase",
            "layering": "Tailored single-breasted blazer",
            "styleTip": f"Keep the palette tidy and intentional ({colors}). A well-fitting shoulder seam signals authority.",
        }
    # 6. Party / Evening / Cocktail / Dinner Date / Birthday
    elif any(k in occ for k in ("party", "birthday", "date", "dinner", "evening", "cocktail", "club", "night out")):
        return {
            "outfit": f"Evening Allure ({occ_raw.title()})",
            "top": "Satin cowl-neck camisole or structured velvet top",
            "bottom": "High-waisted tailored trousers or a bias-cut satin midi skirt",
            "dress": "Classic wrap dress in a rich jewel tone",
            "shoes": "Strappy block heels or sleek pointed ankle boots",
            "accessories": "Chunky gold hoop earrings and a delicate layered necklace",
            "bag": "Structured mini crossbody or metallic envelope clutch",
            "layering": "Cropped vegan leather jacket or tailored trench coat",
            "styleTip": f"Let one statement piece shine. Metallics and rich jewel tones harmonize beautifully with {colors}.",
        }
    # 7. Travel / Flight / Airport
    elif any(k in occ for k in ("travel", "flight", "airport", "vacation", "trip", "road trip")):
        return {
            "outfit": f"Chic Jetsetter ({occ_raw.title()})",
            "top": "Soft breathable oversized cotton tee or ribbed henley",
            "bottom": "Tailored stretch ponte joggers or relaxed straight-leg denim",
            "dress": "",
            "shoes": "Cushioned clean white slip-on sneakers",
            "accessories": "Polarized sunglasses and a slim crossbody phone sling",
            "bag": "Durable nylon weekender tote or sleek ergonomic daypack",
            "layering": "Cashmere blend wrap cardigan or packable utility jacket",
            "styleTip": f"Layering is essential for changing temperatures. Stick with soft stretch fabrics in {colors}.",
        }
    # 8. College / Campus / University
    elif any(k in occ for k in ("college", "university", "campus", "study", "class", "school")):
        return {
            "outfit": f"Campus Smart Casual ({occ_raw.title()})",
            "top": "Vintage wash graphic tee or relaxed crewneck knit",
            "bottom": "Classic mid-rise straight denim jeans",
            "dress": "",
            "shoes": "Retro lifestyle sneakers (e.g. New Balance or Sambas)",
            "accessories": "Canvas tote, stainless steel water bottle, silver rings",
            "bag": "Canvas messenger bag or ergonomic daypack",
            "layering": "Corduroy overshirt or oversized denim jacket",
            "styleTip": f"Effortless comfort meets put-together style. Complement with {colors}.",
        }
    # 9. Outdoor / Hiking / Camping
    elif any(k in occ for k in ("hiking", "outdoor", "camping", "trail", "trekking", "nature")):
        return {
            "outfit": f"Outdoor Explorer ({occ_raw.title()})",
            "top": "Quick-dry synthetic baselayer shirt or long-sleeve merino top",
            "bottom": "Durable stretch cargo trekking pants or trail shorts",
            "dress": "",
            "shoes": "Vibram-soled trail runners or sturdy waterproof hiking boots",
            "accessories": "UV protection sun hat, polarized sunglasses, trail hydration pack",
            "bag": "Lightweight 20L daypack with hip belt",
            "layering": "Windproof fleece jacket or packable rain shell",
            "styleTip": "Dressing in functional layers protects against weather shifts while keeping you comfortable.",
        }
    # 10. Brunch / Coffee / Casual Outing
    elif any(k in occ for k in ("brunch", "coffee", "lunch", "shopping", "weekend", "casual", "picnic")):
        return {
            "outfit": f"Relaxed Brunch Chic ({occ_raw.title()})",
            "top": "Ribbed square-neck knit top or relaxed linen shirt",
            "bottom": "High-waisted wide-leg trousers or light-wash straight jeans",
            "dress": "Casual shirt dress knotted at the waist",
            "shoes": "Minimalist leather slides or clean white retro sneakers",
            "accessories": "Tortoiseshell sunglasses and delicate hoop earrings",
            "bag": "Structured crescent leather shoulder bag",
            "layering": "Lightweight cotton cardigan draped over shoulders",
            "styleTip": f"Balance relaxed fits with one structured piece (like a sleek leather bag). Perfect with {colors}.",
        }
    # 11. Generic / Custom Occasion Dynamic Generator
    else:
        capitalized_occ = occ_raw.strip().title() if occ_raw else "Special Occasion"
        return {
            "outfit": f"Tailored Look for {capitalized_occ}",
            "top": f"Tailored shirt or refined blouse fitting the aesthetic ({aesthetic})",
            "bottom": "Versatile slim or straight trousers suited to the venue",
            "dress": f"Optionally, a classic midi dress tailored for {occ_raw}",
            "shoes": "Comfortable leather loafers, clean dress sneakers, or ankle boots",
            "accessories": "Minimalist watch, gold/silver chain, and sun specs",
            "bag": "Functional structured tote or slim crossbody bag",
            "layering": "A sharp blazer or lightweight jacket appropriate for the weather",
            "styleTip": f"For {occ_raw}, focus on confidence and fit. Incorporating palette tones like {colors} creates a seamless look.",
        }


def call_ai_chat(messages: List[Dict[str, str]], profile: Dict[str, Any], api_key: str, model: str) -> str:
    """Call OpenAI or Anthropic API for chat conversation based on environment API key."""
    if not api_key:
        api_key = get_api_key()

    provider = get_api_provider()

    clean_msgs: List[Dict[str, str]] = []
    for m in messages:
        role = m.get("role", "user")
        content = (m.get("content") or "").strip()
        if not content:
            continue
        if role not in ("user", "assistant"):
            role = "user"
        if clean_msgs and clean_msgs[-1]["role"] == role:
            clean_msgs[-1]["content"] += f"\n\n{content}"
        else:
            clean_msgs.append({"role": role, "content": content})

    while clean_msgs and clean_msgs[0]["role"] != "user":
        clean_msgs.pop(0)

    if not clean_msgs:
        return "Please send a message to start our styling session!"

    # 1. Try OpenAI if provider is openai or key starts with sk- (and not sk-ant)
    if provider == "openai" or (api_key and api_key.startswith("sk-") and not api_key.startswith("sk-ant")):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            model_name = model if "gpt" in model else "gpt-4o"
            oai_messages = [{"role": "system", "content": build_system_prompt(profile)}] + clean_msgs
            resp = client.chat.completions.create(
                model=model_name,
                messages=oai_messages,
                max_tokens=1024,
            )
            text = (resp.choices[0].message.content or "").strip()
            if text:
                return text
        except Exception:
            pass

    # 2. Try Anthropic if provider is anthropic or key starts with sk-ant
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        model_name = model if "claude" in model else "claude-3-5-sonnet-20241022"
        response = client.messages.create(
            model=model_name,
            max_tokens=1024,
            system=build_system_prompt(profile),
            messages=clean_msgs,
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        if text:
            return text
    except Exception:
        pass

    # 3. Fallback to rule-based response
    return rule_based_demo_reply(clean_msgs[-1]["content"], profile)


def call_ai_outfit(data: Dict[str, Any], profile: Dict[str, Any], api_key: str, model: str) -> Dict[str, str]:
    """Call OpenAI or Anthropic API to generate a structured outfit JSON."""
    if not api_key:
        api_key = get_api_key()

    provider = get_api_provider()

    system = (
        build_system_prompt(profile)
        + '\n\nReturn ONLY a valid JSON object with exact keys: "outfit", "top", "bottom", '
        '"dress", "shoes", "accessories", "bag", "layering", "styleTip". '
        'Ensure the values are helpful, specific fashion descriptions. Do not include markdown or text outside JSON.'
    )
    user_prompt = (
        f"Occasion: {data.get('occasion') or 'any'}\n"
        f"Season/Weather: {data.get('season') or 'any'}\n"
        f"Style/Aesthetic: {data.get('style') or 'any'}\n"
        f"Clothes available: {data.get('clothes') or 'unspecified'}\n"
        f"Preferred colors: {data.get('colors') or 'any'}\n\n"
        "Generate one complete, cohesive outfit recommendation as JSON."
    )

    # 1. Try OpenAI
    if provider == "openai" or (api_key and api_key.startswith("sk-") and not api_key.startswith("sk-ant")):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            model_name = model if "gpt" in model else "gpt-4o"
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content or ""
            parsed = json.loads(raw)
            base = rule_based_demo_outfit(data, profile)
            if "style_tip" in parsed and "styleTip" not in parsed:
                parsed["styleTip"] = parsed["style_tip"]
            base.update({k: str(v) for k, v in parsed.items() if v is not None})
            return base
        except Exception:
            pass

    # 2. Try Anthropic
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        model_name = model if "claude" in model else "claude-3-5-sonnet-20241022"
        resp = client.messages.create(
            model=model_name,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = "".join(b.text for b in resp.content if b.type == "text")
        s = raw.find("{")
        e = raw.rfind("}")
        if s != -1 and e != -1:
            parsed = json.loads(raw[s : e + 1])
            base = rule_based_demo_outfit(data, profile)
            if "style_tip" in parsed and "styleTip" not in parsed:
                parsed["styleTip"] = parsed["style_tip"]
            base.update({k: str(v) for k, v in parsed.items() if v is not None})
            return base
    except Exception:
        pass

    return rule_based_demo_outfit(data, profile)


# Alias backward-compatible function names
call_claude_chat = call_ai_chat
call_claude_outfit = call_ai_outfit



# ==========================================
# 3. MAIN UI APPLICATION
# ==========================================
def main():
    st.set_page_config(
        page_title="StyleMate AI — Your Personal Fashion Stylist",
        page_icon="👗",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        .hero-banner {
            background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 50%, #fecdd3 100%);
            border: 1px solid #f43f5e33;
            border-radius: 16px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(225, 29, 72, 0.05);
        }
        .hero-title {
            color: #9f1239;
            font-size: 2.1rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }
        .hero-subtitle {
            color: #881337;
            font-size: 1.05rem;
            margin: 0;
            opacity: 0.9;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }
        .status-live {
            background-color: #ecfdf5;
            color: #065f46;
            border: 1px solid #a7f3d0;
        }
        .status-demo {
            background-color: #fffbeb;
            color: #92400e;
            border: 1px solid #fde68a;
        }
        .outfit-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 5px solid #e11d48;
            border-radius: 14px;
            padding: 1.4rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
            transition: transform 0.15s ease;
        }
        .outfit-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        }
        .outfit-name {
            color: #0f172a;
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }
        .item-row {
            display: flex;
            align-items: baseline;
            gap: 0.6rem;
            font-size: 0.95rem;
            margin-bottom: 0.45rem;
            color: #334155;
        }
        .item-label {
            font-weight: 700;
            color: #475569;
            min-width: 95px;
        }
        .style-tip-box {
            background: #fff1f2;
            border: 1px dashed #f43f5e;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin-top: 0.8rem;
            color: #9f1239;
            font-size: 0.92rem;
            line-height: 1.45;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # State initialization
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "👋 Hi there! I'm **StyleMate AI**, your personal fashion stylist.\n\n"
                "Tell me about an occasion you're dressing for, the weather, your aesthetic, "
                "or what clothes you have in your closet. You can also pick a quick prompt below!",
            }
        ]

    if "saved_outfits" not in st.session_state:
        st.session_state.saved_outfits = [
            {
                "id": 1,
                "name": "Smart Casual Friday",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "outfit": {
                    "outfit": "Smart Casual Friday",
                    "top": "Crisp white linen button-down shirt",
                    "bottom": "Tailored dark wash straight jeans",
                    "dress": "",
                    "shoes": "Minimalist white leather sneakers",
                    "accessories": "Cognac leather watch, matte silver bracelet",
                    "bag": "Structured leather tote in tan",
                    "layering": "Navy unlined cotton blazer",
                    "styleTip": "Roll the blazer sleeves once to show the white shirt cuff for effortless nonchalance.",
                },
            }
        ]

    if "profile" not in st.session_state:
        st.session_state.profile = {
            "name": "Guest Stylist",
            "style_preferences": "Smart casual, minimalist, relaxed chic",
            "favorite_colors": "Navy, cream, sage green, camel",
            "disliked_colors": "Neon green, bright orange",
            "preferred_occasions": "Weekend outings, dinner dates, casual office",
            "clothing_items": "White sneakers, trench coat, dark wash jeans, black blazer, linen shirts",
        }

    # Sidebar
    with st.sidebar:
        st.markdown("### 👗 StyleMate AI")
        st.caption("AI-Powered Personal Fashion Stylist")
        st.markdown("---")

        st.markdown("#### 🔑 AI Engine Configuration")
        active_key = get_api_key()
        provider = get_api_provider()

        if active_key:
            provider_label = "OpenAI" if provider == "openai" else "Claude"
            st.markdown(
                f'<div class="status-badge status-live">🟢 {provider_label} AI Active (.env)</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-badge status-live">🟢 Environment API Key Active</div>',
                unsafe_allow_html=True,
            )

        model_choice = st.selectbox(
            "AI Model",
            options=["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
            index=0,
            help="Select the AI model to generate outfit recommendations.",
        )

        st.markdown("---")
        st.markdown("#### 👤 Current Profile")
        st.text(f"Styling for: {st.session_state.profile.get('name', 'Guest')}")
        st.text(f"Colors: {st.session_state.profile.get('favorite_colors', 'None set')[:25]}...")
        st.caption("Customize your full profile in the **User Profile** tab.")

        st.markdown("---")
        st.markdown(
            """
            **🚀 API Key Info:**
            - **Auto Active**: Automatically loaded from your `.env` file (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`).
            - **Dashboard Input Removed**: Key input option removed from sidebar UI.
            """
        )


    # Hero
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-title">👗 StyleMate AI</div>
            <p class="hero-subtitle">Your personal AI stylist for outfit recommendations, smart color pairing, and wardrobe planning.</p>
            {"<span class='status-badge status-live'>🟢 Live Claude AI Mode</span>" if active_key else "<span class='status-badge status-demo'>🎭 Demo Mode (No API key needed)</span>"}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tabs
    tab_chat, tab_generator, tab_wardrobe, tab_profile = st.tabs(
        ["💬 Stylist Chat", "✨ Outfit Generator", "💾 Saved Looks", "👤 Style Profile"]
    )

    # TAB 1: Chat
    with tab_chat:
        col_chat, col_quick = st.columns([3.2, 1.2])

        with col_quick:
            st.markdown("##### ⚡ Quick Prompts")
            quick_prompts = [
                ("🪔 Ganesh Chaturthi", "What traditional outfit should I wear for Ganesh Chaturthi puja?"),
                ("💃 Navratri Garba", "Suggest a vibrant, comfortable outfit for Navratri Garba night."),
                ("✨ Diwali Festival", "What should I wear for Diwali celebration and Laxmi Puja?"),
                ("🌙 Eid Festive", "Suggest an elegant traditional outfit for Eid celebration."),
                ("🎓 College Outfit", "What should I wear to college tomorrow?"),
                ("💼 Job Interview", "I need a polished outfit for a corporate job interview."),
                ("🎉 Birthday Party", "Suggest a stylish, standout outfit for an evening birthday party."),
                ("✈️ Travel Look", "What should I wear for a long flight and travel day?"),
                ("✨ Dinner Date", "Help me style a classy and confident dinner date outfit."),
                ("🏖️ Beach Vacation", "What outfit should I wear for a beach resort vacation?"),
                ("🎨 Color Matching", "What colors pair best with beige and navy?"),
            ]


            for label, prompt_text in quick_prompts:
                if st.button(label, use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": prompt_text})
                    active_k = get_api_key()
                    if not active_k:
                        reply = rule_based_demo_reply(prompt_text, st.session_state.profile)
                    else:
                        reply = call_claude_chat(
                            st.session_state.chat_history,
                            st.session_state.profile,
                            active_k,
                            model_choice,
                        )
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    st.rerun()

            st.markdown("---")
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.chat_history = [
                    {
                        "role": "assistant",
                        "content": "Chat cleared! How can I help you style your next look?",
                    }
                ]
                st.rerun()

        with col_chat:
            st.markdown("##### 💬 Conversation")
            for msg in st.session_state.chat_history:
                role = msg["role"]
                with st.chat_message(role, avatar="👗" if role == "assistant" else "👤"):
                    st.markdown(msg["content"])

            user_msg = st.chat_input("Ask StyleMate anything (e.g. 'What shoes match olive trousers?')...")
            if user_msg:
                st.session_state.chat_history.append({"role": "user", "content": user_msg})
                with st.chat_message("user", avatar="👤"):
                    st.markdown(user_msg)

                with st.chat_message("assistant", avatar="👗"):
                    with st.spinner("Styling your look..."):
                        active_k = get_api_key()
                        if not active_k:
                            bot_reply = rule_based_demo_reply(user_msg, st.session_state.profile)
                        else:
                            bot_reply = call_claude_chat(
                                st.session_state.chat_history,
                                st.session_state.profile,
                                active_k,
                                model_choice,
                            )
                        st.markdown(bot_reply)

                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                st.rerun()

    # TAB 2: Outfit Generator
    with tab_generator:
        st.markdown("### ✨ Structured Outfit Generator")
        st.caption("Tell us about your event and preferences to generate a tailored look with full piece breakdown.")

        with st.form("outfit_generator_form"):
            col1, col2 = st.columns(2)
            with col1:
                occasion_input = st.selectbox(
                    "Occasion",
                    options=[
                        "Ganesh Chaturthi / Festive Puja",
                        "Navratri / Garba Night",
                        "Diwali / Deepavali Celebration",
                        "Eid Celebration",
                        "Casual Weekend",
                        "Job Interview / Formal Office",
                        "Evening Party / Dinner Date",
                        "Long Travel / Flight",
                        "College / Campus",
                        "Wedding Guest / Reception",
                        "Custom",
                    ],

                )
                if occasion_input == "Custom":
                    custom_occasion = st.text_input("Specify occasion", placeholder="e.g. Gallery opening night")
                    occasion_val = custom_occasion or "Custom Event"
                else:
                    occasion_val = occasion_input

                season_input = st.selectbox(
                    "Season / Weather",
                    options=["Pleasant / Mild", "Summer / Warm", "Autumn / Fall", "Winter / Cold", "Monsoon / Rainy"],
                )

            with col2:
                style_input = st.selectbox(
                    "Preferred Aesthetic",
                    options=[
                        "Smart Casual",
                        "Minimalist & Clean",
                        "Classic & Elegant",
                        "Streetwear & Trendy",
                        "Bohemian & Relaxed",
                        "Athleisure",
                    ],
                )

                colors_input = st.text_input(
                    "Preferred Colors",
                    value=st.session_state.profile.get("favorite_colors", "Navy, white, cream"),
                    help="Enter colors you want to incorporate",
                )

            clothes_input = st.text_area(
                "Clothes You Own to Incorporate (Optional)",
                value=st.session_state.profile.get("clothing_items", ""),
                placeholder="e.g. Tan trench coat, white Stan Smith sneakers, dark wash Levi's jeans",
            )

            submit_gen = st.form_submit_button("✨ Generate Outfit", use_container_width=True, type="primary")

        if submit_gen:
            with st.spinner("Curating your custom outfit..."):
                req_data = {
                    "occasion": occasion_val,
                    "season": season_input,
                    "style": style_input,
                    "colors": colors_input,
                    "clothes": clothes_input,
                }
                active_k = get_api_key()
                if not active_k:
                    outfit_result = rule_based_demo_outfit(req_data, st.session_state.profile)
                else:
                    outfit_result = call_claude_outfit(req_data, st.session_state.profile, active_k, model_choice)

                st.session_state["latest_generated_outfit"] = outfit_result

        if "latest_generated_outfit" in st.session_state:
            out = st.session_state["latest_generated_outfit"]
            st.markdown("---")
            st.markdown(f"#### 🎯 Your Curated Look: **{out.get('outfit', 'Curated Outfit')}**")

            st.markdown(
                f"""
                <div class="outfit-card">
                    <div class="outfit-name">✨ {out.get('outfit', 'Curated Outfit')}</div>
                    <div class="item-row"><span class="item-label">👕 Top:</span> <span>{out.get('top', 'N/A')}</span></div>
                    <div class="item-row"><span class="item-label">👖 Bottom:</span> <span>{out.get('bottom', 'N/A')}</span></div>
                    {f"<div class='item-row'><span class='item-label'>👗 Dress/Alt:</span> <span>{out['dress']}</span></div>" if out.get('dress') else ""}
                    <div class="item-row"><span class="item-label">👟 Shoes:</span> <span>{out.get('shoes', 'N/A')}</span></div>
                    <div class="item-row"><span class="item-label">⌚ Accessories:</span> <span>{out.get('accessories', 'N/A')}</span></div>
                    <div class="item-row"><span class="item-label">👜 Bag:</span> <span>{out.get('bag', 'N/A')}</span></div>
                    {f"<div class='item-row'><span class='item-label'>🧥 Layering:</span> <span>{out['layering']}</span></div>" if out.get('layering') else ""}
                    <div class="style-tip-box">
                        💡 <b>Stylist Tip:</b> {out.get('styleTip', 'Balance proportions and wear with confidence.')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_save1, col_save2 = st.columns([1, 3])
            with col_save1:
                if st.button("💾 Save to My Looks", use_container_width=True, type="primary"):
                    new_id = (
                        max([o["id"] for o in st.session_state.saved_outfits], default=0) + 1
                    )
                    st.session_state.saved_outfits.append(
                        {
                            "id": new_id,
                            "name": out.get("outfit", f"Look #{new_id}"),
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "outfit": out,
                        }
                    )
                    st.success("Outfit saved to your looks! Check the **Saved Looks** tab.")

    # TAB 3: Saved Looks
    with tab_wardrobe:
        st.markdown("### 💾 Your Saved Outfits")
        st.caption("Manage and revisit your favorite looks.")

        if not st.session_state.saved_outfits:
            st.info("No outfits saved yet. Use the **Outfit Generator** to design and save your favorite styles!")
        else:
            for idx, saved in enumerate(reversed(st.session_state.saved_outfits)):
                o = saved["outfit"]
                oid = saved["id"]

                with st.expander(f"✨ {saved['name']} — (Saved on {saved.get('created_at', 'recently')})", expanded=(idx == 0)):
                    st.markdown(
                        f"""
                        <div class="outfit-card" style="margin-bottom: 0.5rem;">
                            <div class="item-row"><span class="item-label">👕 Top:</span> <span>{o.get('top', 'N/A')}</span></div>
                            <div class="item-row"><span class="item-label">👖 Bottom:</span> <span>{o.get('bottom', 'N/A')}</span></div>
                            {f"<div class='item-row'><span class='item-label'>👗 Dress/Alt:</span> <span>{o['dress']}</span></div>" if o.get('dress') else ""}
                            <div class="item-row"><span class="item-label">👟 Shoes:</span> <span>{o.get('shoes', 'N/A')}</span></div>
                            <div class="item-row"><span class="item-label">⌚ Accessories:</span> <span>{o.get('accessories', 'N/A')}</span></div>
                            <div class="item-row"><span class="item-label">👜 Bag:</span> <span>{o.get('bag', 'N/A')}</span></div>
                            {f"<div class='item-row'><span class='item-label'>🧥 Layering:</span> <span>{o['layering']}</span></div>" if o.get('layering') else ""}
                            <div class="style-tip-box">
                                💡 <b>Stylist Tip:</b> {o.get('styleTip', '')}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    del_col, _ = st.columns([1, 4])
                    with del_col:
                        if st.button(f"🗑️ Delete", key=f"del_{oid}", use_container_width=True):
                            st.session_state.saved_outfits = [
                                item for item in st.session_state.saved_outfits if item["id"] != oid
                            ]
                            st.rerun()

    # TAB 4: User Profile
    with tab_profile:
        st.markdown("### 👤 Your Style Profile")
        st.caption("Personalize your preferences so StyleMate AI customizes every outfit to your tastes.")

        with st.form("profile_form"):
            p_name = st.text_input("Your Name", value=st.session_state.profile.get("name", "Guest"))
            p_style = st.text_input(
                "Preferred Fashion Style",
                value=st.session_state.profile.get("style_preferences", ""),
                placeholder="e.g. Minimalist, Classic French, Streetwear, Smart Casual",
            )
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                p_fav_colors = st.text_input(
                    "Favorite Colors",
                    value=st.session_state.profile.get("favorite_colors", ""),
                    placeholder="e.g. Navy, ivory, olive green, blush pink",
                )
            with col_c2:
                p_dislike_colors = st.text_input(
                    "Colors You Don't Prefer",
                    value=st.session_state.profile.get("disliked_colors", ""),
                    placeholder="e.g. Neon yellow, orange",
                )

            p_occasions = st.text_input(
                "Preferred / Common Occasions",
                value=st.session_state.profile.get("preferred_occasions", ""),
                placeholder="e.g. College classes, hybrid office, weekend social events",
            )

            p_clothes = st.text_area(
                "Clothes in Your Wardrobe",
                value=st.session_state.profile.get("clothing_items", ""),
                placeholder="e.g. Navy tailored blazer, black Chelsea boots, white linen shirts, dark wash Levi's 501s",
            )

            save_profile_btn = st.form_submit_button("💾 Save Profile", use_container_width=True, type="primary")

        if save_profile_btn:
            st.session_state.profile = {
                "name": p_name,
                "style_preferences": p_style,
                "favorite_colors": p_fav_colors,
                "disliked_colors": p_dislike_colors,
                "preferred_occasions": p_occasions,
                "clothing_items": p_clothes,
            }
            st.success("Style Profile updated successfully! Future styling recommendations will use these preferences.")


if __name__ == "__main__":
    main()
