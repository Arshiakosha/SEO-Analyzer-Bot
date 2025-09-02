import requests
import json
import os  # <-- Added for env var support
from config import FREE_AI_ENDPOINTS

# Always get your OpenRouter key from the environment, never hardcode
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

class AIContentGenerator:
    def __init__(self):
        self.available_endpoints = []
        self._check_available_endpoints()
    
    def _check_available_endpoints(self):
        """Check which AI endpoints are available"""
        # Check if local LMStudio is running
        try:
            response = requests.get(FREE_AI_ENDPOINTS['local'].replace('/v1/chat/completions', '/v1/models'), 
                                  timeout=5)
            if response.status_code == 200:
                self.available_endpoints.append('local')
                print("✅ Local LMStudio detected")
        except:
            pass
        
        # Check OpenRouter if API key is provided
        if OPENROUTER_KEY:
            self.available_endpoints.append('openrouter')
            print("✅ OpenRouter API key detected")
        
        if not self.available_endpoints:
            print("⚠️  No AI endpoints available. Install LMStudio or add OpenRouter API key for AI suggestions.")
    
    def generate_title_suggestion(self, page_data, target_keyword=None):
        """Generate SEO-optimized title suggestions"""
        if not self.available_endpoints:
            return "AI not available - consider installing LMStudio or adding API keys"
        
        current_title = page_data.get('title', 'No title')
        url = page_data.get('url', '')
        word_count = page_data.get('word_count', 0)
        
        prompt = f"""
        Generate an SEO-optimized title tag for this webpage:
        - Current title: "{current_title}"
        - URL: {url}
        - Content length: {word_count} words
        - Target keyword: {target_keyword or 'not specified'}
        
        Requirements:
        - 100-250 characters long
        - Include target keyword if provided
        - Compelling and click-worthy
        - Accurately describe the content
        
        Return only the suggested title, no explanations.
        """
        
        return self._call_ai_endpoint(prompt)
    
    def generate_meta_description(self, page_data, target_keyword=None):
        """Generate SEO-optimized meta description"""
        if not self.available_endpoints:
            return "AI not available - consider installing LMStudio or adding API keys"
        
        title = page_data.get('title', 'No title')
        url = page_data.get('url', '')
        h1_tags = page_data.get('h1_tags', [])
        
        prompt = f"""
        Generate an SEO-optimized meta description for this webpage:
        - Title: "{title}"
        - URL: {url}
        - Main heading: "{h1_tags[0] if h1_tags else 'No H1'}"
        - Target keyword: {target_keyword or 'not specified'}
        
        Requirements:
        - 250-500 characters long
        - Include target keyword naturally if provided
        - Compelling call-to-action
        - Accurately summarize the page content
        
        Return only the suggested meta description, no explanations.
        """
        
        return self._call_ai_endpoint(prompt)
    
    def generate_content_suggestions(self, page_data, content_type="blog"):
        """Generate content improvement suggestions"""
        if not self.available_endpoints:
            return "AI not available - consider installing LMStudio or adding API keys"
        
        title = page_data.get('title', 'No title')
        word_count = page_data.get('word_count', 0)
        h1_tags = page_data.get('h1_tags', [])
        h2_tags = page_data.get('h2_tags', [])
        
        prompt = f"""
        Analyze this webpage and suggest content improvements:
        - Title: "{title}"
        - Current word count: {word_count}
        - H1: {h1_tags[0] if h1_tags else 'Missing'}
        - H2 tags: {', '.join(h2_tags[:3]) if h2_tags else 'None'}
        - Content type: {content_type}
        
        Provide 3-5 specific suggestions to improve SEO and user engagement:
        1. Content structure improvements
        2. Additional topics to cover
        3. SEO optimization tips
        
        Keep suggestions actionable and specific.
        """
        
        return self._call_ai_endpoint(prompt)
    
    def _call_ai_endpoint(self, prompt):
        """Call available AI endpoint with the given prompt"""
        if 'openrouter' in self.available_endpoints:
            return self._call_openrouter(prompt)
        elif 'local' in self.available_endpoints:
            return self._call_local_ai(prompt)
        else:
            return "No AI endpoint available"
    
    def _call_local_ai(self, prompt):
        """Call local LMStudio endpoint"""
        try:
            response = requests.post(
                FREE_AI_ENDPOINTS['local'],
                json={
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                return f"AI Error: {response.status_code}"
                
        except Exception as e:
            return f"AI Error: {str(e)}"
    
    def _call_openrouter(self, prompt):
        """Call OpenRouter API"""
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/mistral-large",  # Or your preferred model
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                return f"AI Error: {response.status_code}: {response.text}"
        except Exception as e:
            return f"AI Error: {str(e)}"

    def generate_bulk_keywords(self, page_data, target_keyword=None, num_keywords=30):
        """Generate a bulk list of SEO keywords using AI"""
        prompt = f"""
        Generate a list of at least {num_keywords} highly relevant SEO keywords for the following page:
        - Title: "{page_data.get('title', '')}"
        - Meta Description: "{page_data.get('meta_description', '')}"
        - Main Heading: "{page_data.get('h1_tags', [''])[0]}"
        - Target Keyword: {target_keyword or 'not specified'}

        Return the keywords as a plain, comma-separated list, no explanations.
        """
        result = self._call_ai_endpoint(prompt)
        # Split by comma and strip whitespace
        keywords = [k.strip() for k in result.split(",") if k.strip()]
        return keywords