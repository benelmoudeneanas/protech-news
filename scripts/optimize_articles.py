#!/usr/bin/env python3
"""
Script لتحديث جميع ملفات articles بتحسينات الأداء والـ accessibility
"""

import os
import re
from pathlib import Path

def update_article_file(file_path):
    """تحديث ملف article واحد"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. تحسين تحميل الخطوط - إضافة preload
        content = re.sub(
            r'<!-- Preconnect -->\s*<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>',
            '''<!-- Preconnect & Preload Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;900&family=Inter:wght@400;500;600;700;900&display=swap">''',
            content
        )
        
        # 2. تأجيل تحميل الخطوط و Font Awesome
        content = re.sub(
            r'<!-- Fonts -->\s*<link href="https://fonts\.googleapis\.com/css2\?family=Space\+Grotesk:wght@500;700;900&family=Inter:wght@400;500;600;700;900&display=swap" rel="stylesheet">\s*<link rel="stylesheet" href="https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/6\.4\.2/css/all\.min\.css">',
            '''<!-- Fonts - Async loading for better performance -->
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;900&family=Inter:wght@400;500;600;700;900&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
    <noscript><link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;900&family=Inter:wght@400;500;600;700;900&display=swap" rel="stylesheet"></noscript>
    
    <!-- Font Awesome - Deferred -->
    <link rel="preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" media="print" onload="this.media='all'">
    <noscript><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"></noscript>''',
            content
        )
        
        # 3. إضافة aria-hidden لجميع أيقونات Font Awesome
        content = re.sub(
            r'<i class="fas fa-([^"]+)"></i>',
            r'<i class="fas fa-\1" aria-hidden="true"></i>',
            content
        )
        
        # 4. تحسين الصور - إضافة loading و decoding و dimensions
        # البحث عن img tags بدون loading attribute
        content = re.sub(
            r'<img\s+src="([^"]+)"\s+alt="([^"]*)"(?!\s+loading)',
            r'<img src="\1" alt="\2" loading="lazy" decoding="async" width="800" height="450"',
            content
        )
        
        # 5. إضافة aria-label للأزرار
        content = re.sub(
            r'<button class="search-btn" onclick="toggleSearchModal\(\)">',
            r'<button class="search-btn" onclick="toggleSearchModal()" aria-label="Search articles">',
            content
        )
        
        content = re.sub(
            r'<div class="mobile-menu" id="mobile-menu">',
            r'<div class="mobile-menu" id="mobile-menu" role="button" aria-label="Toggle mobile menu" tabindex="0">',
            content
        )
        
        # 6. تحديث الروابط في الـ Footer (إصلاح SEO)
        content = re.sub(
            r'<a href="javascript:void\(0\)" onclick="([^"]+)">',
            r'<a href="#" onclick="\1; return false;">',
            content
        )
        
        # إذا تغير المحتوى، احفظ الملف
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"❌ خطأ في {file_path}: {e}")
        return False

def main():
    """البرنامج الرئيسي"""
    articles_dir = Path('/home/claude/protech-news-main/articles')
    
    if not articles_dir.exists():
        print(f"❌ المجلد غير موجود: {articles_dir}")
        return
    
    # الحصول على جميع ملفات HTML
    html_files = list(articles_dir.glob('*.html'))
    
    print(f"🔍 تم العثور على {len(html_files)} ملف article")
    print("⚡ جاري التحديث...\n")
    
    updated_count = 0
    for file_path in html_files:
        if update_article_file(file_path):
            updated_count += 1
            print(f"✅ تم تحديث: {file_path.name}")
    
    print(f"\n✨ تم الانتهاء!")
    print(f"📊 تم تحديث {updated_count} من {len(html_files)} ملف")

if __name__ == '__main__':
    main()
