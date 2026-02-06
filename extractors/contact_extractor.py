"""
Contact Information Extractor
Extracts emails, phones, and LinkedIn URLs from search results
"""
import re
from typing import List, Tuple, Optional
from urllib.parse import urlparse


class ContactExtractor:
    """Extract contact information from company data"""
    
    # Common email patterns for pharma companies
    EMAIL_PREFIXES = ["info", "contact", "sales", "enquiry", "inquiry", "marketing", "business"]
    
    # Email regex
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    
    # Phone regex (Indian format)
    PHONE_PATTERN = re.compile(r'(?:\+91[\-\s]?)?(?:[0-9]{10}|[0-9]{5}[\-\s][0-9]{5}|[0-9]{4}[\-\s][0-9]{6})')
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        if not text:
            return []
        
        emails = self.EMAIL_PATTERN.findall(text)
        # Filter out common false positives
        filtered = []
        for email in emails:
            email = email.lower()
            if not any(x in email for x in ["example.com", "test.com", "domain.com"]):
                filtered.append(email)
        return list(set(filtered))
    
    def generate_email_patterns(self, domain: str) -> List[str]:
        """Generate common email patterns for a domain"""
        if not domain:
            return []
        
        # Clean domain
        domain = domain.lower().replace("www.", "")
        
        emails = []
        for prefix in self.EMAIL_PREFIXES:
            emails.append(f"{prefix}@{domain}")
        
        return emails
    
    def extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        if not text:
            return []
        
        phones = self.PHONE_PATTERN.findall(text)
        # Clean and format
        cleaned = []
        for phone in phones:
            # Remove spaces and dashes, keep digits and +
            phone = re.sub(r'[\s\-]', '', phone)
            if len(phone) >= 10:
                cleaned.append(phone)
        
        return list(set(cleaned))
    
    def extract_linkedin(self, text: str, company_name: str) -> Optional[str]:
        """Extract or generate LinkedIn company URL"""
        if not text:
            return None
        
        # Look for LinkedIn URL in text
        linkedin_pattern = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/company/[a-zA-Z0-9\-]+/?')
        matches = linkedin_pattern.findall(text)
        
        if matches:
            url = matches[0]
            if not url.startswith("http"):
                url = "https://" + url
            return url
        
        # Generate probable LinkedIn URL from company name
        if company_name:
            slug = company_name.lower()
            slug = re.sub(r'[^a-z0-9\s]', '', slug)
            slug = slug.replace(' ', '-')
            slug = re.sub(r'-+', '-', slug).strip('-')
            if slug:
                return f"https://www.linkedin.com/company/{slug}"
        
        return None
    
    def extract_location(self, text: str) -> Optional[str]:
        """Extract location from text (Indian cities/states)"""
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Major pharma hubs in India
        indian_locations = [
            "mumbai", "delhi", "ahmedabad", "hyderabad", "bangalore", "bengaluru",
            "chennai", "pune", "kolkata", "indore", "chandigarh", "baddi",
            "sikkim", "himachal", "goa", "surat", "vadodara", "jaipur",
            "lucknow", "nagpur", "bhopal", "panchkula", "mohali",
            "maharashtra", "gujarat", "karnataka", "tamil nadu", "telangana",
            "uttarakhand", "himachal pradesh", "haryana", "rajasthan",
        ]
        
        for location in indian_locations:
            if location in text_lower:
                return location.title()
        
        return None
    
    def extract_all(self, company_name: str, website: str, snippet: str) -> dict:
        """
        Extract all contact info from company data.
        Returns dict with: emails, phone_numbers, linkedin, location, contact_found
        """
        combined_text = f"{company_name} {website} {snippet}"
        
        # Extract from snippet
        emails = self.extract_emails(snippet)
        phones = self.extract_phones(snippet)
        
        # Generate email patterns if none found
        if not emails and website:
            domain = urlparse(website).netloc if website.startswith("http") else website
            domain = domain.replace("www.", "")
            emails = self.generate_email_patterns(domain)[:3]  # Top 3 patterns
        
        linkedin = self.extract_linkedin(combined_text, company_name)
        location = self.extract_location(combined_text)
        
        contact_found = bool(emails or phones)
        
        return {
            "emails": emails,
            "phone_numbers": phones,
            "linkedin": linkedin,
            "location": location,
            "contact_found": contact_found
        }
