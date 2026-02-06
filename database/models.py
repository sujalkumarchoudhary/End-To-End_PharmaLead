"""
Data models for AI Pharma Lead Generation Platform
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Contact(BaseModel):
    """Contact person information"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    linkedin: Optional[str] = None


class Company(BaseModel):
    """Company data model matching output CSV format"""
    company_name: str = Field(..., description="Company name")
    website: Optional[str] = Field(None, description="Company website URL")
    linkedin: Optional[str] = Field(None, description="LinkedIn company page")
    size_employees: Optional[str] = Field(None, description="Estimated employee count")
    location: Optional[str] = Field(None, description="City/State in India")
    business_model: Optional[str] = Field(None, description="manufacturing/marketing/hybrid")
    outsourcing_score: Optional[int] = Field(None, ge=1, le=10, description="Outsourcing likelihood 1-10")
    contact_found: bool = Field(False, description="Whether contact info was found")
    emails: List[str] = Field(default_factory=list, description="Extracted emails")
    phone_numbers: List[str] = Field(default_factory=list, description="Extracted phone numbers")
    next_action: Optional[str] = Field(None, description="Suggested follow-up action")
    notes: Optional[str] = Field(None, description="Score justification and notes")
    source: Optional[str] = Field(None, description="Where this lead was found")
    discovered_at: datetime = Field(default_factory=datetime.now)
    
    def to_csv_row(self) -> dict:
        """Convert to CSV row format"""
        return {
            "Company Name": self.company_name,
            "Website": self.website or "",
            "LinkedIn": self.linkedin or "",
            "Size (Employees)": self.size_employees or "",
            "Location": self.location or "",
            "Business Model": self.business_model or "",
            "Outsourcing Score (1-10)": self.outsourcing_score or "",
            "Contact Found": "Yes" if self.contact_found else "No",
            "Emails": "; ".join(self.emails),
            "Phone Numbers": "; ".join(self.phone_numbers),
            "Next Action": self.next_action or "",
            "Notes": self.notes or "",
        }


class SearchResult(BaseModel):
    """Raw search result from scraper"""
    title: str
    link: str
    snippet: Optional[str] = None
    source: str  # google, indiamart, tradeindia, pharmabiz
    keyword_used: Optional[str] = None
