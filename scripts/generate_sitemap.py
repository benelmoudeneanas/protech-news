#!/usr/bin/env python3
"""
Generate sitemap.xml automatically
يولد sitemap من المقالات الموجودة
"""

import os
import re
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Configuration
BASE_URL = "https://protechdaily.online"
ARTICLES_DIR = "articles"
PAGES_DIR = "pages"
OUTPUT_FILE = "sitemap.xml"

def get_article_files():
    """الحصول على جميع ملفات المقالات"""
    if not os.path.exists(ARTICLES_DIR):
        return []
    return [f for f in os.listdir(ARTICLES_DIR) if f.endswith('.html')]

def get_page_files():
    """الحصول على ملفات الصفحات"""
    files = []
    if os.path.exists(PAGES_DIR):
        files = [f for f in os.listdir(PAGES_DIR) if f.endswith('.html')]
    return files

def extract_date_from_file(filepath):
    """استخراج التاريخ من الملف"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # البحث عن التاريخ في meta tags
            date_match = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', content)
            if date_match:
                return date_match.group(1)
            
            # البحث في datePublished
            date_match = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})"', content)
            if date_match:
                return date_match.group(1)
    except:
        pass
    
    # استخدام تاريخ التعديل
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')

def generate_sitemap():
    """توليد sitemap.xml"""
    
    # إنشاء العنصر الرئيسي
    urlset = Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
    urlset.set('xmlns:xhtml', 'http://www.w3.org/1999/xhtml')
    urlset.set('xmlns:mobile', 'http://www.google.com/schemas/sitemap-mobile/1.0')
    urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
    
    # الصفحة الرئيسية
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = f"{BASE_URL}/"
    SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    SubElement(url, 'changefreq').text = 'daily'
    SubElement(url, 'priority').text = '1.0'
    
    # الصفحات الرئيسية
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
    
    # صفحات الأقسام
    page_files = get_page_files()
    for page_file in page_files:
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = f"{BASE_URL}/pages/{page_file}"
        SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
        SubElement(url, 'changefreq').text = 'weekly'
        SubElement(url, 'priority').text = '0.8'
    
    # المقالات (مرتبة من الأحدث للأقدم)
    article_files = get_article_files()
    
    # ترتيب المقالات حسب التاريخ
    articles_with_dates = []
    for article_file in article_files:
        filepath = os.path.join(ARTICLES_DIR, article_file)
        article_date = extract_date_from_file(filepath)
        articles_with_dates.append((article_file, article_date))
    
    # ترتيب عكسي (الأحدث أولاً)
    articles_with_dates.sort(key=lambda x: x[1], reverse=True)
    
    # إضافة المقالات
    for article_file, article_date in articles_with_dates:
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = f"{BASE_URL}/articles/{article_file}"
        SubElement(url, 'lastmod').text = article_date
        SubElement(url, 'changefreq').text = 'weekly'
        SubElement(url, 'priority').text = '0.9'
    
    # تحويل إلى XML منسق
    xml_str = minidom.parseString(tostring(urlset)).toprettyxml(indent='    ')
    
    # إزالة الأسطر الفارغة
    xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])
    
    # الكتابة في الملف
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"✅ تم توليد Sitemap: {OUTPUT_FILE}")
    print(f"   - 1 صفحة رئيسية")
    print(f"   - {len(main_pages)} صفحات أساسية")
    print(f"   - {len(page_files)} صفحات أقسام")
    print(f"   - {len(article_files)} مقال")
    print(f"   - المجموع: {1 + len(main_pages) + len(page_files) + len(article_files)} URL")
    
    return OUTPUT_FILE

if __name__ == "__main__":
    print("🗺️  ProTech Sitemap Generator")
    print("=" * 60)
    generate_sitemap()
    print("\n✨ تم! جاهز للإرسال إلى Google Search Console")
