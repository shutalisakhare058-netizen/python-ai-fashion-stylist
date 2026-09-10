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
# 1. KEY RESOLUTION & ANTHROPIC CLIENT
# ==========================================
def get_api_key() -> str:
    """
    Resolves Anthropic API key in priority order:
    1. UI Sidebar input (session state)
    2. Streamlit Cloud secrets (st.secrets["ANTHROPIC_API_KEY"])
    3. Environment variable (ANTHROPIC_API_KEY from .env / OS)
    """
    # 1. UI override
    try:
        if st.session_state.get("user_api_key"):
            return st.session_state["user_api_key"].strip()
    except Exception:
        pass

    # 2. Streamlit Secrets (for Streamlit Community Cloud)
    try:
        if "ANTHROPIC_API_KEY" in st.secrets and st.secrets["ANTHROPIC_API_KEY"]:
            return str(st.secrets["ANTHROPIC_API_KEY"]).strip()
    except Exception:
        pass

    # 3. Environment variable
    env_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if env_key:
        return env_key

    return ""


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
    banner = "🎭 **DEMO MODE (Rule-based stylist active)**\n\n*Add your Anthropic API key in the sidebar for live Claude AI answers!*\n\n"

    fav_colors = profile.get("favorite_colors") or "navy, cream, and olive"

    if any(w in m for w in ("color", "match", "pair", "beige")):
        return (
            banner
            + f"### 🎨 Color Styling Advice\n"
            + f"Neutral tones like beige, ivory, and taupe create effortless elegance. "
            + f"They pair wonderfully with **navy, chocolate brown, sage green**, or a pop of **terracotta**.\n\n"
            + f"- **For your palette ({fav_colors}):** Try matching a crisp cream top with dark bottoms for a slimming, high-contrast look.\n"
            + f"- **Texture Tip:** When mixing neutrals, vary textures (e.g. chunky knit + tailored linen or denim) so the look stays interesting!"
        )

    outfit = rule_based_demo_outfit({"occasion": message}, profile)
    return (
        banner
        + f"### 👗 {outfit['outfit']}\n"
        + f"- **👕 Top:** {outfit['top']}\n"
        + f"- **👖 Bottom:** {outfit['bottom']}\n"
        + (f"- **👗 Dress / Alt:** {outfit['dress']}\n" if outfit.get("dress") else "")
        + f"- **👟 Shoes:** {outfit['shoes']}\n"
        + f"- **⌚ Accessories:** {outfit['accessories']}\n"
        + f"- **👜 Bag:** {outfit['bag']}\n"
        + (f"- **🧥 Layering:** {outfit['layering']}\n" if outfit.get("layering") else "")
        + f"\n> 💡 **Style Tip:** {outfit['styleTip']}\n\n"
        + "*Would you like me to tweak any of these pieces or tailor it for different weather?*"
    )


def rule_based_demo_outfit(data: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, str]:
    occ = (
        data.get("occasion")
        or profile.get("preferred_occasions")
        or "casual"
    ).lower()
    colors = data.get("colors") or profile.get("favorite_colors") or "navy, white, and soft camel"

    if any(k in occ for k in ("interview", "formal", "office", "work", "corporate")):
        return {
            "outfit": "Polished Executive",
            "top": "Crisp white button-down or silk-blend blouse",
            "bottom": "Tailored charcoal or navy straight-leg trousers",
            "dress": "Structured knee-length sheath dress as an alternative",
            "shoes": "Clean leather pointed-toe loafers or block heels",
            "accessories": "Minimal gold watch and subtle pearl or bar studs",
            "bag": "Structured neutral laptop tote or slim leather briefcase",
            "layering": "Tailored single-breasted blazer",
            "styleTip": f"Keep the palette tidy and intentional ({colors}). A well-fitting shoulder seam signals authority.",
        }
    elif any(k in occ for k in ("party", "birthday", "date", "dinner", "evening", "cocktail")):
        return {
            "outfit": "Evening Allure",
            "top": "Satin cowl-neck camisole or structured velvet top",
            "bottom": "High-waisted tailored trousers or a bias-cut satin midi skirt",
            "dress": "Classic wrap dress in a rich jewel tone",
            "shoes": "Strappy block heels or sleek pointed ankle boots",
            "accessories": "Chunky gold hoop earrings and a delicate layered necklace",
            "bag": "Structured mini crossbody or metallic envelope clutch",
            "layering": "Cropped vegan leather jacket or tailored trench",
            "styleTip": f"Let one statement piece shine. Metallics and rich jewel tones harmonize beautifully with {colors}.",
        }
    elif any(k in occ for k in ("travel", "flight", "airport", "vacation")):
        return {
            "outfit": "Chic Jetsetter",
            "top": "Soft breathable oversized cotton tee or ribbed henley",
            "bottom": "Tailored stretch ponte joggers or relaxed straight-leg denim",
            "dress": "",
            "shoes": "Cushioned clean white sneakers",
            "accessories": "Polarized sunglasses and a slim crossbody phone sling",
            "bag": "Durable nylon weekender tote or sleek backpack",
            "layering": "Cashmere blend wrap cardigan or packable utility jacket",
            "styleTip": f"Layering is essential for changing cabin temperatures. Stick with soft stretch fabrics in {colors}.",
        }
    elif any(k in occ for k in ("college", "university", "campus", "study")):
        return {
            "outfit": "Campus Smart Casual",
            "top": "Vintage wash graphic tee or relaxed crewneck knit",
            "bottom": "Classic mid-rise straight denim jeans",
            "dress": "",
            "shoes": "Retro lifestyle sneakers (e.g. New Balance or Sambas)",
            "accessories": "Canvas tote, stainless steel water bottle, silver rings",
            "bag": "Canvas messenger or ergonomic daypack",
            "layering": "Corduroy overshirt or oversized denim jacket",
            "styleTip": f"Effortless comfort meets put-together style. Complement with {colors}.",
        }
    else:
        return {
            "outfit": "Effortless Smart Casual",
            "top": "High-neck ribbed tee or relaxed linen button-down",
            "bottom": "High-waisted wide-leg trousers or clean-wash jeans",
            "dress": "",
            "shoes": "Minimalist white sneakers or leather slides",
            "accessories": "Simple chain necklace and chic tortoiseshell sunglasses",
            "bag": "Structured crescent shoulder bag or woven tote",
            "layering": "Lightweight knit cardigan draped over the shoulders",
            "styleTip": f"Play with proportions: a fitted top balances a wide-leg bottom. Works wonders with {colors}.",
        }


