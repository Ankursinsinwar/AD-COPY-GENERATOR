# Ad Copy Generator + A/B Tester

An AI-powered digital marketing automation platform built with Python, Flask, Groq API (Llama 3.1 8B Instant), and a modern single-page SaaS frontend interface. It enables digital marketers and SaaS teams to generate, evaluate, persist, and export platform-tailored advertisement copy variations.

---

## 1. Project Overview

The **Ad Copy Generator + A/B Tester** automates advertisement creation across major digital advertising networks. Users provide product details, target demographics, tone styles, and desired A/B variation angles. The platform constructs platform-constrained prompts, queries the Groq Llama 3.1 8B Instant model, parses structured outputs using a 4-method fallback engine, scores quality metrics, saves campaign history locally, and exports reports to CSV and Notion Markdown.

---

## 2. Key Features

- **Multi-Platform Generation**: Custom rules for Google Ads, Facebook, Instagram, LinkedIn, and Twitter/X.
- **A/B Variation Angles**: Distinct marketing approaches (Feature-Focused, Benefit-Focused, Urgency-Focused).
- **Tone Controller**: 6 selectable tones (Professional, Casual, Urgent, Humorous, Emotional, Minimalist).
- **Multi-Stage Fallback JSON Parser**: 4 resilient extraction methods to handle model formatting variations.
- **Deterministic Quality Scoring**: Sub-scores for Headline Strength, Clarity, Emotional Appeal, CTA Effectiveness, and weighted overall score.
- **Local History Persistence**: Automatic storage of generated campaigns in `data/history.json`.
- **Export Center**: Instant CSV file generation and Notion-compatible Markdown popover/download.
- **Modern Responsive SaaS UI**: Single-page application with pill selectors, toast notifications, score badges, and clipboard helpers.
- **Robust Error Handling**: Graceful fallback error cards for API rate limits (HTTP 429 quota exceeded) without crashing the application.
- **Automated Testing Suite**: 100% mocked Groq API unit test suite with 29 pytest assertions.

---

## 3. System Architecture

```
User Frontend (HTML5 / Vanilla CSS / JS)
    │
    ▼ (REST JSON AJAX)
Flask REST API (`backend/routes/api.py`)
    │
    ▼
Ad Generator Service (`backend/services/ad_generator.py`)
    ├── Platform & Tone Configs (`backend/config/`)
    ├── Multi-Method JSON Extractor (`backend/utils/json_parser.py`)
    ├── Copy Scoring Engine (`backend/services/scoring_service.py`)
    ├── History Persistence Service (`backend/services/history_service.py`)
    └── Export Helper Service (`backend/services/export_service.py`)
    │
    ▼
Groq AI Service Wrapper (`backend/services/groq_service.py`)
    │
    ▼ (HTTPS API)
Groq Llama 3.1 8B Instant API
```

---

## 4. Target Folder Structure

```
AdCopyGenerator/
│
├── app.py                      # Flask Application Factory & Server entry point
├── requirements.txt            # Project Python dependencies
├── .env.example                # Environment variable documentation
├── .gitignore                  # Git exclusion rules
├── README.md                   # Complete documentation
│
├── backend/
│   ├── __init__.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api.py              # REST API Endpoints (/api/*)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ad_generator.py     # Campaign generation orchestrator
│   │   ├── groq_service.py     # Groq SDK wrapper & error handling
│   │   ├── scoring_service.py  # Quality analytics & scoring engine
│   │   ├── history_service.py  # Local JSON history persistence
│   │   └── export_service.py   # CSV & Notion Markdown exporter
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── json_parser.py      # 4-stage fallback JSON extractor
│   │   ├── validators.py       # Input payload validation
│   │   └── constants.py        # System prompt & variation directives
│   │
│   └── config/
│       ├── __init__.py
│       ├── platforms.py        # Centralized 5 platform specs & rules
│       └── tones.py            # Centralized 6 tone specs & descriptions
│
├── frontend/
│   ├── index.html              # Modern single-page SaaS interface
│   │
│   └── assets/
│       ├── css/
│       │   └── style.css       # Premium CSS styling & layout
│       │
│       └── js/
│           ├── app.js          # Core app controller & toasts
│           ├── generator.js    # Form state & AJAX triggers
│           ├── results.js      # Variation cards & score rendering
│           ├── history.js      # Saved campaign history list
│           └── export.js       # CSV download & Notion modal
│
├── data/
│   └── history.json            # Local persistence file
│
├── exports/
│   └── .gitkeep                # Export directory marker
│
└── tests/
    ├── conftest.py             # Pytest fixtures & mocks
    ├── test_api.py             # API route tests
    ├── test_generator.py       # Generator service tests
    ├── test_json_parser.py     # Multi-method parser tests
    ├── test_platforms.py       # Configuration tests
    ├── test_scoring.py         # Scoring engine tests
    ├── test_history.py         # History persistence tests
    ├── test_exports.py         # CSV & Notion export tests
    └── test_error_handling.py  # Edge case & 429 quota error tests
```

---

## 5. Technologies Used

