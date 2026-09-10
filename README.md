# 👗 AI Fashion Stylist — StyleMate AI

A complete, working AI personal fashion stylist that gives personalized outfit recommendations based on occasion, style, colors, weather/season, and your personal wardrobe.

---

## 🌟 1. Streamlit App (Fastest & Easiest Deployment) 🚀

The project is fully configured for **1-click deployment to Streamlit Community Cloud** (and local execution via Streamlit).

### Features:
- **💬 Interactive Stylist Chat**: Context-aware chat with quick prompts ("College Outfit", "Job Interview", "Birthday Party", "Comfy Casual", "Match My Clothes", etc.).
- **✨ Structured Outfit Generator**: Build custom looks specifying occasion, season, aesthetic, colors, and owned clothes with full piece breakdowns (Top, Bottom, Dress, Shoes, Accessories, Bag, Layering, and Style Tips).
- **💾 Saved Looks**: Save, browse, and manage your favorite outfits.
- **👤 User Style Profile**: Personalize your name, style aesthetic, color palette, and wardrobe items.
- **🔑 Flexible API Key & Demo Mode**:
  - Automatically reads from Streamlit Secrets (`st.secrets["ANTHROPIC_API_KEY"]`), `.env` file, or sidebar input.
  - Runs in a rich **Demo Mode** if no API key is provided (zero setup required!).

### Quick Start (Local):
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the Streamlit app
streamlit run streamlit_app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### Deploying to Streamlit Community Cloud:
1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app.
3. Select your repository and set Main file path to `streamlit_app.py` (or `app.py`).
4. **(Optional)** In **App Settings ➔ Secrets**, add your Anthropic API key:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-api03-..."
   ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
   ```
5. Click **Deploy**! If you don't add an API key, the app automatically runs in free **Demo Mode**.

---

## 2. `python-backend/` — FastAPI Implementation ✅

Pure-Python reference implementation using **FastAPI, Uvicorn, Pydantic, SQLAlchemy + SQLite, python-dotenv, and Anthropic Claude SDK**, with an HTML/CSS/JS frontend served by Jinja2.

```bash
cd python-backend
python -m venv venv
# Windows: venv\Scripts\activate   |   macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then set ANTHROPIC_API_KEY (optional; empty = DEMO MODE)
uvicorn app.main:app --reload
# open http://localhost:8000
pytest -q                     # run tests
```

---

## 3. Repository root — Next.js Implementation

Next.js version with React and TypeScript, Postgres via Drizzle, and Anthropic Claude integration.

---

## 🔑 Where to put your Anthropic API key
- **Streamlit Cloud:** Go to App Settings ➔ Secrets ➔ add `ANTHROPIC_API_KEY = "sk-..."`.
- **Streamlit UI:** Enter it directly into the sidebar text input.
- **Python / FastAPI:** Set `ANTHROPIC_API_KEY=...` in `python-backend/.env`.
- **Next.js:** Set `ANTHROPIC_API_KEY=...` in `.env`.
- **Demo Mode:** If unset, all versions run in free rule-based Demo Mode with no errors.
