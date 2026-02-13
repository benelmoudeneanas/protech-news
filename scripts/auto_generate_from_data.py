#!/usr/bin/env python3
"""
Auto Generate Articles from data.js
يقرأ data.js ويولد ملفات HTML للمقالات الجديدة فقط
"""

import os
import re
import json
from datetime import datetime

# المسارات
DATA_JS_PATH = "assets/js/data.js"
TEMPLATE_PATH = "templates/article-template.html"
ARTICLES_DIR = "articles"
BASE_URL = "https://protechdaily.online"

def parse_data_js():
    """قراءة وتحليل data.js"""
    
    with open(DATA_JS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # استخراج الـ array من JavaScript
    # نبحث عن const articles = [ ... ];
    match = re.search(r'const\s+articles\s*=\s*\[(.*?)\];', content, re.DOTALL)
    
    if not match:
        print("❌ لم يتم العثور على articles array في data.js")
        return []
    
    array_content = match.group(1)
    
    # تحويل JavaScript objects إلى Python
    # نستبدل ' بـ " ونصلح الـ format
    array_content = array_content.strip()
    
    # تقسيم الـ objects
    articles = []
    
    # نبحث عن كل object بين { }
    objects = re.findall(r'\{([^}]+)\}', array_content)
    
    for obj in objects:
        article = {}
        
        # استخراج كل field
        fields = ['slug', 'title', 'date', 'cat', 'desc', 'img', 'url']
        
        for field in fields:
            # البحث عن: field: "value" أو field: 'value'
            pattern = rf'{field}\s*:\s*["\']([^"\']*)["\']'
            match = re.search(pattern, obj)
            if match:
                article[field] = match.group(1)
        
        if article.get('slug'):
            articles.append(article)
    
    return articles

def format_date(date_str):
    """تنسيق التاريخ"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str

def get_category_class(category):
    """CSS class للفئة"""
    category_map = {
        'ios': 'cat-ios',
        'ai': 'cat-ai',
        'leaks': 'cat-leaks',
        'hardware': 'cat-hardware',
        'gaming': 'cat-gaming',
        'tech': 'cat-tech'
    }
    return category_map.get(category.lower(), 'cat-tech')

def generate_article_html(article_data):
    """توليد HTML من القالب"""
    
    # قراءة القالب
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # تحضير البيانات
    replacements = {
        '{{TITLE}}': article_data.get('title', 'Untitled'),
        '{{DESCRIPTION}}': article_data.get('desc', ''),
        '{{KEYWORDS}}': article_data.get('title', ''),
        '{{CANONICAL_URL}}': f"{BASE_URL}/articles/{article_data.get('slug', '')}.html",
        '{{IMAGE}}': article_data.get('img', ''),
        '{{DATE}}': article_data.get('date', datetime.now().strftime('%Y-%m-%d')),
        '{{DATE_FORMATTED}}': format_date(article_data.get('date', '')),
        '{{CATEGORY}}': article_data.get('cat', 'tech').upper(),
        '{{CATEGORY_CLASS}}': get_category_class(article_data.get('cat', 'tech')),
        '{{TITLE_SHORT}}': article_data.get('title', '')[:50] + '...' if len(article_data.get('title', '')) > 50 else article_data.get('title', ''),
        '{{CONTENT}}': f'''
            <h2>Introduction</h2>
            <p>{article_data.get('desc', 'Content coming soon...')}</p>
            
            <p>This article will be updated with full content soon. Stay tuned for more details!</p>
        '''
    }
    
    # تطبيق الاستبدالات
    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, str(value))
    
    return html

def main():
    """البرنامج الرئيسي"""
    
    print("🤖 Auto Generate Articles from data.js")
    print("=" * 60)
    
    # التأكد من وجود الملفات
    if not os.path.exists(DATA_JS_PATH):
        print(f"❌ {DATA_JS_PATH} غير موجود!")
        return
    
    if not os.path.exists(TEMPLATE_PATH):
        print(f"❌ {TEMPLATE_PATH} غير موجود!")
        return
    
    if not os.path.exists(ARTICLES_DIR):
        os.makedirs(ARTICLES_DIR)
    
    # قراءة المقالات من data.js
    articles = parse_data_js()
    
    if not articles:
        print("⚠️  لم يتم العثور على مقالات في data.js")
        return
    
    print(f"\n📊 تم العثور على {len(articles)} مقال في data.js")
    
    # توليد المقالات
    new_count = 0
    updated_count = 0
    
    for article in articles:
        slug = article.get('slug', '')
        if not slug:
            continue
        
        article_path = os.path.join(ARTICLES_DIR, f"{slug}.html")
        
        # توليد HTML
        html = generate_article_html(article)
        
        # التحقق من وجود الملف
        if os.path.exists(article_path):
            # قراءة الملف الموجود
            with open(article_path, 'r', encoding='utf-8') as f:
                existing = f.read()
            
            # التحقق إذا كان المحتوى placeholder فقط
            if 'Content coming soon' in existing or len(existing) < 5000:
                # تحديث الملف
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"   🔄 محدث: {slug}.html")
                updated_count += 1
        else:
            # إنشاء ملف جديد
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"   ✅ جديد: {slug}.html")
            new_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ تم التوليد بنجاح!")
    print(f"   - مقالات جديدة: {new_count}")
    print(f"   - مقالات محدثة: {updated_count}")
    print(f"   - إجمالي: {len(articles)}")

if __name__ == "__main__":
    main()
