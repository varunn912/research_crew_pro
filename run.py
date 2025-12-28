#!/usr/bin/env python3
"""
Enhanced CLI runner for AutoResearch Crew with provider selection
"""

import argparse
import os
from dotenv import load_dotenv
from src.crew import ResearchCrew
from src.utils import validate_env_variables
from src.llm import LLMManager

def main():
    """Main CLI entry point."""
    
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='AutoResearch Crew - AI-Powered Research Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py "Python programming basics"
  python run.py "AI in healthcare" --language es --audio
  python run.py "Climate change" --provider groq --pdf

Available Providers:
  openai      OpenAI GPT models (requires payment)
  groq        Groq (fast & free) ⭐ RECOMMENDED
  anthropic   Anthropic Claude (has free tier)
  ollama      Local Ollama (100% free)
        """
    )
    
    parser.add_argument(
        'topic',
        type=str,
        help='Research topic to investigate'
    )
    parser.add_argument(
        '--language',
        type=str,
        default='en',
        help='Output language (en, es, fr, de, etc.)'
    )
    parser.add_argument(
        '--provider',
        type=str,
        choices=['openai', 'groq', 'anthropic', 'ollama', 'auto'],
        default=None,
        help='LLM provider to use'
    )
    parser.add_argument(
        '--audio',
        action='store_true',
        help='Generate audio report (TTS)'
    )
    parser.add_argument(
        '--pdf',
        action='store_true',
        help='Generate PDF report'
    )
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Run setup wizard for LLM providers'
    )
    
    args = parser.parse_args()
    
    # Run setup wizard if requested
    if args.setup:
        os.system('python setup_llm.py')
        return 0
    
    # Show available providers
    print("\n" + "="*80)
    print("🧠 AutoResearch Crew - Enhanced Edition")
    print("="*80)
    
    llm_manager = LLMManager()
    provider_info = llm_manager.get_provider_info()
    
    print(f"\n🤖 Available Providers: {', '.join(provider_info['active_providers'])}")
    
    if not provider_info['active_providers']:
        print("\n❌ No LLM providers configured!")
        print("\n🚀 Quick Setup Options:")
        print("\n1. Groq (Recommended - Fast & Free):")
        print("   python run.py --setup")
        print("\n2. Ollama (Local - 100% Free):")
        print("   - Install: curl https://ollama.ai/install.sh | sh")
        print("   - Run: ollama pull llama3")
        print("\n3. OpenAI:")
        print("   - Add OPENAI_API_KEY to .env")
        return 1
    
    # Validate minimum requirements
    if not os.getenv('TAVILY_API_KEY') or os.getenv('TAVILY_API_KEY').startswith('your_'):
        print("\n⚠️  Warning: TAVILY_API_KEY not configured")
        print("   Web search may not work. Get free key at: https://tavily.com")
    
    # Set provider if specified
    if args.provider:
        os.environ['LLM_PROVIDER'] = args.provider
        print(f"\n📌 Using provider: {args.provider}")
    
    print(f"\n📋 Topic: {args.topic}")
    print(f"🌍 Language: {args.language}")
    print(f"🎤 Audio: {'Yes' if args.audio else 'No'}")
    print(f"📄 PDF: {'Yes' if args.pdf else 'No'}")
    print()
    
    try:
        # Initialize and run crew
        crew = ResearchCrew(
            topic=args.topic,
            language=args.language,
            enable_audio=args.audio
        )
        
        results = crew.run()
        
        print("\n" + "="*80)
        print("✅ Research Complete!")
        print("="*80)
        print(f"\n📄 Report: {results['report_path']}")
        
        if results.get('pdf_path'):
            print(f"📄 PDF: {results['pdf_path']}")
        
        if results.get('audio_path'):
            print(f"🎤 Audio: {results['audio_path']}")
        
        if results.get('google_docs_url'):
            print(f"📤 Google Docs: {results['google_docs_url']}")
        
        if results.get('notion_url'):
            print(f"📤 Notion: {results['notion_url']}")
        
        print(f"\n⏱️  Duration: {results['duration']:.2f}s")
        print(f"💾 Database ID: {results['db_record_id']}")
        print("\n✨ All done!\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check your API keys in .env")
        print("2. Try a different provider: python run.py --setup")
        print("3. Use Groq (free): GROQ_API_KEY in .env")
        print("4. Use Ollama (local): ollama pull llama3")
        return 1

if __name__ == "__main__":
    exit(main())