# AI Pharma Lead Generation Platform

An AI-powered platform for discovering Indian pharmaceutical companies that outsource manufacturing.

## Features

- 🔍 **Multi-Source Data Collection** - Google Search + Directory scraping via SerpAPI
- 🤖 **AI Classification** - LangChain-powered business model classification
- 📊 **Outsourcing Scoring** - 1-10 likelihood score with justification
- 📇 **Contact Extraction** - Emails, phones, LinkedIn URLs
- 💾 **Deduplication** - Domain-based duplicate prevention
- 📤 **CSV Export** - Ready-to-use lead list

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
OPENAI_API_KEY=your_openai_key_here
OR
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the Pipeline

```bash
# Full run
python main.py

# Test mode (limited queries)
python main.py --test-mode
```

## Output

The pipeline generates `output/pharma_leads.csv` with columns:

| Column | Description |
|--------|-------------|
| Company Name | Company name |
| Website | Company URL |
| LinkedIn | LinkedIn company page |
| Size (Employees) | Employee count |
| Location | City/State in India |
| Business Model | manufacturing/marketing/hybrid |
| Outsourcing Score (1-10) | Likelihood of outsourcing |
| Contact Found | Yes/No |
| Emails | Extracted emails |
| Phone Numbers | Phone numbers |
| Next Action | Suggested follow-up |
| Notes | Score justification |

## Project Structure

```
├── config/config.py         # Settings and API keys
├── collectors/
│   ├── google_scraper.py    # SerpAPI Google search
│   └── directory_scraper.py # Directory site searches
├── analyzers/
│   ├── classifier.py        # Business model AI classifier
│   └── scorer.py            # Outsourcing score calculator
├── extractors/
│   └── contact_extractor.py # Contact info extraction
├── database/
│   ├── models.py            # Pydantic data models
│   └── storage.py           # SQLite + CSV export
├── pipeline/
│   └── agent.py             # LangGraph workflow
├── main.py                  # CLI entry point
└── output/                  # Generated CSV files
```

## Search Keywords

The platform searches for:
- "loan license pharma India"
- "third party manufacturing pharma"
- "pharma marketing company India"
- "pharma franchise manufacturer"
- And more (see `config/config.py`)

## Requirements

- Python 3.11+
- SerpAPI account (for search)
- OpenAI API key (for AI classification, optional) or Groq API key (for AI classification, optional)
