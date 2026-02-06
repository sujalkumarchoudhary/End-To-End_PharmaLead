"""
Outsourcing Score Calculator
Calculates likelihood (1-10) that a company outsources manufacturing
Supports: OpenAI, Groq (FREE), or keyword-based fallback
"""
from typing import Tuple
from config.config import (
    OPENAI_API_KEY, GROQ_API_KEY, LLM_PROVIDER,
    LLM_MODEL_OPENAI, LLM_MODEL_GROQ, LLM_TEMPERATURE
)


def get_llm():
    """Get the appropriate LLM based on configuration"""
    provider = LLM_PROVIDER.lower()
    
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
            return None
    
    return None


class OutsourcingScorer:
    """Calculate outsourcing likelihood score"""
    
    def __init__(self):
        self.llm = get_llm()
        self.prompt = None
        
        if self.llm:
            from langchain_core.prompts import ChatPromptTemplate
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a pharmaceutical industry analyst evaluating B2B leads.

Score how likely a company is to OUTSOURCE manufacturing (1-10):
- 9-10: Very likely (pure marketing company, mentions loan license)
- 7-8: Likely (marketing focused, no manufacturing)
- 5-6: Moderate (hybrid, may need capacity)
- 3-4: Unlikely (has manufacturing)
- 1-2: Very unlikely (large manufacturer)

Respond in this format:
SCORE: [number]
REASON: [one line]"""),
                ("human", """Company: {company_name}
Business Model: {business_model}
Website: {website}
Description: {snippet}

Evaluate:""")
            ])
    
    def score(self, company_name: str, business_model: str = "", 
              website: str = "", snippet: str = "") -> Tuple[int, str]:
        """Score outsourcing likelihood. Returns (score, reason)"""
        if not self.llm or not self.prompt:
            return self._keyword_score(company_name, business_model, snippet)
        
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "company_name": company_name,
                "business_model": business_model or "unknown",
                "website": website or "",
                "snippet": snippet or ""
            })
            
            result = response.content.strip()
            score = 5
            reason = "LLM evaluation"
            
            for line in result.split("\n"):
                if line.startswith("SCORE:"):
                    try:
                        score = int(line.replace("SCORE:", "").strip())
                        score = max(1, min(10, score))
                    except:
                        pass
                elif line.startswith("REASON:"):
                    reason = line.replace("REASON:", "").strip()
            
            return score, reason
            
        except Exception as e:
            print(f"⚠️  Scoring error: {e}")
            return self._keyword_score(company_name, business_model, snippet)
    
    def _keyword_score(self, company_name: str, business_model: str, snippet: str) -> Tuple[int, str]:
        """Keyword-based scoring (works without any API)"""
        text = f"{company_name} {business_model} {snippet}".lower()
        
        score = 5
        reasons = []
        
        # High indicators
        high_indicators = [
            ("loan license", 3, "Loan license company"),
            ("third party manufacturing", 3, "Third party manufacturing"),
            ("marketing company", 2, "Marketing company"),
            ("franchise", 2, "Franchise model"),
            ("propaganda", 2, "Distribution focused"),
            ("pcd", 2, "PCD pharma"),
        ]
        
        # Low indicators
        low_indicators = [
            ("manufacturing unit", -2, "Has manufacturing"),
            ("who-gmp", -1, "GMP facility"),
            ("factory", -2, "Owns factory"),
        ]
        
        for keyword, adj, reason in high_indicators:
            if keyword in text:
                score += adj
                reasons.append(reason)
        
        for keyword, adj, reason in low_indicators:
            if keyword in text:
                score += adj
                reasons.append(reason)
        
        if business_model == "marketing":
            score += 2
            reasons.append("Marketing model")
        elif business_model == "manufacturing":
            score -= 2
            reasons.append("Manufacturing model")
        
        score = max(1, min(10, score))
        reason = "; ".join(reasons) if reasons else "Default score"
        return score, reason