- **Language**: Python 3.14+
- **Backend Framework**: Flask 3.1
- **CORS Support**: Flask-CORS 6.0
- **AI SDK**: Groq Python SDK 1.7 (`llama-3.1-8b-instant`)
- **Frontend**: HTML5, Vanilla JavaScript (ES6+), Modern Vanilla CSS
- **Icons & Fonts**: Google Fonts (Inter, Fira Code), FontAwesome 6
- **Test Framework**: Pytest 9.1

---

## 6. Environment Setup & Configuration

Create a `.env` file in the root directory (based on `.env.example`):

```env
GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
FLASK_SECRET_KEY=dev-secret-key-change-in-production-12345
FLASK_ENV=development
```

---

## 7. Groq API Configuration

1. Create a free account at [Groq Console](https://console.groq.com).
2. Generate an API Key in the dashboard.
3. Paste the key into `GROQ_API_KEY` inside `.env`.

---

## 8. Installation

1. Activate your virtual environment:
   ```bash
   .\venv\Scripts\activate
   ```
2. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 9. Running the Application

Start the Flask development server:
```bash
python app.py
```
Open your browser and navigate to:
`http://127.0.0.1:5000/`

---

## 10. REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check & Groq status |
| `POST` | `/api/generate` | Generate ad copies across platforms |
| `POST` | `/api/export/csv` | Download generated results as CSV |
| `POST` | `/api/export/notion` | Get Notion-compatible Markdown report |
| `GET` | `/api/history` | List latest 20 saved campaigns |
| `GET` | `/api/history/<id>` | Fetch specific campaign by ID |

---

## 11. Platform Generation Rules

- **Google Ads**: Search Ad format. Headline ≤ 30 chars (max 3), Description ≤ 90 chars (max 2). Sentence case, no exclamation marks in headlines, no hashtags.
- **Facebook**: Feed Ad format. Primary text ≤ 125 chars, Headline ≤ 40 chars. Starts with strong hook.
- **Instagram**: Feed/Story Ad format. Caption capture ≤ 125 chars. Lifestyle & emotion focus. Includes 3-5 hashtags.
- **LinkedIn**: Sponsored Content format. Intro ≤ 150 chars, Headline ≤ 70 chars. Professional B2B tone. Includes 2-3 B2B hashtags.
- **Twitter/X**: Promoted Tweet format. Total max ≤ 280 chars. Concise, 1-2 hashtags, conversational tone.

---

## 12. Tone Configurations

1. **Professional**: Authoritative, polished, business-focused.
2. **Casual**: Friendly, conversational, warm.
3. **Urgent**: Time-sensitive, action-driven, FOMO.
4. **Humorous**: Witty, playful, clever wordplay.
5. **Emotional**: Empathetic, inspiring, story-driven.
6. **Minimalist**: Ultra-clean, direct, maximum impact in fewest words.

---

## 13. A/B Variation Logic

- **Variation A (Feature-Focused)**: Focuses on features, specifications, and utility.
- **Variation B (Benefit-Focused)**: Focuses on customer pain points, benefits, and positive outcomes.
- **Variation C (Urgency-Focused)**: Focuses on FOMO, scarcity, exclusivity, and immediate action.

---

## 14. Scoring Engine & Formula

Scores evaluate copy quality across 5 metrics:
- **Headline Strength (30%)**: Impact, length adherence, hook quality.
- **Clarity (25%)**: Readability index, conciseness.
- **Emotional Appeal (25%)**: Persuasive triggers and power words.
- **CTA Effectiveness (20%)**: Action verb presence and urgency.

**Overall Formula**:
$$\text{Overall Score} = 0.30 \cdot \text{Headline} + 0.25 \cdot \text{Clarity} + 0.25 \cdot \text{Emotional} + 0.20 \cdot \text{CTA}$$

---

## 15. Export Functionality

- **CSV Export**: Columns include `Platform`, `Variation`, `Label`, `Headline`, `Body`, `CTA`, `Hashtags`, `Overall Score`, `Suggestions`. Directly compatible with Excel and Google Sheets.
- **Notion Export**: Generates clean Markdown with headers, metadata, variation blocks, scores, strengths, and suggestions ready to paste or download as `.md`.

---

## 16. Running Automated Tests

Run the complete pytest test suite (all Groq API calls are mocked):
```bash
pytest -v
```

---

## 17. Screenshots Placeholder

*(Place UI screenshots of generator form, variation cards, score badges, Notion export modal, and history panel here)*

---

## 18. Demonstration Instructions

1. Start application (`python app.py`).
2. Open `http://127.0.0.1:5000/`.
3. Input Product Name: `"Acme AI CRM"`.
4. Input Description: `"Cloud customer relationship manager with automated AI email responses."`
5. Input Target Audience: `"SaaS Founders and Sales Leads"`.
6. Select platforms (Google Ads, Facebook, Instagram, LinkedIn, Twitter/X).
7. Select tone: `"Professional"`.
8. Click **Generate Ad Copies**.
9. Inspect rendered variation cards, score badges, and copy buttons.
10. Click **Export to Notion** to preview Markdown report.
11. Click **Campaign History** in the sidebar to review persisted data.

---

## 19. Known Limitations

- Real-time Groq API generation requires an active internet connection and valid `GROQ_API_KEY`.
- If API key is unconfigured or quota is exceeded (HTTP 429), the system displays platform error cards while preserving UI stability.
