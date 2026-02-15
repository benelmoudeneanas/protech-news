#!/usr/bin/env python3
"""
Convert All Existing Images to WebP
تحويل جميع الصور الموجودة إلى WebP
"""

import os
import re
from PIL import Image
from pathlib import Path

# المسارات
DATA_JS_PATH = "assets/js/data.js"
IMAGES_DIR = "assets/images/articles"

# إعدادات WebP
WEBP_QUALITY = 85
MAX_WIDTH = 1200

def convert_image_to_webp(image_path):
    """تحويل صورة واحدة لـ WebP"""
    try:
        # قراءة الصورة
        img = Image.open(image_path)
        
        # تحويل RGBA إلى RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # تصغير إذا كانت كبيرة
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
        
        # اسم الملف الجديد
        base_name = os.path.splitext(image_path)[0]
        new_path = f"{base_name}.webp"
        
        # الحجم الأصلي
        original_size = os.path.getsize(image_path) / 1024
        
        # حفظ كـ WebP
        img.save(new_path, 'WEBP', quality=WEBP_QUALITY, method=6)
        
        # الحجم الجديد
        webp_size = os.path.getsize(new_path) / 1024
        savings = ((original_size - webp_size) / original_size) * 100
        
        print(f"✅ {os.path.basename(image_path)}")
        print(f"   📥 قبل: {original_size:.1f} KB")
        print(f"   📤 بعد: {webp_size:.1f} KB (توفير {savings:.0f}%)")
        
        # حذف الملف القديم
        os.remove(image_path)
        print(f"   🗑️  حذف القديم\n")
        
        return new_path, os.path.basename(image_path), os.path.basename(new_path)
        
    except Exception as e:
        print(f"❌ خطأ في {os.path.basename(image_path)}: {str(e)}\n")
        return None, None, None

def convert_all_images():
    """تحويل جميع الصور في المجلد"""
    
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ المجلد غير موجود: {IMAGES_DIR}")
        return []
    
    # البحث عن جميع الصور
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png']:
        image_files.extend(Path(IMAGES_DIR).glob(f'*{ext}'))
    
    if not image_files:
        print("⚠️  لا توجد صور للتحويل (jpg/png)")
        return []
    
    print(f"📊 تم العثور على {len(image_files)} صورة للتحويل")
    print("=" * 70)
    print()
    
    conversions = []
    total_original = 0
    total_webp = 0
    
    for i, img_file in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] تحويل...")
        img_path = str(img_file)
        
        # الحجم الأصلي
        original_size = os.path.getsize(img_path) / 1024
        total_original += original_size
        
        # التحويل
        new_path, old_name, new_name = convert_image_to_webp(img_path)
        
        if new_path:
            webp_size = os.path.getsize(new_path) / 1024
            total_webp += webp_size
            conversions.append((old_name, new_name))
    
    # الإحصائيات
    if conversions:
        total_savings = ((total_original - total_webp) / total_original) * 100
        print("=" * 70)
        print(f"📊 الإحصائيات:")
        print(f"   ✅ تم التحويل: {len(conversions)} صورة")
        print(f"   📥 الحجم الأصلي: {total_original:.1f} KB")
        print(f"   📤 الحجم الجديد: {total_webp:.1f} KB")
        print(f"   💾 التوفير: {total_savings:.0f}%")
        print("=" * 70)
    
    return conversions

def update_data_js(conversions):
    """تحديث data.js بأسماء الملفات الجديدة"""
    
    if not conversions:
        print("\n⚠️  لا توجد تحويلات للتطبيق")
        return
    
    if not os.path.exists(DATA_JS_PATH):
        print(f"\n⚠️  {DATA_JS_PATH} غير موجود")
        return
    
    print("\n🔄 تحديث data.js...")
    
    # قراءة data.js
    with open(DATA_JS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # حفظ نسخة احتياطية
    backup_path = DATA_JS_PATH + ".backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"   💾 نسخة احتياطية: {backup_path}")
    
    # تحديث الأسماء
    updated_content = content
    replaced_count = 0
    
    for old_name, new_name in conversions:
        if old_name in updated_content:
            updated_content = updated_content.replace(old_name, new_name)
            replaced_count += 1
            print(f"   ✅ {old_name} → {new_name}")
    
    # حفظ التحديث
    with open(DATA_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"\n   ✅ تم تحديث {replaced_count} رابط في data.js")

def main():
    """البرنامج الرئيسي"""
    
    print("=" * 70)
    print("🖼️  تحويل جميع الصور القديمة إلى WebP")
    print("=" * 70)
    print()
    
    # تحويل الصور
    conversions = convert_all_images()
    
    # تحديث data.js
    if conversions:
        update_data_js(conversions)
        
        print("\n" + "=" * 70)
        print("✅ تم الانتهاء بنجاح!")
        print("=" * 70)
        print("\n💡 الخطوات التالية:")
        print("   1. تحقق من المجلد: assets/images/articles/")
        print("   2. راجع data.js (نسخة احتياطية: data.js.backup)")
        print("   3. Commit & Push للتغييرات")
        print("\n🎯 جميع الصور الآن بصيغة WebP!")
    else:
        print("\n⚠️  لم يتم تحويل أي صور")

if __name__ == "__main__":
    main()
