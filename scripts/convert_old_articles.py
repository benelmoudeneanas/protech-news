#!/usr/bin/env python3
"""
ProTech Article Converter
تحويل جميع المقالات القديمة إلى النظام الجديد تلقائياً
"""

import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

# المسارات
OLD_ARTICLES_DIR = "old_articles"  # ضع المقالات القديمة هنا
NEW_ARTICLES_DIR = "articles"       # المقالات الجديدة ستظهر هنا
TEMPLATE_PATH = "templates/article-template.html"
DATA_JS_PATH = "assets/js/data.js"

def extract_article_data(html_content, filename):
    """استخراج البيانات من المقال القديم"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    data = {
        'slug': filename.replace('.html', ''),
        'title': '',
        'description': '',
        'keywords': '',
        'category': 'tech',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'image': '',
        'content': ''
    }
    
    # استخراج العنوان
    title_tag = soup.find('title')
    if title_tag:
        data['title'] = title_tag.text.replace(' | ProTech', '').strip()
    else:
        h1_tag = soup.find('h1')
        if h1_tag:
            data['title'] = h1_tag.text.strip()
    
    # استخراج الوصف
    desc_tag = soup.find('meta', {'name': 'description'})
    if desc_tag:
        data['description'] = desc_tag.get('content', '')
    
    # استخراج الكلمات المفتاحية
    keywords_tag = soup.find('meta', {'name': 'keywords'})
    if keywords_tag:
        data['keywords'] = keywords_tag.get('content', '')
    
    # استخراج الصورة الرئيسية
    og_image = soup.find('meta', {'property': 'og:image'})
    if og_image:
        data['image'] = og_image.get('content', '')
    else:
        # البحث عن أول صورة في المحتوى
        first_img = soup.find('img')
        if first_img:
            data['image'] = first_img.get('src', '')
    
    # استخراج التاريخ
    time_tag = soup.find('time')
    if time_tag:
        datetime_attr = time_tag.get('datetime')
        if datetime_attr:
            data['date'] = datetime_attr.split('T')[0]
    
    # محاولة استخراج الفئة من الكلمات المفتاحية أو المحتوى
    content_lower = html_content.lower()
    if 'iphone' in content_lower or 'ios' in content_lower or 'ipad' in content_lower:
        data['category'] = 'ios'
    elif 'ai' in content_lower or 'artificial intelligence' in content_lower or 'gemini' in content_lower:
        data['category'] = 'ai'
    elif 'ps5' in content_lower or 'ps6' in content_lower or 'xbox' in content_lower or 'gaming' in content_lower or 'nintendo' in content_lower:
        data['category'] = 'gaming'
    elif 'leak' in content_lower or 'rumor' in content_lower or 'تسريب' in content_lower:
        data['category'] = 'leaks'
    elif 'samsung' in content_lower or 'galaxy' in content_lower or 'pixel' in content_lower:
        data['category'] = 'hardware'
    
    # استخراج المحتوى الرئيسي
    # البحث عن div أو section التي تحتوي على المحتوى
    article_content = None
    
    # محاولات متعددة لإيجاد المحتوى
    possible_containers = [
        soup.find('article'),
        soup.find('div', class_=re.compile('article|content|post|entry', re.I)),
        soup.find('section', class_=re.compile('article|content|post', re.I)),
        soup.find('main'),
    ]
    
    for container in possible_containers:
        if container:
            article_content = container
            break
    
    # إذا لم نجد container محدد، نبحث عن المحتوى بين header و footer
    if not article_content:
        # إزالة nav, header, footer
        for tag in soup.find_all(['nav', 'header', 'footer', 'script', 'style']):
            tag.decompose()
        
        # أخذ body كمحتوى
        body = soup.find('body')
        if body:
            article_content = body
    
    if article_content:
        # تنظيف المحتوى
        # إزالة العناصر غير المرغوبة
        for tag in article_content.find_all(['nav', 'header', 'footer', 'script', 'style', 'iframe']):
            tag.decompose()
        
        # إزالة الأزرار والروابط الجانبية
        for tag in article_content.find_all(class_=re.compile('share|social|sidebar|widget|ad|advertisement', re.I)):
            tag.decompose()
        
        # الحصول على المحتوى النظيف
        content_html = str(article_content)
        
        # تنظيف إضافي
        content_html = re.sub(r'<div[^>]*class="[^"]*(?:share|social|sidebar)[^"]*"[^>]*>.*?</div>', '', content_html, flags=re.DOTALL)
        
        # إزالة الأنماط المضمنة
        content_html = re.sub(r' style="[^"]*"', '', content_html)
        
        # إزالة classes غير ضرورية
        content_html = re.sub(r' class="[^"]*"', '', content_html)
        
        data['content'] = content_html
    
    return data

def format_date(date_str):
    """تنسيق التاريخ"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str

def get_category_class(category):
    """الحصول على class الفئة"""
    category_map = {
        'ios': 'cat-ios',
        'ai': 'cat-ai',
        'leaks': 'cat-leaks',
        'hardware': 'cat-hardware',
        'gaming': 'cat-gaming',
        'tech': 'cat-tech'
    }
    return category_map.get(category.lower(), 'cat-tech')

