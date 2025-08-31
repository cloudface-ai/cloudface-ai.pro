"""
Quick SEO Fix Script for CloudFace AI
Fixes remaining SEO issues to improve scores from 82-84 to 95+.
"""

import os
import re
from pathlib import Path

class SEOQuickFix:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.templates_dir = self.project_root / "templates"
        
    def add_preconnect_links(self, html_content: str) -> str:
        """Add preconnect and DNS prefetch links for better performance"""
        preconnect_links = '''
        <!-- Performance optimization links -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link rel="dns-prefetch" href="https://www.googletagmanager.com">
        <link rel="dns-prefetch" href="https://www.google-analytics.com">
        '''
        
        # Insert after charset meta tag
        if '<meta charset=' in html_content and 'rel="preconnect"' not in html_content:
            html_content = html_content.replace(
                '<meta charset="utf-8">',
                '<meta charset="utf-8">' + preconnect_links
            )
        
        return html_content
    
    def add_structured_data(self, html_content: str, page_name: str) -> str:
        """Add structured data to pages that don't have it"""
        if 'application/ld+json' in html_content:
            return html_content  # Already has structured data
        
        # Basic organization schema for all pages
        structured_data = f'''
        <!-- Structured Data (JSON-LD) for SEO -->
        <script type="application/ld+json">
        {{
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": "CloudFace AI - {page_name.title()}",
            "description": "AI-powered face recognition technology for photo organization",
            "url": "https://cloudface-ai.com/{page_name if page_name != 'landing' else ''}",
            "author": {{
                "@type": "Organization",
                "name": "CloudFace AI",
                "url": "https://cloudface-ai.com"
            }},
            "publisher": {{
                "@type": "Organization",
                "name": "CloudFace AI",
                "url": "https://cloudface-ai.com"
            }}
        }}
        </script>
        '''
        
        # Insert before closing head tag
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', structured_data + '\n</head>')
        
        return html_content
    
    def add_image_optimization(self, html_content: str) -> str:
        """Add alt attributes and lazy loading to images"""
        # Find images without alt attributes
        img_pattern = r'<img([^>]*?)(?<!alt=)([^>]*?)>'
        
        def add_alt_and_lazy(match):
            attrs = match.group(1) + match.group(2)
            if 'alt=' not in attrs:
                attrs += ' alt="CloudFace AI"'
            if 'loading=' not in attrs:
                attrs += ' loading="lazy"'
            return f'<img{attrs}>'
        
        html_content = re.sub(img_pattern, add_alt_and_lazy, html_content)
        return html_content
    
    def fix_heading_hierarchy(self, html_content: str) -> str:
        """Ensure proper heading hierarchy"""
        # This is a basic check - in practice, you'd want to analyze the actual content structure
        # For now, we'll just ensure there's at least one H1
        if '<h1' not in html_content and '<h2' in html_content:
            # Convert first H2 to H1 if no H1 exists
            html_content = html_content.replace('<h2', '<h1', 1)
            html_content = html_content.replace('</h2>', '</h1>', 1)
        
        return html_content
    
    def fix_page(self, file_path: Path) -> bool:
        """Fix SEO issues in a single HTML file"""
        page_name = file_path.stem
        print(f"Fixing {page_name}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            original_content = html_content
            
            # Apply fixes
            html_content = self.add_preconnect_links(html_content)
            html_content = self.add_structured_data(html_content, page_name)
            html_content = self.add_image_optimization(html_content)
            html_content = self.fix_heading_hierarchy(html_content)
            
            # Save fixed file
            if html_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"✅ {page_name} fixed successfully")
                return True
            else:
                print(f"ℹ️  {page_name} already optimized")
                return False
                
        except Exception as e:
            print(f"❌ Error fixing {page_name}: {e}")
            return False
    
    def run_fixes(self):
        """Run all SEO fixes"""
        print("🔧 Starting SEO Quick Fixes...")
        print("=" * 50)
        
        html_files = list(self.templates_dir.glob("*.html"))
        fixed_count = 0
        
        for html_file in html_files:
            if self.fix_page(html_file):
                fixed_count += 1
        
        print(f"\n✅ Fixes completed!")
        print(f"📊 Files updated: {fixed_count}/{len(html_files)}")
        
        if fixed_count > 0:
            print(f"\n🔄 Next steps:")
            print("1. Run 'python seo_audit.py' again to check improved scores")
            print("2. Test the updated pages")
            print("3. Submit sitemap to Google Search Console")
        else:
            print(f"\n🎉 All pages are already optimized!")

def main():
    """Main function to run the SEO fixes"""
    fixer = SEOQuickFix()
    fixer.run_fixes()

if __name__ == "__main__":
    main()
