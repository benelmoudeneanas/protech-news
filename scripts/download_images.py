#!/usr/bin/env python3
"""
Image Downloader for ProTech News
يقرأ الصور من data.js، يحملها، ويخزنها محلياً
"""

import os
import re
import hashlib
import requests
from urllib.parse import urlparse
from pathlib import Path

# المسارات
DATA_JS_PATH = "assets/js/data.js"
IMAGES_DIR = "assets/images/articles"
TEMP_DATA_JS = "assets/js/data.js.backup"

def ensure_directories():
    """التأكد من وجود المجلدات"""
    os.makedirs(IMAGES_DIR, exist_ok=True)

def parse_data_js():
    """قراءة وتحليل data.js لاستخراج الصور"""
    
    with open(DATA_JS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # استخراج جميع روابط الصور
    # البحث عن: img: "https://..." أو img: 'https://...'
    img_pattern = r'img\s*:\s*["\']([^"\']+)["\']'
    images = re.findall(img_pattern, content)
    
    return content, images

def get_image_extension(url):
    """استخراج امتداد الصورة من الرابط"""
    parsed = urlparse(url)
    path = parsed.path
    
    # محاولة استخراج الامتداد من الرابط
    ext = os.path.splitext(path)[1]
    
    # إذا مافيهش امتداد، استعمل .jpg كافتراضي
    if not ext or ext not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
        ext = '.jpg'
    
    return ext

def generate_local_filename(url):
    """توليد اسم ملف محلي من الرابط"""
    # استعمال hash باش نتجنب تكرار الأسماء
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    ext = get_image_extension(url)
    return f"article-{url_hash}{ext}"

def download_image(url, save_path):
    """تحميل صورة من رابط"""
    try:
        print(f"      ⬇️  تحميل: {url[:60]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # حفظ الصورة
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(save_path) / 1024  # KB
        print(f"      ✅ تم التحميل: {os.path.basename(save_path)} ({file_size:.1f} KB)")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"      ❌ فشل التحميل: {str(e)[:50]}")
        return False
    except Exception as e:
        print(f"      ❌ خطأ: {str(e)[:50]}")
        return False

def process_images():
    """معالجة وتحميل جميع الصور"""
    
    ensure_directories()
    
    # قراءة data.js
    content, images = parse_data_js()
    
    if not images:
        print("⚠️  لم يتم العثور على صور في data.js")
        return
    
    print(f"\n📊 تم العثور على {len(images)} صورة")
    print("=" * 70)
    
    # خريطة للاستبدال (رابط قديم -> رابط جديد)
    replacements = {}
    downloaded = 0
    skipped = 0
    failed = 0
    
    for i, img_url in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] معالجة الصورة...")
        
        # تجنب الصور المحلية
        if img_url.startswith('../') or img_url.startswith('assets/'):
            print(f"      ⏭️  تخطي: صورة محلية بالفعل")
            skipped += 1
            continue
        
        # توليد اسم الملف المحلي
        local_filename = generate_local_filename(img_url)
        local_path = os.path.join(IMAGES_DIR, local_filename)
        
        # التحقق إذا كانت الصورة موجودة مسبقاً
        if os.path.exists(local_path):
            print(f"      ✅ موجود مسبقاً: {local_filename}")
            skipped += 1
        else:
            # تحميل الصورة
            if download_image(img_url, local_path):
                downloaded += 1
            else:
                failed += 1
                continue
        
        # إضافة للاستبدالات
        # المسار النسبي من root: assets/images/articles/xxx.jpg
        new_url = f"assets/images/articles/{local_filename}"
        replacements[img_url] = new_url
    
    print("\n" + "=" * 70)
    print(f"📦 ملخص التحميل:")
    print(f"   ✅ تم التحميل: {downloaded}")
    print(f"   ⏭️  متخطاة: {skipped}")
    print(f"   ❌ فشلت: {failed}")
    print(f"   📊 إجمالي: {len(images)}")
    
    return content, replacements

