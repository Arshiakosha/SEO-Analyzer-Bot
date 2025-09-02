import re
from urllib.parse import urlparse

class SEOAuditor:
    def __init__(self):
        self.issues = []
        self.recommendations = []
    
    def audit_page(self, page_data):
        """Perform comprehensive SEO audit on a single page"""
        url = page_data['url']
        audit_results = {
            'url': url,
            'issues': [],
            'recommendations': [],
            'scores': {},
            'seo_data': {}
        }
        
        # Title Tag Analysis
        title_score, title_issues, title_recs = self._audit_title(page_data)
        audit_results['scores']['title'] = title_score
        audit_results['issues'].extend(title_issues)
        audit_results['recommendations'].extend(title_recs)
        
        # Meta Description Analysis
        meta_score, meta_issues, meta_recs = self._audit_meta_description(page_data)
        audit_results['scores']['meta_description'] = meta_score
        audit_results['issues'].extend(meta_issues)
        audit_results['recommendations'].extend(meta_recs)
        
        # Heading Tags Analysis
        heading_score, heading_issues, heading_recs = self._audit_headings(page_data)
        audit_results['scores']['headings'] = heading_score
        audit_results['issues'].extend(heading_issues)
        audit_results['recommendations'].extend(heading_recs)
        
        # Content Analysis
        content_score, content_issues, content_recs = self._audit_content(page_data)
        audit_results['scores']['content'] = content_score
        audit_results['issues'].extend(content_issues)
        audit_results['recommendations'].extend(content_recs)
        
        # Images Analysis
        image_score, image_issues, image_recs = self._audit_images(page_data)
        audit_results['scores']['images'] = image_score
        audit_results['issues'].extend(image_issues)
        audit_results['recommendations'].extend(image_recs)
        
        # Links Analysis
        link_score, link_issues, link_recs = self._audit_links(page_data)
        audit_results['scores']['links'] = link_score
        audit_results['issues'].extend(link_issues)
        audit_results['recommendations'].extend(link_recs)
        
        # Calculate Overall Score
        audit_results['overall_score'] = self._calculate_overall_score(audit_results['scores'])
        
        # Store SEO data for AI suggestions
        audit_results['seo_data'] = {
            'title': page_data.get('title'),
            'meta_description': page_data.get('meta_description'),
            'h1_tags': page_data.get('h1_tags', []),
            'word_count': page_data.get('word_count', 0),
            'url': url
        }
        
        return audit_results
    
    def _audit_title(self, page_data):
        """Audit title tag"""
        title = page_data.get('title')
        issues = []
        recommendations = []
        score = 100
        
        if not title:
            issues.append("Missing title tag")
            recommendations.append("Add a descriptive title tag (50-60 characters)")
            score = 0
        else:
            title_length = len(title)
            if title_length < 30:
                issues.append(f"Title too short ({title_length} characters)")
                recommendations.append("Expand title to 50-60 characters for better SEO")
                score -= 30
            elif title_length > 60:
                issues.append(f"Title too long ({title_length} characters)")
                recommendations.append("Shorten title to under 60 characters to avoid truncation")
                score -= 20
            
            # Check for duplicate words
            words = title.lower().split()
            if len(words) != len(set(words)):
                issues.append("Title contains duplicate words")
                recommendations.append("Remove duplicate words from title")
                score -= 10
        
        return max(score, 0), issues, recommendations
    
    def _audit_meta_description(self, page_data):
        """Audit meta description"""
        meta_desc = page_data.get('meta_description')
        issues = []
        recommendations = []
        score = 100
        
        if not meta_desc:
            issues.append("Missing meta description")
            recommendations.append("Add a compelling meta description (150-160 characters)")
            score = 0
        else:
            desc_length = len(meta_desc)
            if desc_length < 120:
                issues.append(f"Meta description too short ({desc_length} characters)")
                recommendations.append("Expand meta description to 150-160 characters")
                score -= 30
            elif desc_length > 160:
                issues.append(f"Meta description too long ({desc_length} characters)")
                recommendations.append("Shorten meta description to under 160 characters")
                score -= 20
        
        return max(score, 0), issues, recommendations
    
    def _audit_headings(self, page_data):
        """Audit heading structure"""
        h1_tags = page_data.get('h1_tags', [])
        h2_tags = page_data.get('h2_tags', [])
        issues = []
        recommendations = []
        score = 100
        
        if not h1_tags:
            issues.append("Missing H1 tag")
            recommendations.append("Add exactly one H1 tag to define the main topic")
            score -= 40
        elif len(h1_tags) > 1:
            issues.append(f"Multiple H1 tags found ({len(h1_tags)})")
            recommendations.append("Use only one H1 tag per page")
            score -= 30
        else:
            h1_text = h1_tags[0]
            if len(h1_text) < 20:
                issues.append("H1 tag too short")
                recommendations.append("Make H1 more descriptive (20-70 characters)")
                score -= 15
            elif len(h1_text) > 70:
                issues.append("H1 tag too long")
                recommendations.append("Shorten H1 to under 70 characters")
                score -= 10
        
        if not h2_tags:
            recommendations.append("Consider adding H2 tags to structure your content")
            score -= 10
        
        return max(score, 0), issues, recommendations
    
    def _audit_content(self, page_data):
        """Audit content quality"""
        word_count = page_data.get('word_count', 0)
        issues = []
        recommendations = []
        score = 100
        
        if word_count < 300:
            issues.append(f"Low word count ({word_count} words)")
            recommendations.append("Add more content (aim for 300+ words minimum)")
            score -= 40
        elif word_count < 500:
            recommendations.append("Consider expanding content to 500+ words for better SEO")
            score -= 15
        
        return max(score, 0), issues, recommendations
    
    def _audit_images(self, page_data):
        """Audit image optimization"""
        total_images = page_data.get('images', 0)
        images_without_alt = page_data.get('images_without_alt', 0)
        issues = []
        recommendations = []
        score = 100
        
        if total_images > 0:
            if images_without_alt > 0:
                issues.append(f"{images_without_alt} images missing alt text")
                recommendations.append("Add descriptive alt text to all images")
                score -= min(40, images_without_alt * 10)
        else:
            recommendations.append("Consider adding relevant images to enhance content")
            score -= 5
        
        return max(score, 0), issues, recommendations
    
    def _audit_links(self, page_data):
        """Audit internal and external links"""
        internal_links = page_data.get('internal_links', 0)
        external_links = page_data.get('external_links', 0)
        issues = []
        recommendations = []
        score = 100
        
        if internal_links == 0:
            recommendations.append("Add internal links to improve site navigation")
            score -= 15
        
        if external_links == 0:
            recommendations.append("Consider adding relevant external links to authoritative sources")
            score -= 10
        
        return max(score, 0), issues, recommendations
    
    def _calculate_overall_score(self, scores):
        """Calculate overall SEO score"""
        if not scores:
            return 0
        
        weights = {
            'title': 0.25,
            'meta_description': 0.20,
            'headings': 0.20,
            'content': 0.15,
            'images': 0.10,
            'links': 0.10
        }
        
        weighted_score = 0
        total_weight = 0
        
        for category, score in scores.items():
            if category in weights:
                weighted_score += score * weights[category]
                total_weight += weights[category]
        
        return round(weighted_score / total_weight if total_weight > 0 else 0, 1)
    
    def audit_multiple_pages(self, pages_data):
        """Audit multiple pages and return consolidated results"""
        results = {
            'pages': [],
            'summary': {
                'total_pages': len(pages_data),
                'average_score': 0,
                'common_issues': {},
                'total_issues': 0
            }
        }
        
        total_score = 0
        all_issues = []
        
        for page_data in pages_data:
            page_audit = self.audit_page(page_data)
            results['pages'].append(page_audit)
            total_score += page_audit['overall_score']
            all_issues.extend(page_audit['issues'])
        
        # Calculate summary statistics
        if pages_data:
            results['summary']['average_score'] = round(total_score / len(pages_data), 1)
        
        # Find common issues
        issue_counts = {}
        for issue in all_issues:
            issue_type = issue.split(' ')[0].lower()  # Get first word as issue type
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        results['summary']['common_issues'] = dict(sorted(issue_counts.items(), 
                                                         key=lambda x: x[1], reverse=True)[:5])
        results['summary']['total_issues'] = len(all_issues)
        
        return results