def convert_article(old_html_path, template_path):
    """تحويل مقال واحد"""
    
    # قراءة المقال القديم
    with open(old_html_path, 'r', encoding='utf-8') as f:
        old_html = f.read()
    
    # قراءة القالب
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # استخراج البيانات
    filename = os.path.basename(old_html_path)
    data = extract_article_data(old_html, filename)
    
    # استبدال العلامات في القالب
    replacements = {
        '{{TITLE}}': data['title'],
        '{{DESCRIPTION}}': data['description'],
        '{{KEYWORDS}}': data['keywords'],
        '{{CANONICAL_URL}}': f"https://protech-news.vercel.app/articles/{data['slug']}.html",
        '{{IMAGE}}': data['image'],
        '{{DATE}}': data['date'],
        '{{DATE_FORMATTED}}': format_date(data['date']),
        '{{CATEGORY}}': data['category'].upper(),
        '{{CATEGORY_CLASS}}': get_category_class(data['category']),
        '{{TITLE_SHORT}}': data['title'][:50] + '...' if len(data['title']) > 50 else data['title'],
        '{{CONTENT}}': data['content']
    }
    
    new_html = template
    for placeholder, value in replacements.items():
        new_html = new_html.replace(placeholder, value)
    
    # حفظ المقال الجديد
    new_path = os.path.join(NEW_ARTICLES_DIR, filename)
    with open(new_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    return data

def convert_all_articles():
    """تحويل جميع المقالات"""
    
    print("🚀 ProTech Article Converter")
    print("=" * 60)
    
    # التأكد من وجود المجلدات
    if not os.path.exists(OLD_ARTICLES_DIR):
        print(f"\n❌ خطأ: المجلد {OLD_ARTICLES_DIR} غير موجود!")
        print(f"   قم بإنشاء المجلد ووضع المقالات القديمة فيه")
        return
    
    if not os.path.exists(TEMPLATE_PATH):
        print(f"\n❌ خطأ: القالب {TEMPLATE_PATH} غير موجود!")
        return
    
    if not os.path.exists(NEW_ARTICLES_DIR):
        os.makedirs(NEW_ARTICLES_DIR)
    
    # الحصول على جميع ملفات HTML
    html_files = [f for f in os.listdir(OLD_ARTICLES_DIR) if f.endswith('.html')]
    
    if not html_files:
        print(f"\n❌ لم يتم العثور على ملفات HTML في {OLD_ARTICLES_DIR}")
        return
    
    print(f"\n📄 تم العثور على {len(html_files)} مقال")
    print("\n🔄 جاري التحويل...\n")
    
    converted_articles = []
    failed_articles = []
    
    for i, filename in enumerate(html_files, 1):
        try:
            old_path = os.path.join(OLD_ARTICLES_DIR, filename)
            article_data = convert_article(old_path, TEMPLATE_PATH)
            converted_articles.append(article_data)
            
            print(f"   ✅ [{i}/{len(html_files)}] {filename}")
            
        except Exception as e:
            failed_articles.append((filename, str(e)))
            print(f"   ❌ [{i}/{len(html_files)}] {filename} - خطأ: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"✅ تم تحويل {len(converted_articles)} مقال بنجاح")
    
    if failed_articles:
        print(f"❌ فشل تحويل {len(failed_articles)} مقال:")
        for filename, error in failed_articles:
            print(f"   - {filename}: {error}")
    
    # إنشاء ملف data.js جديد
    if converted_articles:
        print("\n📝 جاري تحديث data.js...")
        update_data_js(converted_articles)
        print("✅ تم تحديث data.js")
    
    print("\n" + "=" * 60)
    print("🎉 انتهى التحويل!")
    print(f"\n📂 المقالات الجديدة في: {NEW_ARTICLES_DIR}/")
    print("📝 البيانات محدثة في: assets/js/data.js")
    print("\n💡 الخطوة التالية: شغّل generate_sitemap.py لتحديث خريطة الموقع")

def update_data_js(articles_data):
    """تحديث ملف data.js"""
    
    # بناء محتوى المقالات
    articles_js = "const articles = [\n"
    
    for article in sorted(articles_data, key=lambda x: x['date'], reverse=True):
        articles_js += f'''
  {{
    slug: "{article['slug']}",
    title: "{article['title'].replace('"', '\\"')}",
    date: "{article['date']}",
    cat: "{article['category']}",
    desc: "{article['description'].replace('"', '\\"')[:200]}",
    img: "{article['image']}",
    url: "articles/{article['slug']}.html"
  }},'''
    
    articles_js += "\n];"
    
    # حفظ الملف
    os.makedirs(os.path.dirname(DATA_JS_PATH), exist_ok=True)
    with open(DATA_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(articles_js)

if __name__ == "__main__":
    # تثبيت BeautifulSoup إذا لم يكن موجوداً
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("📦 جاري تثبيت BeautifulSoup...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'beautifulsoup4', '--break-system-packages'])
        from bs4 import BeautifulSoup
        print("✅ تم التثبيت بنجاح\n")
    
    convert_all_articles()
