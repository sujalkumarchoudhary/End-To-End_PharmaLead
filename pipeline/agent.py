"""
LangGraph Pipeline Agent for Lead Generation
Orchestrates the full collection → classification → scoring → export workflow
"""
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from database.models import SearchResult, Company
from database.storage import LeadStorage
from collectors.google_scraper import GoogleScraper
from collectors.directory_scraper import DirectoryScraper
from analyzers.classifier import BusinessModelClassifier
from analyzers.scorer import OutsourcingScorer
from extractors.contact_extractor import ContactExtractor


class PipelineState(TypedDict):
    """State for the pipeline graph"""
    search_results: List[dict]  # Raw search results
    companies: List[dict]  # Processed companies
    saved_count: int
    duplicate_count: int
    output_path: str
    errors: List[str]


def create_pipeline():
    """Create the LangGraph pipeline"""
    
    # Initialize components
    google_scraper = GoogleScraper()
    directory_scraper = DirectoryScraper()
    classifier = BusinessModelClassifier()
    scorer = OutsourcingScorer()
    contact_extractor = ContactExtractor()
    storage = LeadStorage()
    
    # Define nodes
    def collect_node(state: PipelineState) -> PipelineState:
        """Collect leads from all sources"""
        print("\n" + "="*50)
        print("📡 PHASE 1: DATA COLLECTION")
        print("="*50)
        
        all_results = []
        errors = state.get("errors", [])
        
        try:
            # Google search
            print("\n🔍 Running Google searches...")
            google_results = google_scraper.search_all_keywords()
            all_results.extend([r.model_dump() for r in google_results])
        except Exception as e:
            errors.append(f"Google scraper error: {e}")
            print(f"❌ Google scraper failed: {e}")
        
        try:
            # Directory searches
            print("\n📂 Scraping directories...")
            directory_results = directory_scraper.search_all_directories()
            all_results.extend([r.model_dump() for r in directory_results])
        except Exception as e:
            errors.append(f"Directory scraper error: {e}")
            print(f"❌ Directory scraper failed: {e}")
        
        print(f"\n✅ Total raw results collected: {len(all_results)}")
        
        return {
            **state,
            "search_results": all_results,
            "errors": errors
        }
    
    def classify_node(state: PipelineState) -> PipelineState:
        """Classify and process all search results"""
        print("\n" + "="*50)
        print("🤖 PHASE 2: AI CLASSIFICATION & SCORING")
        print("="*50)
        
        search_results = state.get("search_results", [])
        companies = []
        errors = state.get("errors", [])
        
        # Deduplicate by URL first
        seen_urls = set()
        unique_results = []
        for r in search_results:
            url = r.get("link", "").lower()
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)
        
        print(f"📊 Processing {len(unique_results)} unique results...")
        
        for i, result in enumerate(unique_results):
            try:
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                source = result.get("source", "")
                
                if not title:
                    continue
                
                # Extract company name from title (remove trailing extras)
                company_name = title.split("-")[0].split("|")[0].strip()
                
                # Classify business model
                business_model = classifier.classify(company_name, link, snippet)
                
                # Score outsourcing likelihood
                score, reason = scorer.score(company_name, business_model, link, snippet)
                
                # Extract contacts
                contact_info = contact_extractor.extract_all(company_name, link, snippet)
                
                # Determine next action based on score
                if score >= 8:
                    next_action = "High Priority - Contact immediately"
                elif score >= 6:
                    next_action = "Medium Priority - Research and contact"
                elif score >= 4:
                    next_action = "Low Priority - Add to nurture campaign"
                else:
                    next_action = "Monitor - May not be a good fit"
                
                company = {
                    "company_name": company_name,
                    "website": link,
                    "linkedin": contact_info.get("linkedin"),
                    "size_employees": None,  # Would need additional API
                    "location": contact_info.get("location"),
                    "business_model": business_model,
                    "outsourcing_score": score,
                    "contact_found": contact_info.get("contact_found", False),
                    "emails": contact_info.get("emails", []),
                    "phone_numbers": contact_info.get("phone_numbers", []),
                    "next_action": next_action,
                    "notes": reason,
                    "source": source,
                }
                
                companies.append(company)
                
                if (i + 1) % 10 == 0:
                    print(f"   Processed {i + 1}/{len(unique_results)} companies...")
                
            except Exception as e:
                errors.append(f"Error processing {result.get('title', 'unknown')}: {e}")
        
        print(f"✅ Classified {len(companies)} companies")
        
        return {
            **state,
            "companies": companies,
            "errors": errors
        }
    
    def save_node(state: PipelineState) -> PipelineState:
        """Save companies to database with deduplication"""
        print("\n" + "="*50)
        print("💾 PHASE 3: SAVE TO DATABASE")
        print("="*50)
        
        companies = state.get("companies", [])
        errors = state.get("errors", [])
        
        # Convert to Company objects
        company_objects = []
        for c in companies:
            try:
                company_objects.append(Company(**c))
            except Exception as e:
                errors.append(f"Invalid company data: {e}")
        
        # Save with deduplication
        saved, duplicates = storage.save_companies(company_objects)
        
        print(f"✅ Saved: {saved} new companies")
        print(f"⏭️  Skipped: {duplicates} duplicates")
        print(f"📊 Total in database: {storage.count()}")
        
        return {
            **state,
            "saved_count": saved,
            "duplicate_count": duplicates,
            "errors": errors
        }
    
    def export_node(state: PipelineState) -> PipelineState:
        """Export all leads to CSV"""
        print("\n" + "="*50)
        print("📤 PHASE 4: EXPORT TO CSV")
        print("="*50)
        
        errors = state.get("errors", [])
        
        try:
            output_path = storage.export_to_csv()
            print(f"✅ Exported to: {output_path}")
        except Exception as e:
            output_path = ""
            errors.append(f"Export error: {e}")
            print(f"❌ Export failed: {e}")
        
        return {
            **state,
            "output_path": output_path,
            "errors": errors
        }
    
    # Build graph
    workflow = StateGraph(PipelineState)
    
    # Add nodes
    workflow.add_node("collect", collect_node)
    workflow.add_node("classify", classify_node)
    workflow.add_node("save", save_node)
    workflow.add_node("export", export_node)
    
    # Define edges
    workflow.set_entry_point("collect")
    workflow.add_edge("collect", "classify")
    workflow.add_edge("classify", "save")
    workflow.add_edge("save", "export")
    workflow.add_edge("export", END)
    
    return workflow.compile()


def run_pipeline() -> dict:
    """Run the full pipeline and return results"""
    pipeline = create_pipeline()
    
    initial_state: PipelineState = {
        "search_results": [],
        "companies": [],
        "saved_count": 0,
        "duplicate_count": 0,
        "output_path": "",
        "errors": []
    }
    
    result = pipeline.invoke(initial_state)
    return result
