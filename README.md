# AI Pharma Lead Generation Platform

An AI-powered platform for discovering Indian pharmaceutical companies that outsource manufacturing.

## Features

- 🔍 **Multi-Source Data Collection** - Google Search + Directory scraping via SerpAPI
- 🤖 **AI Classification** - LangChain-powered business model classification (Groq FREE / OpenAI)
- 📊 **Outsourcing Scoring** - 1-10 likelihood score with justification
- 📇 **Contact Extraction** - Emails, phones, LinkedIn URLs
- 💾 **Deduplication** - Domain-based duplicate prevention
- 📤 **CSV Export** - Ready-to-use lead list
- 🌐 **Web Interface** - Beautiful Streamlit dashboard

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
SERPAPI_KEY=your_serpapi_key_here
GROQ_API_KEY=your_groq_key_here  # FREE at console.groq.com
```

### 3. Run the Platform

**🌐 Web Interface (Recommended):**
```bash
python -m streamlit run app.py
```
Open http://localhost:8501 in your browser.

**💻 Command Line:**
```bash
python main.py              # Full run
python main.py --test-mode  # Quick test
```

---

## Web Interface

| Tab | Feature |
|-----|---------|
| 📊 Dashboard | Metrics, charts, filterable lead table |
| 🚀 Run Pipeline | Start lead discovery with progress |
| 📥 Export | Download CSV of all leads |

---

## Output CSV Format

| Column | Description |
|--------|-------------|
| Company Name | Company name |
| Website | Company URL |
| LinkedIn | LinkedIn company page |
| Location | City/State in India |
| Business Model | manufacturing/marketing/hybrid |
| Outsourcing Score (1-10) | Likelihood of outsourcing |
| Contact Found | Yes/No |
| Emails | Extracted emails |
| Phone Numbers | Phone numbers |
| Next Action | Suggested follow-up |
| Notes | Score justification |

---

## Project Structure

```
├── app.py               # 🌐 Streamlit web interface
├── main.py              # 💻 CLI entry point
├── config/config.py     # Settings and API keys
├── collectors/          # SerpAPI scrapers
├── analyzers/           # AI classifiers (Groq/OpenAI/keyword)
├── extractors/          # Contact extraction
├── database/            # SQLite + CSV export
├── pipeline/            # LangGraph workflow
└── output/              # Generated CSV files
```

---

## LLM Options

| Option | Cost | Setup |
|--------|------|-------|
| Groq | **FREE** | Get key at console.groq.com |
| OpenAI | Paid | Set OPENAI_API_KEY |
| Keyword-only | FREE | Leave keys empty |

---

## Requirements

- Python 3.11+
- SerpAPI account (for search)
- Groq API key (FREE, for AI classification)
