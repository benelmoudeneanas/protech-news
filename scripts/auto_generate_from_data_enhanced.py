#!/usr/bin/env python3
"""
Auto Generate Articles from data.js - Enhanced Version
يقرأ data.js ويولد ملفات HTML بمحتوى جيد
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
    match = re.search(r'const\s+articles\s*=\s*\[(.*?)\];', content, re.DOTALL)
    
    if not match:
        print("❌ لم يتم العثور على articles array في data.js")
        return []
    
    array_content = match.group(1)
    
    # تحويل JavaScript objects إلى Python
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
                article[field] = match.group(1).replace('\\', '')
        
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

def generate_smart_content(article_data):
    """توليد محتوى ذكي بناءً على البيانات"""
    
    title = article_data.get('title', '')
    desc = article_data.get('desc', '')
    category = article_data.get('cat', 'tech')
    
    # توليد محتوى بناءً على الفئة
    content = f'''
        <h2>Overview</h2>
        <p>{desc}</p>
        
        <p>In this comprehensive article, we dive deep into all the details surrounding {title}. Stay with us as we explore the key highlights, implications, and what this means for the tech industry.</p>
    '''
    
    # محتوى مخصص حسب الفئة
    if category == 'ios':
        content += '''
        <h2>Key Features</h2>
        <p>Apple continues to push the boundaries with innovative features that set new standards in the industry. Here's what stands out:</p>
        
        <ul>
            <li><strong>Performance:</strong> Latest chipset delivering unprecedented speed and efficiency</li>
            <li><strong>Camera:</strong> Advanced imaging capabilities for professional-quality photos and videos</li>
            <li><strong>Battery:</strong> All-day battery life with fast charging support</li>
            <li><strong>Design:</strong> Premium materials with attention to every detail</li>
        </ul>
        
        <h2>Pricing and Availability</h2>
        <p>Details about pricing and release dates will be updated as official information becomes available. Stay tuned for the latest updates.</p>
        '''
    
    elif category == 'ai':
        content += '''
        <h2>The Impact of AI</h2>
        <p>Artificial Intelligence continues to revolutionize how we interact with technology. This development represents a significant step forward in the field.</p>
        
        <h3>Key Capabilities</h3>
        <ul>
            <li>Advanced natural language processing</li>
            <li>Improved accuracy and reliability</li>
            <li>Enhanced user experience</li>
            <li>Broader application possibilities</li>
        </ul>
        
        <h2>What This Means for Users</h2>
        <p>These advancements will bring tangible benefits to everyday users, from improved productivity to more intuitive interactions with technology.</p>
        '''
    
    elif category == 'gaming':
        content += '''
        <h2>Gaming Experience</h2>
        <p>The gaming industry continues to evolve with cutting-edge hardware and innovative features that deliver immersive experiences.</p>
        
        <h3>Performance Highlights</h3>
        <ul>
            <li><strong>Graphics:</strong> Stunning visuals with ray tracing and high frame rates</li>
            <li><strong>Loading Times:</strong> Near-instant loading with advanced SSD technology</li>
            <li><strong>Controller:</strong> Responsive controls with haptic feedback</li>
            <li><strong>Game Library:</strong> Extensive collection of exclusive titles</li>
        </ul>
        
        <h2>Release Information</h2>
        <p>We'll update this article with official release dates and pricing as soon as they're announced.</p>
        '''
    
    elif category == 'leaks':
        content += '''
        <h2>Exclusive Information</h2>
        <p>Based on reliable sources and insider information, we've gathered the most credible leaks and rumors surrounding this topic.</p>
        
        <h3>What We Know So Far</h3>
        <p>Our sources indicate several exciting developments that could reshape expectations. While we cannot confirm all details until official announcements, the information gathered points to significant improvements.</p>
        
        <blockquote>
            "These leaks, if accurate, suggest a major leap forward in technology and user experience."
        </blockquote>
        
        <h2>Reliability Check</h2>
        <p>We've cross-referenced multiple sources to verify the accuracy of this information. However, as with all leaks, official confirmation is pending.</p>
        '''
    
    elif category == 'hardware':
        content += '''
        <h2>Technical Specifications</h2>
        <p>This device brings impressive hardware specifications designed to deliver exceptional performance.</p>
        
        <h3>Key Specs</h3>
        <ul>
            <li><strong>Processor:</strong> Latest generation chipset for smooth performance</li>
            <li><strong>Display:</strong> High-quality screen with vibrant colors</li>
            <li><strong>Storage:</strong> Ample space for all your content</li>
            <li><strong>Connectivity:</strong> 5G support and latest wireless standards</li>
        </ul>
        
        <h2>Design and Build</h2>
        <p>Premium materials and thoughtful design choices make this device stand out from the competition.</p>
        '''
    
    else:  # tech
        content += '''
        <h2>Technical Details</h2>
        <p>This development represents an important advancement in the technology sector, with implications that reach across multiple industries.</p>
        
        <h3>Key Takeaways</h3>
        <ul>
            <li>Innovative approach to solving real-world problems</li>
            <li>Integration with existing technologies</li>
            <li>Potential for widespread adoption</li>
            <li>Future-ready design and capabilities</li>
        </ul>
        
        <h2>Industry Impact</h2>
        <p>The ripple effects of this technology will be felt across the industry, potentially changing how we approach similar challenges in the future.</p>
        '''
    
    content += '''
        <h2>Final Thoughts</h2>
        <p>This is an exciting development that we'll continue to monitor closely. Check back for updates as more information becomes available.</p>
        
        <p>What are your thoughts on this news? We'd love to hear your perspective in the comments below.</p>
    '''
    
    return content

def generate_article_html(article_data):
    """توليد HTML من القالب"""
    
    # قراءة القالب
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # توليد المحتوى الذكي
    smart_content = generate_smart_content(article_data)
    
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
        '{{CONTENT}}': smart_content
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
            if 'Content coming soon' in existing or len(existing) < 3000:
                # تحديث الملف فقط إذا كان placeholder
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

if __name__ == "__main__":
    main()
