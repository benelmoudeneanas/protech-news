#!/usr/bin/env python3
"""
Image Downloader for ProTech News with WebP Conversion
يقرأ الصور من data.js، يحملها، يحولها لـ WebP، ويخزنها محلياً
"""

import os
import re
import hashlib
import requests
from urllib.parse import urlparse
from pathlib import Path
from PIL import Image
from io import BytesIO

# المسارات
DATA_JS_PATH = "assets/js/data.js"
IMAGES_DIR = "assets/images/articles"
TEMP_DATA_JS = "assets/js/data.js.backup"

# إعدادات WebP
CONVERT_TO_WEBP = True  # ← غيرها لـ False إذا ما بغيتيش WebP
WEBP_QUALITY = 85  # جودة WebP (1-100، 85 ممتاز)
MAX_WIDTH = 800  # أقصى عرض للصور (باش يصغروا إلا كانو كبار بزاف)

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

def generate_local_filename(url, force_webp=False):
    """توليد اسم ملف محلي من الرابط"""
    # استعمال hash باش نتجنب تكرار الأسماء
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]

    # إذا بغينا نحولوا لـ WebP
    if CONVERT_TO_WEBP or force_webp:
        ext = '.webp'
    else:
        # استخراج الامتداد الأصلي
        parsed = urlparse(url)
        path = parsed.path
        ext = os.path.splitext(path)[1]

        # إذا مافيهش امتداد، استعمل .jpg كافتراضي
        if not ext or ext not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
            ext = '.jpg'

    return f"article-{url_hash}{ext}"

def convert_to_webp(image_data, save_path):
    """تحويل الصورة لـ WebP مع تحسين الحجم"""
    try:
        # فتح الصورة من البيانات
        img = Image.open(BytesIO(image_data))

        # تحويل RGBA إلى RGB إذا لزم الأمر
        if img.mode in ('RGBA', 'LA', 'P'):
            # إنشاء خلفية بيضاء
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # تصغير الصورة إذا كانت كبيرة بزاف
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
            print(f"      📐 تصغير: {img.width}x{img.height}")

        # حفظ كـ WebP
        img.save(save_path, 'WEBP', quality=WEBP_QUALITY, method=6)

        return True

    except Exception as e:
        print(f"      ❌ فشل التحويل لـ WebP: {str(e)[:50]}")
        return False

def download_and_convert_image(url, save_path):
    """تحميل صورة وتحويلها لـ WebP"""
    try:
        print(f"      ⬇️  تحميل: {url[:60]}...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        # قراءة البيانات
        image_data = response.content
        original_size = len(image_data) / 1024  # KB

        print(f"      📥 حجم أصلي: {original_size:.1f} KB")

        # التحويل لـ WebP
        if CONVERT_TO_WEBP:
            if convert_to_webp(image_data, save_path):
                webp_size = os.path.getsize(save_path) / 1024  # KB
                savings = ((original_size - webp_size) / original_size) * 100
                print(f"      ✅ WebP: {webp_size:.1f} KB (توفير {savings:.0f}%)")
                return True
            else:
                # إذا فشل التحويل، احفظها كما هي
                print(f"      ⚠️  الحفظ بالصيغة الأصلية...")
                with open(save_path, 'wb') as f:
                    f.write(image_data)
                return True
        else:
            # حفظ بدون تحويل
            with open(save_path, 'wb') as f:
                f.write(image_data)
            print(f"      ✅ تم الحفظ: {original_size:.1f} KB")
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
    if CONVERT_TO_WEBP:
        print(f"🔄 التحويل لـ WebP مفعل (جودة: {WEBP_QUALITY}%)")
    print("=" * 70)

    # خريطة للاستبدال (رابط قديم -> رابط جديد)
    replacements = {}
    downloaded = 0
    skipped = 0
    failed = 0
    total_original_size = 0
    total_webp_size = 0

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
            # تحميل وتحويل الصورة
            if download_and_convert_image(img_url, local_path):
                downloaded += 1
            else:
                failed += 1
                continue

        # إضافة للاستبدالات
        # المسار النسبي من root: assets/images/articles/xxx.webp
        new_url = f"assets/images/articles/{local_filename}"
        replacements[img_url] = new_url

    print("\n" + "=" * 70)
    print(f"📦 ملخص التحميل:")
    print(f"   ✅ تم التحميل: {downloaded}")
    print(f"   ⏭️  متخطاة: {skipped}")
    print(f"   ❌ فشلت: {failed}")
    print(f"   📊 إجمالي: {len(images)}")

    if CONVERT_TO_WEBP and downloaded > 0:
        print(f"\n💾 تم التحويل إلى WebP بجودة {WEBP_QUALITY}%")

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

def main():
    """البرنامج الرئيسي"""

    print("=" * 70)
    print("🖼️  ProTech Image Downloader & WebP Converter")
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

        print("\n" + "=" * 70)
        print("✅ تم الانتهاء بنجاح!")
        print("=" * 70)
        print("\n💡 الخطوات التالية:")
        print("   1. تحقق من المجلد: assets/images/articles/")
        print("   2. راجع data.js (نسخة احتياطية: data.js.backup)")
        print("   3. شغل السكريبت المولد: python3 scripts/auto_generate_from_data.py")
        print("   4. Commit & Push للتغييرات")

        if CONVERT_TO_WEBP:
            print(f"\n🎯 جميع الصور تم تحويلها لـ WebP بجودة {WEBP_QUALITY}%")

    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()