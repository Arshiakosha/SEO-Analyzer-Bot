#!/usr/bin/env python3
"""
SEO Bot - Free Local SEO Automation Tool
Run this script to start the SEO analysis
"""

import argparse
import json
import os
import sys
from datetime import datetime
from urllib.parse import urlparse

from crawler.sitemap_parser import WebsiteCrawler
from audit.seo_checker import SEOAuditor
from ai.content_generator import AIContentGenerator
from rank_checker.serp_checker import RankChecker
from config import OUTPUT_DIR

def main():
    parser = argparse.ArgumentParser(description='SEO Bot - Free Local SEO Automation Tool')
    parser.add_argument('url', help='Website URL to analyze')
    parser.add_argument('--keywords', '-k', nargs='+', help='Keywords to check rankings for')
    parser.add_argument('--pages', '-p', type=int, default=10, help='Number of pages to crawl (default: 10)')
    parser.add_argument('--ai', action='store_true', help='Generate AI suggestions')
    parser.add_argument('--output', '-o', choices=['json', 'console'], default='console', help='Output format')
    parser.add_argument('--dashboard', action='store_true', help='Launch Streamlit dashboard')
    
    args = parser.parse_args()
    
    if args.dashboard:
        launch_dashboard()
        return
    
    print("🔍 SEO Bot - Starting Analysis...")
    print(f"🌐 Target URL: {args.url}")
    print(f"📄 Pages to analyze: {args.pages}")
    print("=" * 50)
    
    try:
        # Step 1: Crawl website
        print("🕷️ Step 1: Crawling website...")
        crawler = WebsiteCrawler(args.url, args.pages)
        
        # Try sitemap first
        sitemap_urls = crawler.get_sitemap_urls()
        
        if sitemap_urls:
            print(f"✅ Found {len(sitemap_urls)} URLs in sitemap")
            pages_data = crawler.get_page_data(sitemap_urls)
        else:
            print("⚠️ No sitemap found, crawling manually...")
            pages_data = crawler.crawl_pages_manual()
        
        if not pages_data:
            print("❌ No pages could be crawled. Please check the URL.")
            return
        
        print(f"✅ Successfully crawled {len(pages_data)} pages")
        
        # Step 2: SEO Audit
        print("\n📊 Step 2: Running SEO audit...")
        auditor = SEOAuditor()
        audit_results = auditor.audit_multiple_pages(pages_data)
        print(f"✅ Audit complete - Average score: {audit_results['summary']['average_score']}/100")
        
        # Step 3: AI Suggestions (if requested)
        ai_suggestions = None
        if args.ai:
            print("\n🤖 Step 3: Generating AI suggestions...")
            ai_generator = AIContentGenerator()
            
            ai_suggestions = {}
            for page_data in pages_data[:3]:  # Limit to first 3 pages for demo
                url = page_data['url']
                print(f"  Generating suggestions for: {url}")
                
                ai_suggestions[url] = {
                    'title': ai_generator.generate_title_suggestion(page_data),
                    'meta_description': ai_generator.generate_meta_description(page_data),
                    'content': ai_generator.generate_content_suggestions(page_data)
                }
            
            print("✅ AI suggestions generated")
        
        # Step 4: Rank Checking (if keywords provided)
        rank_results = None
        if args.keywords:
            print(f"\n🔍 Step 4: Checking rankings for {len(args.keywords)} keywords...")
            domain = urlparse(args.url).netloc
            
            rank_checker = RankChecker()
            rank_results = rank_checker.check_multiple_keywords(domain, args.keywords)
            
            ranked_count = len([r for r in rank_results if r.get('rank')])
            print(f"✅ Rank check complete - {ranked_count}/{len(args.keywords)} keywords ranked")
        
        # Output results
        results = {
            'website_url': args.url,
            'analysis_date': datetime.now().isoformat(),
            'audit_results': audit_results,
            'ai_suggestions': ai_suggestions,
            'rank_results': rank_results
        }
        
        if args.output == 'json':
            output_to_json(results)
        else:
            output_to_console(results)
            
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        if '--debug' in sys.argv:
            raise

def output_to_console(results):
    """Output results to console in a readable format"""
    print("\n" + "="*60)
    print("📈 SEO ANALYSIS RESULTS")
    print("="*60)
    
    audit = results['audit_results']
    
    # Summary
    print(f"\n🎯 SUMMARY:")
    print(f"   • Overall Score: {audit['summary']['average_score']}/100")
    print(f"   • Pages Analyzed: {audit['summary']['total_pages']}")
    print(f"   • Total Issues: {audit['summary']['total_issues']}")
    
    # Common issues
    if audit['summary']['common_issues']:
        print(f"\n🚨 MOST COMMON ISSUES:")
        for issue, count in audit['summary']['common_issues'].items():
            print(f"   • {issue.title()}: {count} occurrences")
    
    # Page details
    print(f"\n📄 PAGE DETAILS:")
    for i, page in enumerate(audit['pages'][:5], 1):  # Show first 5 pages
        print(f"\n   {i}. {page['url']}")
        print(f"      Score: {page['overall_score']}/100")
        
        if page['issues']:
            print(f"      Issues: {', '.join(page['issues'][:3])}")
        else:
            print(f"      Issues: None")
    
    # AI suggestions
    if results['ai_suggestions']:
        print(f"\n🤖 AI SUGGESTIONS:")
        for url, suggestions in list(results['ai_suggestions'].items())[:2]:
            print(f"\n   URL: {url}")
            print(f"   Title: {suggestions['title'][:100]}...")
            print(f"   Meta: {suggestions['meta_description'][:100]}...")
    
    # Rankings
    if results['rank_results']:
        print(f"\n🔍 KEYWORD RANKINGS:")
        for result in results['rank_results']:
            rank_display = result.get('rank', 'Not Found')
            print(f"   • {result['keyword']}: Position {rank_display}")
    
    print(f"\n💾 Full results saved to: results/seo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

def output_to_json(results):
    """Save results to JSON file"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    filename = f"seo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Results saved to: {filepath}")

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    import subprocess
    import sys
    
    print("🚀 Launching SEO Bot Dashboard...")
    print("🌐 Dashboard will open in your browser at: http://localhost:8501")
    print("⚠️ Press Ctrl+C to stop the dashboard")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard/streamlit_app.py",
            "--server.port=8501",
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")

if __name__ == "__main__":
    main()