def update_data_js(content, replacements):
    """تحديث data.js بالمسارات المحلية"""
    
    if not replacements:
        print("\n⚠️  لا توجد استبدالات للتطبيق")
        return
    
    print("\n" + "=" * 70)
    print("🔄 تحديث data.js...")
    
    # حفظ نسخة احتياطية
    backup_path = DATA_JS_PATH + ".backup"
    with open(DATA_JS_PATH, 'r', encoding='utf-8') as f:
        with open(backup_path, 'w', encoding='utf-8') as bf:
            bf.write(f.read())
    
    print(f"   💾 نسخة احتياطية: {backup_path}")
    
    # استبدال الروابط
    updated_content = content
    replaced_count = 0
    
    for old_url, new_url in replacements.items():
        if old_url in updated_content:
            updated_content = updated_content.replace(old_url, new_url)
            replaced_count += 1
            print(f"   ✅ استبدال: {os.path.basename(new_url)}")
    
    # حفظ الملف المحدث
    with open(DATA_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"\n   ✅ تم تحديث {replaced_count} رابط في data.js")

def update_existing_html_files():
    """تحديث ملفات HTML الموجودة بالمسارات الجديدة"""
    
    articles_dir = "articles"
    
    if not os.path.exists(articles_dir):
        return
    
    print("\n" + "=" * 70)
    print("🔄 تحديث ملفات HTML الموجودة...")
    
    html_files = [f for f in os.listdir(articles_dir) if f.endswith('.html')]
    
    if not html_files:
        print("   ⚠️  لا توجد ملفات HTML")
        return
    
    # قراءة الاستبدالات من data.js
    with open(DATA_JS_PATH, 'r', encoding='utf-8') as f:
        data_content = f.read()
    
    # استخراج المسارات المحلية
    local_images = re.findall(r'img\s*:\s*["\']assets/images/articles/([^"\']+)["\']', data_content)
    
    updated_count = 0
    
    for html_file in html_files:
        file_path = os.path.join(articles_dir, html_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # استبدال روابط الصور الخارجية بالمحلية
        original_content = html_content
        
        # البحث عن src="https://..." أو src='https://...'
        external_images = re.findall(r'src=["\']https://[^"\']+["\']', html_content)
        
        for ext_img in external_images:
            # محاولة إيجاد المسار المحلي المناسب
            for local_img in local_images:
                # إذا وجدنا مطابقة، نستبدل
                local_path = f'../assets/images/articles/{local_img}'
                html_content = re.sub(
                    r'src=["\']https://[^"\']+' + re.escape(local_img[-20:]) + r'[^"\']*["\']',
                    f'src="{local_path}"',
                    html_content
                )
        
        # حفظ إذا تغير المحتوى
        if html_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            updated_count += 1
            print(f"   ✅ محدث: {html_file}")
    
    print(f"\n   ✅ تم تحديث {updated_count} ملف HTML")

def main():
    """البرنامج الرئيسي"""
    
    print("=" * 70)
    print("🖼️  ProTech Image Downloader & Localizer")
    print("=" * 70)
    
    # التحقق من وجود data.js
    if not os.path.exists(DATA_JS_PATH):
        print(f"❌ {DATA_JS_PATH} غير موجود!")
        return
    
    try:
        # معالجة وتحميل الصور
        content, replacements = process_images()
        
        # تحديث data.js
        if replacements:
            update_data_js(content, replacements)
            
            # تحديث ملفات HTML الموجودة (اختياري)
            # update_existing_html_files()
        
        print("\n" + "=" * 70)
        print("✅ تم الانتهاء بنجاح!")
        print("=" * 70)
        print("\n💡 الخطوات التالية:")
        print("   1. تحقق من المجلد: assets/images/articles/")
        print("   2. راجع data.js (نسخة احتياطية: data.js.backup)")
        print("   3. شغل السكريبت المولد: python3 scripts/auto_generate_from_data.py")
        print("   4. Commit & Push للتغييرات")
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
