#!/usr/bin/env python3
"""
Resize Existing WebP Images
تصغير الصور WebP الموجودة من 1200px إلى 800px
"""

import os
from PIL import Image
from pathlib import Path

# المسارات
IMAGES_DIR = "assets/images/articles"

# إعدادات
WEBP_QUALITY = 85
MAX_WIDTH = 800  # ← الحجم الجديد

def resize_webp_image(image_path):
    """تصغير صورة WebP واحدة"""
    try:
        # قراءة الصورة
        img = Image.open(image_path)
        
        # الحجم الأصلي
        original_width = img.width
        original_height = img.height
        original_size = os.path.getsize(image_path) / 1024  # KB
        
        # تحقق إذا كانت محتاجة تصغير
        if img.width <= MAX_WIDTH:
            print(f"⏭️  {os.path.basename(image_path)}")
            print(f"   📏 الحجم: {img.width}x{img.height} (ما يحتاجش تصغير)\n")
            return False
        
        # تصغير مع الحفاظ على النسبة
        ratio = MAX_WIDTH / img.width
        new_height = int(img.height * ratio)
        img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
        
        # حفظ بنفس الاسم (استبدال)
        img.save(image_path, 'WEBP', quality=WEBP_QUALITY, method=6)
        
        # الحجم الجديد
        new_size = os.path.getsize(image_path) / 1024  # KB
        savings = ((original_size - new_size) / original_size) * 100
        
        print(f"✅ {os.path.basename(image_path)}")
        print(f"   📏 قبل: {original_width}x{original_height} ({original_size:.1f} KB)")
        print(f"   📐 بعد: {MAX_WIDTH}x{new_height} ({new_size:.1f} KB)")
        print(f"   💾 توفير: {savings:.0f}%\n")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في {os.path.basename(image_path)}: {str(e)}\n")
        return False

def resize_all_webp_images():
    """تصغير جميع صور WebP في المجلد"""
    
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ المجلد غير موجود: {IMAGES_DIR}")
        return
    
    # البحث عن جميع صور WebP
    webp_files = list(Path(IMAGES_DIR).glob('*.webp'))
    
    if not webp_files:
        print("⚠️  لا توجد صور WebP للتصغير")
        return
    
    print(f"📊 تم العثور على {len(webp_files)} صورة WebP")
    print(f"🎯 الحد الأقصى للعرض: {MAX_WIDTH}px")
    print(f"🎨 الجودة: {WEBP_QUALITY}%")
    print("=" * 70)
    print()
    
    resized_count = 0
    skipped_count = 0
    total_original = 0
    total_new = 0
    
    for i, img_file in enumerate(webp_files, 1):
        print(f"[{i}/{len(webp_files)}] معالجة...")
        img_path = str(img_file)
        
        # الحجم قبل
        size_before = os.path.getsize(img_path) / 1024
        total_original += size_before
        
        # التصغير
        if resize_webp_image(img_path):
            resized_count += 1
            size_after = os.path.getsize(img_path) / 1024
            total_new += size_after
        else:
            skipped_count += 1
            total_new += size_before
    
    # الإحصائيات النهائية
    print("=" * 70)
    print(f"📊 الإحصائيات النهائية:")
    print(f"   ✅ تم التصغير: {resized_count} صورة")
    print(f"   ⏭️  متخطاة: {skipped_count} صورة (صغيرة بالفعل)")
    print(f"   📊 إجمالي: {len(webp_files)} صورة")
    print()
    
    if resized_count > 0:
        total_savings = ((total_original - total_new) / total_original) * 100
        print(f"💾 التوفير الكلي:")
        print(f"   📥 الحجم قبل: {total_original:.1f} KB ({total_original/1024:.2f} MB)")
        print(f"   📤 الحجم بعد: {total_new:.1f} KB ({total_new/1024:.2f} MB)")
        print(f"   💰 التوفير: {total_savings:.0f}% ({(total_original-total_new)/1024:.2f} MB)")
    
    print("=" * 70)

def main():
    """البرنامج الرئيسي"""
    
    print("=" * 70)
    print("📐 تصغير صور WebP الموجودة")
    print(f"🎯 من أي حجم → {MAX_WIDTH}px عرض")
    print("=" * 70)
    print()
    
    resize_all_webp_images()
    
    print("\n" + "=" * 70)
    print("✅ تم الانتهاء!")
    print("=" * 70)
    print("\n💡 الخطوات التالية:")
    print("   1. تحقق من الصور: assets/images/articles/")
    print("   2. Commit & Push:")
    print("      git add assets/images/articles/")
    print("      git commit -m '📐 Resize images to 800px'")
    print("      git push")
    print()
    print("🚀 الآن الصور محسنة 100%!")

if __name__ == "__main__":
    main()
