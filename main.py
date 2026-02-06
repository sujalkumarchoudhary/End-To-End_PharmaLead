"""
AI Pharma Lead Generation Platform
Main entry point for running the lead generation pipeline
"""
import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import SERPAPI_KEY, OPENAI_API_KEY, GROQ_API_KEY, LLM_PROVIDER
from pipeline.agent import run_pipeline


def print_banner():
    """Print application banner"""
    print("\n" + "="*60)
    print("🏭 AI PHARMA LEAD GENERATION PLATFORM")
    print("   Discover pharmaceutical companies that outsource manufacturing")
    print("="*60)


def check_config():
    """Check required configuration"""
    warnings = []
    info = []
    
    if not SERPAPI_KEY:
        warnings.append("⚠️  SERPAPI_KEY not set - Scrapers will not work")
    
    # Check LLM configuration
    if GROQ_API_KEY:
        info.append("✅ Using Groq (FREE) for AI classification")
    elif OPENAI_API_KEY:
        info.append("✅ Using OpenAI for AI classification")
    else:
        info.append("ℹ️  Using keyword-based classification (no LLM API)")
    
    if warnings:
        print("\n📋 Configuration Warnings:")
        for w in warnings:
            print(f"   {w}")
    
    if info:
        print("\n📋 Configuration:")
        for i in info:
            print(f"   {i}")
    
    print()
    return len(warnings) == 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Pharma Lead Generation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Run full pipeline
  python main.py --test-mode  # Run with limited queries for testing
        """
    )
    
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with limited queries"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check config
    config_ok = check_config()
    
    if args.test_mode:
        print("🧪 Running in TEST MODE (limited queries)\n")
        # Modify config for test mode
        import config.config as cfg
        cfg.SEARCH_KEYWORDS = cfg.SEARCH_KEYWORDS[:1]  # Only first keyword
        cfg.MAX_RESULTS_PER_KEYWORD = 5
        cfg.MAX_RESULTS_PER_DIRECTORY = 5
    
    # Run pipeline
    print("🚀 Starting pipeline...\n")
    
    try:
        result = run_pipeline()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 PIPELINE COMPLETE - SUMMARY")
        print("="*60)
        print(f"   📥 Raw results collected: {len(result.get('search_results', []))}")
        print(f"   🏢 Companies processed: {len(result.get('companies', []))}")
        print(f"   💾 New companies saved: {result.get('saved_count', 0)}")
        print(f"   ⏭️  Duplicates skipped: {result.get('duplicate_count', 0)}")
        
        if result.get("output_path"):
            print(f"\n   📤 CSV exported to: {result['output_path']}")
        
        errors = result.get("errors", [])
        if errors:
            print(f"\n   ⚠️  Errors encountered: {len(errors)}")
            for e in errors[:5]:  # Show first 5 errors
                print(f"      - {e}")
            if len(errors) > 5:
                print(f"      ... and {len(errors) - 5} more")
        
        print("\n" + "="*60)
        print("✅ Done! Check the output folder for your leads CSV.")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        print("   Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
