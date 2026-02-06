"""
Storage module for saving and exporting leads
"""
import os
import sqlite3
import pandas as pd
from typing import List, Optional
from urllib.parse import urlparse
from database.models import Company
from config.config import DATABASE_PATH, OUTPUT_DIR, OUTPUT_FILENAME


def get_domain(url: str) -> str:
    """Extract domain from URL for deduplication"""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        domain = domain.lower().replace("www.", "")
        return domain
    except:
        return url.lower()


class LeadStorage:
    """SQLite storage for leads with deduplication"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                website TEXT,
                domain TEXT UNIQUE,
                linkedin TEXT,
                size_employees TEXT,
                location TEXT,
                business_model TEXT,
                outsourcing_score INTEGER,
                contact_found INTEGER,
                emails TEXT,
                phone_numbers TEXT,
                next_action TEXT,
                notes TEXT,
                source TEXT,
                discovered_at TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def save_company(self, company: Company) -> bool:
        """Save company with deduplication by domain. Returns True if new, False if duplicate."""
        domain = get_domain(company.website) if company.website else company.company_name.lower()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO companies (
                    company_name, website, domain, linkedin, size_employees, 
                    location, business_model, outsourcing_score, contact_found,
                    emails, phone_numbers, next_action, notes, source, discovered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company.company_name,
                company.website,
                domain,
                company.linkedin,
                company.size_employees,
                company.location,
                company.business_model,
                company.outsourcing_score,
                1 if company.contact_found else 0,
                "; ".join(company.emails),
                "; ".join(company.phone_numbers),
                company.next_action,
                company.notes,
                company.source,
                company.discovered_at.isoformat()
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Duplicate domain
            return False
        finally:
            conn.close()
    
    def save_companies(self, companies: List[Company]) -> tuple:
        """Save multiple companies. Returns (saved_count, duplicate_count)"""
        saved = 0
        duplicates = 0
        for company in companies:
            if self.save_company(company):
                saved += 1
            else:
                duplicates += 1
        return saved, duplicates
    
    def get_all_companies(self) -> List[dict]:
        """Get all companies as dictionaries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return [dict(zip(columns, row)) for row in rows]
    
    def export_to_csv(self, filepath: Optional[str] = None) -> str:
        """Export all leads to CSV file"""
        if filepath is None:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            filepath = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        
        companies = self.get_all_companies()
        
        # Map to output format
        rows = []
        for c in companies:
            rows.append({
                "Company Name": c["company_name"],
                "Website": c["website"] or "",
                "LinkedIn": c["linkedin"] or "",
                "Size (Employees)": c["size_employees"] or "",
                "Location": c["location"] or "",
                "Business Model": c["business_model"] or "",
                "Outsourcing Score (1-10)": c["outsourcing_score"] or "",
                "Contact Found": "Yes" if c["contact_found"] else "No",
                "Emails": c["emails"] or "",
                "Phone Numbers": c["phone_numbers"] or "",
                "Next Action": c["next_action"] or "",
                "Notes": c["notes"] or "",
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
        return filepath
    
    def count(self) -> int:
        """Get total count of companies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM companies")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def clear(self):
        """Clear all data (for testing)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM companies")
        conn.commit()
        conn.close()
