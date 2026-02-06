"""
Configuration module for AI Pharma Lead Generation Platform
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # FREE alternative!

# LLM Provider: "openai", "groq", or "none" (keyword-based only)
# Set to "groq" for free LLM classification
# Set to "none" to use keyword-based classification without any API
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto")  # auto detects available key

# Search Keywords for Pharma Lead Discovery
SEARCH_KEYWORDS = [
    '"loan license pharma" India',
    '"third party manufacturing" pharma India',
    '"pharma marketing company" India',
    '"loan license" pharmaceutical India',
    '"propaganda cum distribution" company pharma',
    '"pharma franchise" manufacturer India',
    '"virtual pharma" company India',
    '"marketing and distribution" pharmaceutical India',
]

# Directory Sites for site: searches
DIRECTORY_SITES = [
    "indiamart.com",
    "tradeindia.com",
    "pharmabiz.com",
]

# Rate Limiting
RATE_LIMIT_DELAY = 1.0  # seconds between requests

# Output Settings
OUTPUT_DIR = "output"
OUTPUT_FILENAME = "pharma_leads.csv"

# Database
DATABASE_PATH = "database/leads.db"

# Search Results Limit
MAX_RESULTS_PER_KEYWORD = 10
MAX_RESULTS_PER_DIRECTORY = 20

# LLM Settings
LLM_MODEL_OPENAI = "gpt-4o-mini"
LLM_MODEL_GROQ = "llama-3.1-8b-instant"  # Fast and free on Groq
LLM_TEMPERATURE = 0.1
