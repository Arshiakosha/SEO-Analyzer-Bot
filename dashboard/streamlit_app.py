import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import sys

from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler.sitemap_parser import WebsiteCrawler
from audit.seo_checker import SEOAuditor
from ai.content_generator import AIContentGenerator
from rank_checker.serp_checker import RankChecker
from keyword_utils import extract_keywords_from_text

st.set_page_config(
    page_title="SEO Bot Dashboard",
    page_icon="🔍",
    layout="wide"
)

def main():
    st.title("🔍 SEO Bot Dashboard")
    st.markdown("---")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        company_description = st.text_input(
            "Describe your business (optional)",
            placeholder="E.g. HVAC company that sells heating and cooling products"
        )

        website_url = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            help="Enter the website URL to analyze"
        )

        use_ai_for_keywords = st.checkbox("Use AI for keyword suggestions", value=False)

        suggested_keywords = []
        ai_keywords = []
        extraction_error = ""
        homepage_data = None

        if website_url:
            try:
                crawler = WebsiteCrawler(website_url, crawl_limit=1)
                homepage_urls = [website_url]
                homepage_data = crawler.get_page_data(homepage_urls)

                if homepage_data and isinstance(homepage_data, list) and 'seo_data' in homepage_data[0]:
                    homepage_text = homepage_data[0]['seo_data'].get('title', '')
                    homepage_text += " " + homepage_data[0]['seo_data'].get('meta_description', '')
                    homepage_text += " " + " ".join(homepage_data[0]['seo_data'].get('h1_tags', []))
                    combined_text = (company_description or "") + " " + homepage_text

                    if use_ai_for_keywords:
                        try:
                            ai_gen = AIContentGenerator()
                            ai_keywords = ai_gen.generate_bulk_keywords(
                                homepage_data[0]['seo_data'], 
                                target_keyword=None,
                                num_keywords=30
                            )
                        except Exception as e:
                            extraction_error = f"Could not generate AI keywords: {e}"
                    else:
                        try:
                            suggested_keywords = extract_keywords_from_text(combined_text)
                        except Exception as e:
                            extraction_error = f"Could not auto-extract keywords: {e}"
                else:
                    extraction_error = "Crawler did not return SEO data for this page (no 'seo_data' key)."
            except Exception as e:
                extraction_error = f"Could not auto-extract keywords: {e}"

        # Only show warning if there's an error
        if extraction_error:
            st.warning(extraction_error)

        # Prefer AI keywords if user selected
        keywords_to_show = ai_keywords if use_ai_for_keywords and ai_keywords else suggested_keywords

        keywords_input = st.text_area(
            "Keywords (one per line)",
            value="\n".join(keywords_to_show) if keywords_to_show else "",
            placeholder="SEO tools\nwebsite optimization\ndigital marketing",
            help="Edit or add keywords to check rankings for"
        )
        
        st.subheader("Options")
        crawl_limit = st.slider("Pages to crawl", min_value=1, max_value=50, value=10)
        use_ai = st.checkbox("Generate AI suggestions for SEO improvements", value=True)
        check_rankings = st.checkbox("Check keyword rankings", value=True)
        run_analysis = st.button("🚀 Run SEO Analysis", type="primary")
    
    # Main content area
    if run_analysis and website_url:
        run_seo_analysis(website_url, keywords_input, crawl_limit, use_ai, check_rankings)
    else:
        show_welcome_screen()

