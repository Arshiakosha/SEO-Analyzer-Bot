# SEO Bot - Free Local SEO Automation Tool

A lightweight, free SEO automation tool that runs entirely on your localhost. Analyze websites, check rankings, and get AI-powered suggestions without any costs.

##  Features

-  **Website Crawler**: Extract pages from sitemap.xml or crawl manually
- **SEO Auditor**: Check titles, meta descriptions, headings, content quality
-  **AI Suggestions**: Generate optimized titles and meta descriptions (optional)
-  **Rank Checker**: Check keyword positions on Google
-  **Dashboard**: Beautiful Streamlit web interface
-  **Export**: JSON and CSV reports
-  **100% Free**: No API costs, runs locally

## Quick Start

### 1. Install Dependencies

```bash
# Clone or download the project
cd seo-bot

# Install required packages
pip install -r requirements.txt
```

### 2. Run Analysis (Command Line)

```bash
# Basic SEO audit
python main.py https://example.com

# With keyword ranking check
python main.py https://example.com --keywords "SEO tools" "website audit"

# With AI suggestions (requires LMStudio or API key)
python main.py https://example.com --ai

# Limit pages and save to JSON
python main.py https://example.com --pages 5 --output json
```

### 3. Launch Web Dashboard

```bash
# Start the dashboard
python main.py --dashboard

# Or directly with streamlit
streamlit run dashboard/streamlit_app.py
```

Then open http://localhost:8501 in your browser.

## 🛠️ Configuration

### AI Setup (Optional)

For AI suggestions, you can use:

1. **LMStudio (Free, Local)**:
   - Download from https://lmstudio.ai
   - Load a model (e.g., DeepSeek, Mixtral)
   - Start the local server on port 1234

2. **OpenRouter (Free Tier)**:
   - Get API key from https://openrouter.ai
   - Set environment variable: `export OPENROUTER_KEY=your_key`

### Rank Checking

- **Free**: Uses web scraping (be respectful, limited requests)
- **Paid**: Add SerpAPI key for more reliable results
  - Get key from https://serpapi.com
  - Set: `export SERPAPI_KEY=your_key`

## Project Structure

```
seo-bot/
├── crawler/          # Website crawling logic
├── audit/           # SEO audit rules
├── ai/              # AI content generation
├── rank_checker/    # Keyword ranking
├── dashboard/       # Streamlit web UI
├── results/         # Output files
├── main.py          # Command line interface
└── config.py        # Configuration
```

## Example Output

```json
{
  "url": "https://example.com/blog/post",
  "overall_score": 75,
  "issues": [
    "Meta description too short (89 characters)",
    "2 images missing alt text"
  ],
  "recommendations": [
    "Expand meta description to 150-160 characters",
    "Add descriptive alt text to all images"
  ],
  "ai_suggestions": {
    "title": "Complete Guide to SEO Optimization - Boost Rankings in 2024",
    "meta_description": "Learn proven SEO strategies to improve your website rankings..."
  },
  "keyword_rank": {
    "SEO optimization": 15
  }
}
```

## 🔧 Troubleshooting

**Common Issues:**

1. **"No pages found"**: Check if URL is accessible and has sitemap.xml
2. **AI not working**: Install L
3. If google sign in doesent work its normal just register (will be fixed in V2.0) and official release