def call_claude_chat(messages: List[Dict[str, str]], profile: Dict[str, Any], api_key: str, model: str) -> str:
    """Call Anthropic Claude API for chat conversation."""
    try:
        from anthropic import Anthropic
    except ImportError:
        return "⚠️ Anthropic package not installed. Running in Demo Mode.\n\n" + rule_based_demo_reply(messages[-1]["content"], profile)

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

    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=build_system_prompt(profile),
            messages=clean_msgs,
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        return text or "I couldn't put together a reply just now. Could you rephrase your question?"
    except Exception as e:
        st.warning(f"Claude API note: {str(e)}. Falling back to Demo Mode response.")
        return rule_based_demo_reply(clean_msgs[-1]["content"], profile)


def call_claude_outfit(data: Dict[str, Any], profile: Dict[str, Any], api_key: str, model: str) -> Dict[str, str]:
    """Call Claude API to generate a structured outfit JSON."""
    try:
        from anthropic import Anthropic
    except ImportError:
        return rule_based_demo_outfit(data, profile)

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

    try:
        client = Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model,
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
        return rule_based_demo_outfit(data, profile)
    except Exception as e:
        st.warning(f"Claude API note: {str(e)}. Generating with rule-based styling.")
        return rule_based_demo_outfit(data, profile)


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

        if active_key:
            st.markdown(
                '<div class="status-badge status-live">🟢 Claude AI Active</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-badge status-demo">🎭 Demo Mode Active</div>',
                unsafe_allow_html=True,
            )

        user_key_input = st.text_input(
            "Anthropic API Key (Optional)",
            type="password",
            value=st.session_state.get("user_api_key", ""),
            help="Paste your Anthropic Claude API key. If empty, the app runs in free rule-based Demo Mode. In Streamlit Cloud, you can set ANTHROPIC_API_KEY in App Settings -> Secrets.",
            placeholder="sk-ant-api03-...",
        )
        if user_key_input != st.session_state.get("user_api_key", ""):
            st.session_state["user_api_key"] = user_key_input
            st.rerun()

        model_choice = st.selectbox(
            "Claude Model",
            options=["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307", "claude-3-opus-20240229"],
            index=0,
            help="Select the Anthropic Claude model to generate recommendations.",
        )

        st.markdown("---")
        st.markdown("#### 👤 Current Profile")
        st.text(f"Styling for: {st.session_state.profile.get('name', 'Guest')}")
        st.text(f"Colors: {st.session_state.profile.get('favorite_colors', 'None set')[:25]}...")
        st.caption("Customize your full profile in the **User Profile** tab.")

        st.markdown("---")
        st.markdown(
            """
            **🚀 Deployment Info:**
            - **Streamlit Cloud**: Add `ANTHROPIC_API_KEY` to **App Secrets**.
            - **Zero Setup**: Runs in Demo Mode even without an API key!
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
                ("🎓 College Outfit", "What should I wear to college tomorrow?"),
                ("💼 Job Interview", "I need a polished outfit for a corporate job interview."),
                ("🎉 Birthday Party", "Suggest a stylish, standout outfit for an evening birthday party."),
                ("☕ Comfy Casual", "Suggest a chic, relaxed outfit for coffee and walking around."),
                ("✈️ Travel Look", "What should I wear for a long flight and travel day?"),
                ("✨ Dinner Date", "Help me style a classy and confident dinner date outfit."),
                ("🎨 Color Matching", "What colors pair best with beige and navy?"),
                ("👖 Match My Clothes", "I have dark blue jeans and a white shirt. How can I style them?"),
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
                        "Casual Weekend",
                        "Job Interview / Formal Office",
                        "Evening Party / Dinner Date",
                        "Long Travel / Flight",
                        "College / Campus",
                        "Wedding Guest / Festive",
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
                rows=2,
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
                rows=3,
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
