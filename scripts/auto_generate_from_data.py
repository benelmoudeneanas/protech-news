#!/usr/bin/env python3
"""
Auto Generate Articles from data.js (UPDATED)
يقرأ data.js ويولد ملفات HTML مع دعم الصور المحلية
"""

import os
import re
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
    match = re.search(r'const\s+articles\s*=\s*\[(.*?)\];', content, re.DOTALL)
    
    if not match:
        print("❌ لم يتم العثور على articles array في data.js")
        return []
    
    array_content = match.group(1)
    articles = []
    
    # تقسيم المقالات (كل object بين {})
    pattern = r'\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    objects = re.findall(pattern, array_content)
    
    for obj in objects:
        article = {}
        
        # استخراج الحقول العادية
        fields = ['slug', 'title', 'date', 'cat', 'desc', 'img', 'url']
        
        for field in fields:
            # البحث عن: field: "value" أو field: 'value'
            field_pattern = rf'{field}\s*:\s*["\']([^"\']*)["\']'
            field_match = re.search(field_pattern, obj)
            if field_match:
                article[field] = field_match.group(1).replace('\\', '')
        
        # استخراج content (بين ` `)
        content_match = re.search(r'content\s*:\s*`([^`]+)`', obj, re.DOTALL)
        if content_match:
            article['content'] = content_match.group(1).strip()
        
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
        'tech': 'cat-tech',
        'news': 'cat-tech',
        'reviews': 'cat-tech',
        'comparison': 'cat-tech',
        'tech-tips': 'cat-tech',
        'entertainment': 'cat-entertainment'
    }
    return category_map.get(category.lower(), 'cat-tech')

def convert_image_path(img_url):
    """تحويل مسار الصورة من مطلق إلى نسبي"""
    
    # إذا كانت الصورة محلية بالفعل
    if img_url.startswith('assets/'):
        # من articles/ نرجع لـ root ونروح لـ assets
        return f"../{img_url}"
    
    # إذا كانت رابط خارجي، نخليها كما هي
    # (السكريبت الآخر download_images.py يحولها لمحلية)
    return img_url

def get_article_content(article_data):
    """الحصول على المحتوى - من data.js أو توليد بسيط"""
    
    # إذا كان المحتوى موجود في data.js، استعمله
    if article_data.get('content'):
        content = article_data['content']
        
        # تحويل مسارات الصور في المحتوى
        # البحث عن src="assets/images/..." وتحويلها لـ src="../assets/images/..."
        content = re.sub(
            r'src="(assets/images/[^"]+)"',
            r'src="../\1"',
            content
        )
        
        return content
    
    # إذا مافيهش، ولد محتوى بسيط
    desc = article_data.get('desc', '')
    
    return f'''
        <h2>Overview</h2>
        <p>{desc}</p>
        
        <p>This article will be updated with full content soon. Stay tuned for more details!</p>
    '''

def generate_article_html(article_data):
    """توليد HTML من القالب"""
    
    # قراءة القالب
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # الحصول على المحتوى
    article_content = get_article_content(article_data)
    
    # تحويل مسار الصورة
    article_image = convert_image_path(article_data.get('img', ''))
    
    # تحضير البيانات
    replacements = {
        '{{TITLE}}': article_data.get('title', 'Untitled'),
        '{{DESCRIPTION}}': article_data.get('desc', ''),
        '{{KEYWORDS}}': article_data.get('title', ''),
        '{{CANONICAL_URL}}': f"{BASE_URL}/articles/{article_data.get('slug', '')}.html",
        '{{IMAGE}}': article_image,  # استخدام المسار المحول
        '{{DATE}}': article_data.get('date', datetime.now().strftime('%Y-%m-%d')),
        '{{DATE_FORMATTED}}': format_date(article_data.get('date', '')),
        '{{CATEGORY}}': article_data.get('cat', 'tech').upper(),
        '{{CATEGORY_CLASS}}': get_category_class(article_data.get('cat', 'tech')),
        '{{TITLE_SHORT}}': article_data.get('title', '')[:50] + '...' if len(article_data.get('title', '')) > 50 else article_data.get('title', ''),
        '{{CONTENT}}': article_content
    }
    
    # تطبيق الاستبدالات
    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, str(value))
    
    return html

def main():
    """البرنامج الرئيسي"""
    
    print("🤖 Auto Generate Articles from data.js (UPDATED)")
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
    skipped_count = 0
    
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
            
            # التحقق إذا كان المحتوى قديم أو placeholder
            if 'Content coming soon' in existing or 'will be updated with full content soon' in existing or len(existing) < 3000:
                # تحديث الملف
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"   🔄 محدث: {slug}.html")
                new_count += 1
            else:
                # تخطي الملفات التي تحتوي على محتوى كامل
                print(f"   ⏭️  تخطي: {slug}.html (يحتوي على محتوى)")
                skipped_count += 1
        else:
            # إنشاء ملف جديد
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"   ✅ جديد: {slug}.html")
            new_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ تم التوليد بنجاح!")
    print(f"   - مقالات جديدة/محدثة: {new_count}")
    print(f"   - مقالات متخطاة: {skipped_count}")
    print(f"   - إجمالي: {len(articles)}")
    print("\n💡 ملاحظة: الصور المحلية في assets/images/articles/")

if __name__ == "__main__":
    main()
