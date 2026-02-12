#!/usr/bin/env python3
"""
ProTech Sitemap Generator
Automatically generates sitemap.xml from articles
"""

import os
import re
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Configuration
BASE_URL = "https://protech-news.vercel.app"
ARTICLES_DIR = "articles"
PAGES_DIR = "pages"
OUTPUT_FILE = "sitemap.xml"

def get_article_files():
    """Get all article HTML files"""
    if not os.path.exists(ARTICLES_DIR):
        return []
    return [f for f in os.listdir(ARTICLES_DIR) if f.endswith('.html')]

def get_page_files():
    """Get all page HTML files"""
    files = []
    if os.path.exists(PAGES_DIR):
        files = [f for f in os.listdir(PAGES_DIR) if f.endswith('.html')]
    return files

def extract_date_from_file(filepath):
    """Try to extract date from file content or use modification time"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Try to find date in meta tags
            date_match = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', content)
            if date_match:
                return date_match.group(1)
    except:
        pass
    
    # Fallback to file modification time
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')

def generate_sitemap():
    """Generate sitemap.xml"""
    
    # Create root element
    urlset = Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
    urlset.set('xmlns:xhtml', 'http://www.w3.org/1999/xhtml')
    urlset.set('xmlns:mobile', 'http://www.google.com/schemas/sitemap-mobile/1.0')
    urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
    
    # Add homepage
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = f"{BASE_URL}/"
    SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    SubElement(url, 'changefreq').text = 'daily'
    SubElement(url, 'priority').text = '1.0'
    
    # Add main pages
    main_pages = [
        ('about.html', 'monthly', '0.5'),
        ('contact.html', 'monthly', '0.5')
    ]
    
    for page, changefreq, priority in main_pages:
        if os.path.exists(page):
            url = SubElement(urlset, 'url')
            SubElement(url, 'loc').text = f"{BASE_URL}/{page}"
            SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
            SubElement(url, 'changefreq').text = changefreq
            SubElement(url, 'priority').text = priority
    
    # Add pages from pages directory
    page_files = get_page_files()
    for page_file in page_files:
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = f"{BASE_URL}/pages/{page_file}"
        SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
        SubElement(url, 'changefreq').text = 'weekly'
        SubElement(url, 'priority').text = '0.8'
    
    # Add articles
    article_files = get_article_files()
    for article_file in sorted(article_files, reverse=True):  # Most recent first
        filepath = os.path.join(ARTICLES_DIR, article_file)
        article_date = extract_date_from_file(filepath)
        
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = f"{BASE_URL}/articles/{article_file}"
        SubElement(url, 'lastmod').text = article_date
        SubElement(url, 'changefreq').text = 'weekly'
        SubElement(url, 'priority').text = '0.9'
    
    # Convert to pretty XML
    xml_str = minidom.parseString(tostring(urlset)).toprettyxml(indent='    ')
    
    # Remove extra blank lines
    xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])
    
    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"✅ Sitemap generated: {OUTPUT_FILE}")
    print(f"   - 1 homepage")
    print(f"   - {len(main_pages)} main pages")
    print(f"   - {len(page_files)} category pages")
    print(f"   - {len(article_files)} articles")
    print(f"   - Total: {1 + len(main_pages) + len(page_files) + len(article_files)} URLs")
    
    return OUTPUT_FILE

if __name__ == "__main__":
    print("🗺️  ProTech Sitemap Generator")
    print("=" * 50)
    generate_sitemap()
    print("\n✨ Done! Submit sitemap.xml to Google Search Console.")
