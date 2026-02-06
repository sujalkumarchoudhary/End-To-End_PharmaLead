"""
AI Business Model Classifier using LangChain
Classifies companies as manufacturing, marketing, or hybrid
Supports: OpenAI, Groq (FREE), or keyword-based fallback
"""
from typing import Optional
from config.config import (
    OPENAI_API_KEY, GROQ_API_KEY, LLM_PROVIDER,
    LLM_MODEL_OPENAI, LLM_MODEL_GROQ, LLM_TEMPERATURE
)


def get_llm():
    """Get the appropriate LLM based on configuration"""
    provider = LLM_PROVIDER.lower()
    
    # Auto-detect if provider is "auto"
    if provider == "auto":
        if GROQ_API_KEY:
            provider = "groq"
        elif OPENAI_API_KEY:
            provider = "openai"
        else:
            provider = "none"
    
    if provider == "groq" and GROQ_API_KEY:
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                api_key=GROQ_API_KEY,
                model_name=LLM_MODEL_GROQ,
                temperature=LLM_TEMPERATURE
            )
        except ImportError:
            print("⚠️  langchain-groq not installed. Using keyword-based classification.")
            return None
    
    elif provider == "openai" and OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model=LLM_MODEL_OPENAI,
                temperature=LLM_TEMPERATURE
            )
        except ImportError:
            print("⚠️  langchain-openai not installed. Using keyword-based classification.")
            return None
    
    return None


class BusinessModelClassifier:
    """Classify company business model using LLM or keywords"""
    
    def __init__(self):
        self.llm = get_llm()
        self.prompt = None
        
        if self.llm:
            from langchain_core.prompts import ChatPromptTemplate
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a pharmaceutical industry analyst. Analyze company information and classify its business model.

Classify into ONE of these categories:
- "manufacturing": Company owns manufacturing facilities and produces pharma products
- "marketing": Company focuses on marketing/distribution, likely outsources manufacturing (loan license, third party)
- "hybrid": Company does both manufacturing and marketing

Look for key indicators:
MARKETING indicators: "loan license", "third party", "franchise", "distribution", "marketing company", "propaganda"
MANUFACTURING indicators: "WHO-GMP certified", "manufacturing unit", "plant", "FDA approved facility"

Respond with ONLY the category word: manufacturing, marketing, or hybrid"""),
                ("human", """Company: {company_name}
Website: {website}
Description: {snippet}

Classify this company's business model:""")
            ])
    
    def classify(self, company_name: str, website: str = "", snippet: str = "") -> Optional[str]:
        """Classify a company's business model"""
        if not self.llm or not self.prompt:
            return self._keyword_classify(company_name, snippet)
        
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "company_name": company_name,
                "website": website or "",
                "snippet": snippet or ""
            })
            
            result = response.content.strip().lower()
            
            if result in ["manufacturing", "marketing", "hybrid"]:
                return result
            
            return self._keyword_classify(company_name, snippet)
            
        except Exception as e:
            print(f"⚠️  Classification error for {company_name}: {e}")
            return self._keyword_classify(company_name, snippet)
    
    def _keyword_classify(self, company_name: str, snippet: str) -> str:
        """Keyword-based classification (works without any API)"""
        text = f"{company_name} {snippet}".lower()
        
        marketing_keywords = [
            "loan license", "third party", "franchise", "distribution",
            "marketing company", "propaganda", "virtual pharma", "pcd",
            "pharma franchise", "marketing and distribution", "loan licensee"
        ]
        manufacturing_keywords = [
            "manufacturing unit", "who-gmp", "gmp certified", "plant",
            "manufacturing facility", "fda approved", "production unit",
            "manufacturer", "factory", "api manufacturer"
        ]
        
        has_marketing = any(kw in text for kw in marketing_keywords)
        has_manufacturing = any(kw in text for kw in manufacturing_keywords)
        
        if has_marketing and has_manufacturing:
            return "hybrid"
        elif has_marketing:
            return "marketing"
        elif has_manufacturing:
            return "manufacturing"
        else:
            return "marketing"  # Default for pharma lead gen
