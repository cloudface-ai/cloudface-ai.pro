"""
Performance Optimization Script for CloudFace AI
This script handles CSS/JS minification, image optimization, and performance improvements.
"""

import os
import re
import json
import gzip
import shutil
from pathlib import Path
from typing import List, Dict, Any

class PerformanceOptimizer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.templates_dir = self.project_root / "templates"
        self.assets_dir = self.project_root / "assets"
        self.build_dir = self.project_root / "build" / "optimized"
        
        # Create build directory if it doesn't exist
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
    def minify_css(self, css_content: str) -> str:
        """Minify CSS content by removing unnecessary whitespace and comments"""
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        css_content = re.sub(r';\s*}', '}', css_content)
        css_content = re.sub(r'{\s*', '{', css_content)
        css_content = re.sub(r'}\s*', '}', css_content)
        css_content = re.sub(r':\s*', ':', css_content)
        css_content = re.sub(r';\s*', ';', css_content)
        css_content = re.sub(r',\s*', ',', css_content)
        
        # Remove leading/trailing whitespace
        css_content = css_content.strip()
        
        return css_content
    
    def minify_js(self, js_content: str) -> str:
        """Minify JavaScript content by removing unnecessary whitespace and comments"""
        # Remove single-line comments
        js_content = re.sub(r'//.*$', '', js_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        js_content = re.sub(r';\s*}', '}', js_content)
        js_content = re.sub(r'{\s*', '{', js_content)
        js_content = re.sub(r'}\s*', '}', js_content)
        js_content = re.sub(r';\s*', ';', js_content)
        js_content = re.sub(r',\s*', ',', js_content)
        
        # Remove leading/trailing whitespace
        js_content = js_content.strip()
        
        return js_content
    
    def extract_css_from_html(self, html_content: str) -> List[str]:
        """Extract CSS from HTML style tags"""
        css_pattern = r'<style[^>]*>(.*?)</style>'
        css_blocks = re.findall(css_pattern, html_content, re.DOTALL)
        return css_blocks
    
    def extract_js_from_html(self, html_content: str) -> List[str]:
        """Extract JavaScript from HTML script tags"""
        js_pattern = r'<script[^>]*>(.*?)</script>'
        js_blocks = re.findall(js_pattern, html_content, re.DOTALL)
        return js_blocks
    
    def optimize_html_file(self, file_path: Path) -> Dict[str, Any]:
        """Optimize a single HTML file"""
        print(f"Optimizing {file_path.name}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract CSS and JS
        css_blocks = self.extract_css_from_html(html_content)
        js_blocks = self.extract_js_from_html(html_content)
        
        # Minify CSS
        minified_css = []
        for css in css_blocks:
            minified_css.append(self.minify_css(css))
        
        # Minify JS
        minified_js = []
        for js in js_blocks:
            minified_js.append(self.minify_js(js))
        
        # Create optimized HTML
        optimized_html = html_content
        
        # Replace CSS blocks
        for i, (original, minified) in enumerate(zip(css_blocks, minified_css)):
            optimized_html = optimized_html.replace(original, minified)
        
        # Replace JS blocks
        for i, (original, minified) in enumerate(zip(js_blocks, minified_js)):
            optimized_html = optimized_html.replace(original, minified)
        
        # Save optimized file
        output_path = self.build_dir / file_path.name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized_html)
        
        # Calculate size reduction
        original_size = len(html_content)
        optimized_size = len(optimized_html)
        reduction = ((original_size - optimized_size) / original_size) * 100
        
        return {
            "file": file_path.name,
            "original_size": original_size,
            "optimized_size": optimized_size,
            "reduction_percent": reduction,
            "css_blocks": len(css_blocks),
            "js_blocks": len(js_blocks)
        }
    
    def create_gzip_versions(self):
        """Create gzipped versions of optimized files for better compression"""
        print("Creating gzipped versions...")
        
        for file_path in self.build_dir.glob("*.html"):
            with open(file_path, 'rb') as f:
                content = f.read()
            
            gzip_path = file_path.with_suffix('.html.gz')
            with gzip.open(gzip_path, 'wb') as f:
                f.write(content)
            
            print(f"Created {gzip_path.name}")
    
    def generate_performance_report(self, optimization_results: List[Dict[str, Any]]) -> str:
        """Generate a performance optimization report"""
        total_original = sum(r['original_size'] for r in optimization_results)
        total_optimized = sum(r['optimized_size'] for r in optimization_results)
        total_reduction = ((total_original - total_optimized) / total_original) * 100
        
        report = f"""
# Performance Optimization Report

## Summary
- Total files optimized: {len(optimization_results)}
- Total original size: {total_original:,} bytes
- Total optimized size: {total_optimized:,} bytes
- Overall size reduction: {total_reduction:.1f}%

## File Details
"""
        
        for result in optimization_results:
            report += f"""
### {result['file']}
- Original size: {result['original_size']:,} bytes
- Optimized size: {result['optimized_size']:,} bytes
- Reduction: {result['reduction_percent']:.1f}%
- CSS blocks: {result['css_blocks']}
- JS blocks: {result['js_blocks']}
"""
        
        return report
    
    def optimize_all_templates(self) -> List[Dict[str, Any]]:
        """Optimize all HTML template files"""
        print("Starting performance optimization...")
        
        html_files = list(self.templates_dir.glob("*.html"))
        if not html_files:
            print("No HTML files found in templates directory")
            return []
        
        results = []
        for html_file in html_files:
            try:
                result = self.optimize_html_file(html_file)
                results.append(result)
            except Exception as e:
                print(f"Error optimizing {html_file.name}: {e}")
        
        return results
    
    def run_optimization(self):
        """Run the complete optimization process"""
        print("🚀 CloudFace AI Performance Optimizer")
        print("=" * 50)
        
        # Optimize templates
        results = self.optimize_all_templates()
        
        if results:
            # Create gzipped versions
            self.create_gzip_versions()
            
            # Generate report
            report = self.generate_performance_report(results)
            
            # Save report
            report_path = self.build_dir / "optimization_report.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print("\n✅ Optimization complete!")
            print(f"📊 Report saved to: {report_path}")
            print(f"📁 Optimized files in: {self.build_dir}")
            
            # Print summary
            total_original = sum(r['original_size'] for r in results)
            total_optimized = sum(r['optimized_size'] for r in results)
            total_reduction = ((total_original - total_optimized) / total_original) * 100
            
            print(f"\n📈 Overall Results:")
            print(f"   Size reduction: {total_reduction:.1f}%")
            print(f"   Space saved: {(total_original - total_optimized) / 1024:.1f} KB")
        else:
            print("❌ No files were optimized")

def main():
    """Main function to run the optimizer"""
    optimizer = PerformanceOptimizer()
    optimizer.run_optimization()

if __name__ == "__main__":
    main()
