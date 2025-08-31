"""
SEO Audit Script for CloudFace AI
This script performs a comprehensive audit of all SEO elements across the website.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

class SEOAuditor:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.templates_dir = self.project_root / "templates"
        self.results = {
            "overall_score": 0,
            "page_scores": {},
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "missing_elements": [],
            "performance_issues": []
        }

    def check_meta_tags(self, html_content: str, page_name: str) -> Dict[str, Any]:
        """Check meta tags implementation"""
        issues = []
        score = 100
        
        # Required meta tags
        required_tags = {
            "charset": r'<meta charset="[^"]*"',
            "viewport": r'<meta name="viewport"[^>]*>',
            "title": r'<title>[^<]+</title>',
            "description": r'<meta name="description"[^>]*>',
            "keywords": r'<meta name="keywords"[^>]*>',
            "author": r'<meta name="author"[^>]*>',
            "robots": r'<meta name="robots"[^>]*>'
        }
        
        for tag_name, pattern in required_tags.items():
            if not re.search(pattern, html_content, re.IGNORECASE):
                issues.append(f"Missing {tag_name} meta tag")
                score -= 15
        
        # Open Graph tags
        og_tags = {
            "og:type": r'<meta property="og:type"[^>]*>',
            "og:title": r'<meta property="og:title"[^>]*>',
            "og:description": r'<meta property="og:description"[^>]*>',
            "og:url": r'<meta property="og:url"[^>]*>',
            "og:image": r'<meta property="og:image"[^>]*>'
        }
        
        for og_tag, pattern in og_tags.items():
            if not re.search(pattern, html_content, re.IGNORECASE):
                issues.append(f"Missing {og_tag} tag")
                score -= 10
        
        # Twitter Card tags
        twitter_tags = {
            "twitter:card": r'<meta property="twitter:card"[^>]*>',
            "twitter:title": r'<meta property="twitter:title"[^>]*>',
            "twitter:description": r'<meta property="twitter:description"[^>]*>'
        }
        
        for twitter_tag, pattern in twitter_tags.items():
            if not re.search(pattern, html_content, re.IGNORECASE):
                issues.append(f"Missing {twitter_tag} tag")
                score -= 8
        
        # Canonical URL
        if not re.search(r'<link rel="canonical"[^>]*>', html_content, re.IGNORECASE):
            issues.append("Missing canonical URL")
            score -= 12
        
        # Favicon
        if not re.search(r'<link rel="(icon|shortcut icon)"[^>]*>', html_content, re.IGNORECASE):
            issues.append("Missing favicon")
            score -= 5
        
        return {
            "score": max(0, score),
            "issues": issues,
            "total_issues": len(issues)
        }

    def check_structured_data(self, html_content: str) -> Dict[str, Any]:
        """Check structured data implementation"""
        issues = []
        score = 100
        
        # Check for JSON-LD scripts
        json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
        json_ld_blocks = re.findall(json_ld_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        if not json_ld_blocks:
            issues.append("No structured data (JSON-LD) found")
            score -= 50
        else:
            # Validate JSON structure
            for i, block in enumerate(json_ld_blocks):
                try:
                    data = json.loads(block.strip())
                    if "@type" not in data:
                        issues.append(f"Structured data block {i+1} missing @type")
                        score -= 20
                except json.JSONDecodeError:
                    issues.append(f"Invalid JSON in structured data block {i+1}")
                    score -= 30
        
        return {
            "score": max(0, score),
            "issues": issues,
            "total_issues": len(issues),
            "blocks_found": len(json_ld_blocks)
        }

    def check_performance_elements(self, html_content: str) -> Dict[str, Any]:
        """Check performance optimization elements"""
        issues = []
        score = 100
        
        # Preconnect links
        if not re.search(r'<link rel="preconnect"[^>]*>', html_content, re.IGNORECASE):
            issues.append("Missing preconnect links for external resources")
            score -= 15
        
        # DNS prefetch
        if not re.search(r'<link rel="dns-prefetch"[^>]*>', html_content, re.IGNORECASE):
            issues.append("Missing DNS prefetch links")
            score -= 10
        
        # Critical CSS (inline styles)
        if not re.search(r'<style[^>]*>', html_content, re.IGNORECASE):
            issues.append("No inline critical CSS found")
            score -= 10
        
        return {
            "score": max(0, score),
            "issues": issues,
            "total_issues": len(issues)
        }

    def check_content_optimization(self, html_content: str) -> Dict[str, Any]:
        """Check content optimization elements"""
        issues = []
        score = 100
        
        # Heading structure
        headings = re.findall(r'<h([1-6])[^>]*>', html_content, re.IGNORECASE)
        if not headings:
            issues.append("No headings found")
            score -= 30
        else:
            # Check for H1
            if '1' not in headings:
                issues.append("No H1 heading found")
                score -= 20
            
            # Check heading hierarchy
            if len(headings) > 1:
                for i in range(len(headings) - 1):
                    if int(headings[i]) < int(headings[i+1]) and int(headings[i+1]) - int(headings[i]) > 1:
                        issues.append(f"Invalid heading hierarchy: H{headings[i]} followed by H{headings[i+1]}")
                        score -= 10
        
        # Image optimization
        images = re.findall(r'<img[^>]*>', html_content, re.IGNORECASE)
        for img in images:
            if 'alt=' not in img:
                issues.append("Image missing alt attribute")
                score -= 5
            if 'loading=' not in img and 'lazy' not in img:
                issues.append("Image missing lazy loading")
                score -= 3
        
        return {
            "score": max(0, score),
            "issues": issues,
            "total_issues": len(issues),
            "headings_count": len(headings),
            "images_count": len(images)
        }

    def check_file_structure(self) -> Dict[str, Any]:
        """Check essential SEO files"""
        issues = []
        score = 100
        
        required_files = [
            "robots.txt",
            "sitemap.xml",
            ".htaccess"
        ]
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                issues.append(f"Missing {file_name}")
                score -= 25
        
        # Check sitemap content
        sitemap_path = self.project_root / "sitemap.xml"
        if sitemap_path.exists():
            with open(sitemap_path, 'r', encoding='utf-8') as f:
                sitemap_content = f.read()
                if '<urlset' not in sitemap_content:
                    issues.append("Invalid sitemap.xml structure")
                    score -= 15
        else:
            score -= 25
        
        return {
            "score": max(0, score),
            "issues": issues,
            "total_issues": len(issues)
        }

    def audit_page(self, file_path: Path) -> Dict[str, Any]:
        """Audit a single HTML page"""
        page_name = file_path.stem
        print(f"Auditing {page_name}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Perform all checks
        meta_check = self.check_meta_tags(html_content, page_name)
        structured_data_check = self.check_structured_data(html_content)
        performance_check = self.check_performance_elements(html_content)
        content_check = self.check_content_optimization(html_content)
        
        # Calculate overall page score
        page_score = (
            meta_check["score"] * 0.3 +
            structured_data_check["score"] * 0.25 +
            performance_check["score"] * 0.2 +
            content_check["score"] * 0.25
        )
        
        return {
            "page_name": page_name,
            "overall_score": round(page_score, 1),
            "meta_tags": meta_check,
            "structured_data": structured_data_check,
            "performance": performance_check,
            "content": content_check,
            "total_issues": (
                meta_check["total_issues"] +
                structured_data_check["total_issues"] +
                performance_check["total_issues"] +
                content_check["total_issues"]
            )
        }

    def run_audit(self) -> Dict[str, Any]:
        """Run complete SEO audit"""
        print("🔍 Starting comprehensive SEO audit...")
        print("=" * 50)
        
        # Audit all HTML templates
        html_files = list(self.templates_dir.glob("*.html"))
        page_results = []
        
        for html_file in html_files:
            try:
                result = self.audit_page(html_file)
                page_results.append(result)
                self.results["page_scores"][result["page_name"]] = result["overall_score"]
            except Exception as e:
                print(f"Error auditing {html_file.name}: {e}")
        
        # Check file structure
        file_structure = self.check_file_structure()
        
        # Calculate overall score
        if page_results:
            avg_page_score = sum(r["overall_score"] for r in page_results) / len(page_results)
            file_score = file_structure["score"]
            
            self.results["overall_score"] = round((avg_page_score * 0.8) + (file_score * 0.2), 1)
            
            # Collect all issues
            for result in page_results:
                if result["total_issues"] > 0:
                    self.results["warnings"].append(f"{result['page_name']}: {result['total_issues']} issues found")
                
                if result["overall_score"] < 70:
                    self.results["critical_issues"].append(f"{result['page_name']}: Low score ({result['overall_score']})")
        
        # Add file structure issues
        if file_structure["total_issues"] > 0:
            self.results["critical_issues"].extend(file_structure["issues"])
        
        # Generate recommendations
        self.generate_recommendations()
        
        return self.results

    def generate_recommendations(self):
        """Generate actionable recommendations"""
        if self.results["overall_score"] < 80:
            self.results["recommendations"].append("Overall SEO score is below 80. Focus on critical issues first.")
        
        if self.results["overall_score"] < 60:
            self.results["recommendations"].append("Critical SEO issues detected. Immediate attention required.")
        
        # Page-specific recommendations
        for page_name, score in self.results["page_scores"].items():
            if score < 70:
                self.results["recommendations"].append(f"Prioritize fixing {page_name} (score: {score})")
        
        # General recommendations
        self.results["recommendations"].extend([
            "Ensure all meta tags are properly implemented",
            "Add structured data to all pages",
            "Optimize images with alt tags and lazy loading",
            "Implement proper heading hierarchy",
            "Add preconnect and DNS prefetch links",
            "Create and submit sitemap to Google Search Console",
            "Set up Google Analytics and Search Console",
            "Test page speed with Google PageSpeed Insights"
        ])

    def print_report(self):
        """Print comprehensive audit report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE SEO AUDIT REPORT")
        print("=" * 60)
        
        print(f"\n🏆 OVERALL SEO SCORE: {self.results['overall_score']}/100")
        
        if self.results["overall_score"] >= 90:
            print("🎉 EXCELLENT! Your SEO implementation is outstanding!")
        elif self.results["overall_score"] >= 80:
            print("✅ GOOD! Your SEO implementation is solid with room for improvement.")
        elif self.results["overall_score"] >= 70:
            print("⚠️  FAIR! Your SEO needs attention to reach optimal performance.")
        else:
            print("❌ POOR! Critical SEO issues need immediate attention.")
        
        print(f"\n📄 PAGE-BY-PAGE BREAKDOWN:")
        print("-" * 40)
        for page_name, score in self.results["page_scores"].items():
            status = "✅" if score >= 80 else "⚠️" if score >= 70 else "❌"
            print(f"{status} {page_name}: {score}/100")
        
        if self.results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES ({len(self.results['critical_issues'])}):")
            print("-" * 40)
            for issue in self.results["critical_issues"]:
                print(f"❌ {issue}")
        
        if self.results["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(self.results['warnings'])}):")
            print("-" * 40)
            for warning in self.results["warnings"]:
                print(f"⚠️  {warning}")
        
        if self.results["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS ({len(self.results['recommendations'])}):")
            print("-" * 40)
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"{i}. {rec}")
        
        print(f"\n📁 FILE STRUCTURE CHECK:")
        print("-" * 40)
        required_files = ["robots.txt", "sitemap.xml", ".htaccess"]
        for file_name in required_files:
            file_path = self.project_root / file_name
            status = "✅" if file_path.exists() else "❌"
            print(f"{status} {file_name}")
        
        print(f"\n🎯 NEXT STEPS:")
        print("-" * 40)
        print("1. Fix critical issues identified above")
        print("2. Implement missing meta tags and structured data")
        print("3. Test page speed with Google PageSpeed Insights")
        print("4. Submit sitemap to Google Search Console")
        print("5. Set up Google Analytics tracking")
        print("6. Monitor Core Web Vitals")
        
        print(f"\n📈 EXPECTED IMPROVEMENTS:")
        print("-" * 40)
        if self.results["overall_score"] < 80:
            print("• Fixing identified issues should improve score by 15-25 points")
            print("• Better search engine visibility and rankings")
            print("• Improved page load speed and user experience")
            print("• Higher click-through rates from search results")
        
        print("\n" + "=" * 60)

def main():
    """Main function to run the SEO audit"""
    auditor = SEOAuditor()
    results = auditor.run_audit()
    auditor.print_report()
    
    # Save detailed results to file
    report_file = "seo_audit_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    main()
