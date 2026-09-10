"""Self-contained verification script for StyleMate AI logic."""
import sys
from unittest.mock import MagicMock

# If streamlit is not installed in the local runner, mock it for logic testing
if "streamlit" not in sys.modules:
    class DotDict(dict):
        def __getattr__(self, attr):
            return self.get(attr)
        def __setattr__(self, attr, value):
            self[attr] = value
        def __delattr__(self, attr):
            del self[attr]

    mock_st = MagicMock()
    mock_st.session_state = DotDict()
    mock_st.secrets = {}
    sys.modules["streamlit"] = mock_st

from streamlit_app import (
    build_system_prompt,
    rule_based_demo_reply,
    rule_based_demo_outfit,
    get_api_key,
    is_demo_mode,
)

def test_all():
    profile = {
        "name": "Alex",
        "style_preferences": "Minimalist chic",
        "favorite_colors": "Navy, cream",
        "disliked_colors": "Neon yellow",
        "preferred_occasions": "Office, weekend brunch",
        "clothing_items": "White sneakers, navy blazer, blue jeans",
    }

    # 1. Test system prompt generation
    prompt = build_system_prompt(profile)
    assert "Alex" in prompt, "Profile name not in prompt"
    assert "Navy, cream" in prompt, "Colors not in prompt"
    print("[OK] System prompt generation OK")

    # 2. Test demo reply
    reply = rule_based_demo_reply("What should I wear for a job interview?", profile)
    assert len(reply) > 20
    assert "DEMO MODE" in reply
    print("[OK] Demo chat reply OK")

    # 3. Test demo color reply
    color_reply = rule_based_demo_reply("What colors match beige?", profile)
    assert "Color Styling Advice" in color_reply
    print("[OK] Color matching reply OK")

    # 4. Test demo outfit generation
    outfit = rule_based_demo_outfit({"occasion": "party"}, profile)
    assert "outfit" in outfit
    assert "top" in outfit
    assert "bottom" in outfit
    assert "shoes" in outfit
    assert "styleTip" in outfit
    assert outfit["top"] != ""
    print("[OK] Outfit generation OK:", outfit["outfit"])

    # 5. Test key resolution in demo mode
    assert is_demo_mode() is True
    print(f"[OK] Key resolution OK (demo_mode={is_demo_mode()})")

    # 6. Test outfit categories
    for occ in ["interview", "party", "travel", "college", "casual"]:
        out = rule_based_demo_outfit({"occasion": occ}, profile)
        assert out["outfit"], f"Failed for {occ}"
        assert out["top"], f"Missing top for {occ}"
        assert out["bottom"], f"Missing bottom for {occ}"
        assert out["shoes"], f"Missing shoes for {occ}"
    print("[OK] All occasion category fallbacks OK")

    print("\n=== ALL LOGIC AND RESILIENCE TESTS PASSED! ===")

if __name__ == "__main__":
    test_all()