def show_welcome_screen():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### 🕷️ Website Crawler
        - Extracts pages from sitemap.xml
        - Analyzes page structure
        - Gathers SEO data
        """)
    with col2:
        st.markdown("""
        ### 📊 SEO Auditor
        - Checks title tags & meta descriptions
        - Analyzes heading structure
        - Reviews content quality
        """)
    with col3:
        st.markdown("""
        ### 🤖 AI Assistant
        - Generates SEO suggestions
        - Creates optimized titles
        - Improves meta descriptions
        """)
    st.markdown("---")
    st.info("👈 Enter a website URL in the sidebar to get started!")

def run_seo_analysis(website_url, keywords_input, crawl_limit, use_ai, check_rankings):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Crawl website
        status_text.text("🕷️ Crawling website...")
        progress_bar.progress(10)
        crawler = WebsiteCrawler(website_url, crawl_limit)
        sitemap_urls = crawler.get_sitemap_urls()
        
        if sitemap_urls:
            st.success(f"✅ Found {len(sitemap_urls)} URLs in sitemap")
            pages_data = crawler.get_page_data(sitemap_urls)
        else:
            st.warning("⚠️ No sitemap found, crawling manually...")
            pages_data = crawler.crawl_pages_manual()
        
        if not pages_data:
            st.error("❌ No pages could be crawled. Please check the URL.")
            return
        
        progress_bar.progress(30)
        
        # Step 2: SEO Audit
        status_text.text("📊 Running SEO audit...")
        auditor = SEOAuditor()
        audit_results = auditor.audit_multiple_pages(pages_data)
        progress_bar.progress(50)
        
        # Step 3: AI Suggestions (if enabled)
        ai_suggestions = None
        if use_ai:
            status_text.text("🤖 Generating AI suggestions...")
            ai_generator = AIContentGenerator()
            ai_suggestions = generate_ai_suggestions(ai_generator, pages_data[:3])  # Limit to first 3 pages
        
        progress_bar.progress(70)
        
        # Step 4: Rank Checking (if enabled)
        rank_results = None
        if check_rankings and keywords_input.strip():
            status_text.text("🔍 Checking keyword rankings...")
            keywords = [k.strip() for k in keywords_input.strip().split('\n') if k.strip()]
            domain = website_url.replace('https://', '').replace('http://', '').split('/')[0]
            rank_checker = RankChecker()
            rank_results = rank_checker.check_multiple_keywords(domain, keywords)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        # Display results
        display_results(audit_results, ai_suggestions, rank_results, website_url)
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.exception(e)

def generate_ai_suggestions(ai_generator, pages_data):
    suggestions = {}
    for page_data in pages_data:
        url = page_data['url']
        suggestions[url] = {
            'title': ai_generator.generate_title_suggestion(page_data),
            'meta_description': ai_generator.generate_meta_description(page_data),
            'content': ai_generator.generate_content_suggestions(page_data)
        }
    return suggestions

def display_results(audit_results, ai_suggestions, rank_results, website_url):
    st.header("📈 SEO Analysis Results")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Overall Score",
            f"{audit_results['summary']['average_score']}/100",
            delta=None
        )
    with col2:
        st.metric(
            "Pages Analyzed",
            audit_results['summary']['total_pages']
        )
    with col3:
        st.metric(
            "Total Issues",
            audit_results['summary']['total_issues']
        )
    with col4:
        if rank_results:
            ranked_count = len([r for r in rank_results if r.get('rank')])
            st.metric(
                "Keywords Ranked",
                f"{ranked_count}/{len(rank_results)}"
            )
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Page Analysis", "🤖 AI Suggestions", "🔍 Rankings", "📋 Export"])
    with tab1:
        display_page_analysis(audit_results)
    with tab2:
        if ai_suggestions:
            display_ai_suggestions(ai_suggestions)
        else:
            st.info("AI suggestions were not generated for this analysis.")
    with tab3:
        if rank_results:
            display_rankings(rank_results)
        else:
            st.info("Keyword rankings were not checked for this analysis.")
    with tab4:
        display_export_options(audit_results, ai_suggestions, rank_results, website_url)

def display_page_analysis(audit_results):
    if audit_results['summary']['common_issues']:
        st.subheader("🚨 Most Common Issues")
        issue_df = pd.DataFrame([
            {'Issue Type': issue.title(), 'Count': count}
            for issue, count in audit_results['summary']['common_issues'].items()
        ])
        st.bar_chart(issue_df.set_index('Issue Type'))
    st.subheader("📄 Individual Page Analysis")
    for i, page in enumerate(audit_results['pages']):
        with st.expander(f"Page {i+1}: {page['url']}", expanded=i == 0):
            score_color = "green" if page['overall_score'] >= 80 else "orange" if page['overall_score'] >= 60 else "red"
            st.markdown(f"**Overall Score: <span style='color:{score_color}'>{page['overall_score']}/100</span>**", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if page['issues']:
                    st.markdown("**❌ Issues Found:**")
                    for issue in page['issues']:
                        st.markdown(f"• {issue}")
                else:
                    st.success("✅ No major issues found!")
            with col2:
                if page['recommendations']:
                    st.markdown("**💡 Recommendations:**")
                    for rec in page['recommendations']:
                        st.markdown(f"• {rec}")
            st.markdown("**Current SEO Data:**")
            seo_data = page['seo_data']
            st.write(f"**Title:** {seo_data.get('title', 'Not found')}")
            st.write(f"**Meta Description:** {seo_data.get('meta_description', 'Not found')}")
            st.write(f"**H1 Tags:** {', '.join(seo_data.get('h1_tags', ['None']))}")
            st.write(f"**Word Count:** {seo_data.get('word_count', 0)}")

def display_ai_suggestions(ai_suggestions):
    st.subheader("🤖 AI-Generated SEO Suggestions")
    for url, suggestions in ai_suggestions.items():
        with st.expander(f"Suggestions for: {url}"):
            st.markdown("**🏷️ Suggested Title:**")
            st.info(suggestions['title'])
            st.markdown("**📝 Suggested Meta Description:**")
            st.info(suggestions['meta_description'])
            st.markdown("**💡 Content Suggestions:**")
            st.info(suggestions['content'])

def display_rankings(rank_results):
    st.subheader("🔍 Keyword Ranking Results")
    ranking_data = []
    for result in rank_results:
        ranking_data.append({
            'Keyword': result['keyword'],
            'Rank': result.get('rank', 'Not Found'),
            'URL': result.get('url', ''),
            'Title': result.get('title', ''),
            'Method': result.get('method', 'scraping')
        })
    df = pd.DataFrame(ranking_data)
    st.dataframe(df, use_container_width=True)
    ranked_keywords = [r for r in rank_results if r.get('rank')]
    if ranked_keywords:
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_rank = sum(r['rank'] for r in ranked_keywords) / len(ranked_keywords)
            st.metric("Average Rank", f"{avg_rank:.1f}")
        with col2:
            best_rank = min(r['rank'] for r in ranked_keywords)
            st.metric("Best Rank", best_rank)
        with col3:
            top_10_count = len([r for r in ranked_keywords if r['rank'] <= 10])
            st.metric("Top 10 Rankings", top_10_count)

def display_export_options(audit_results, ai_suggestions, rank_results, website_url):
    st.subheader("📋 Export Results")
    export_data = {
        'website_url': website_url,
        'analysis_date': datetime.now().isoformat(),
        'audit_results': audit_results,
        'ai_suggestions': ai_suggestions,
        'rank_results': rank_results
    }
    json_data = json.dumps(export_data, indent=2)
    st.download_button(
        label="📄 Download JSON Report",
        data=json_data,
        file_name=f"seo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
    if audit_results['pages']:
        csv_data = []
        for page in audit_results['pages']:
            csv_data.append({
                'URL': page['url'],
                'Overall Score': page['overall_score'],
                'Issues Count': len(page['issues']),
                'Issues': '; '.join(page['issues']),
                'Recommendations': '; '.join(page['recommendations']),
                'Title': page['seo_data'].get('title', ''),
                'Meta Description': page['seo_data'].get('meta_description', ''),
                'H1 Tags': '; '.join(page['seo_data'].get('h1_tags', [])),
                'Word Count': page['seo_data'].get('word_count', 0)
            })
        csv_df = pd.DataFrame(csv_data)
        csv_string = csv_df.to_csv(index=False)
        st.download_button(
            label="📊 Download CSV Report",
            data=csv_string,
            file_name=f"seo_pages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()