import os
import json
from PIL import Image

# =============== CẤU HÌNH ===============
# Đường dẫn đến thư mục chứa books.json, series.json và thư mục covers/
BASE_DIR = r"E:\DATA\1_test_Src\src\python\web_up_pdf"

BOOKS_JSON = os.path.join(BASE_DIR, "books.json")
SERIES_JSON = os.path.join(BASE_DIR, "series.json")

COVERS_DIR = os.path.join(BASE_DIR, "covers")
THUMBNAILS_DIR = os.path.join(BASE_DIR, "thumbnails")

THUMB_SIZE = (300, 400)  # width, height — sẽ giữ tỷ lệ (thumbnail)
MAX_SIZE_BYTES = 50 * 1024  # ~50KB (chỉ để log, không ép)

# =============== TẠO THƯ MỤC ===============
os.makedirs(THUMBNAILS_DIR, exist_ok=True)

# =============== HÀM XỬ LÝ ẢNH ===============
def process_image(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            # Chuyển sang RGB nếu là PNG có alpha (WebP không hỗ trợ RGBA trực tiếp nếu quality thấp)
            if img.mode in ("RGBA", "P"):
                # Tạo nền trắng cho ảnh có alpha
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1])  # dùng alpha làm mask
                img = background

            # Resize giữ tỷ lệ
            img.thumbnail(THUMB_SIZE, Image.LANCZOS)

            # Lưu WebP
            img.save(output_path, "WEBP", quality=85, method=6)

            # Log kích thước
            size_kb = os.path.getsize(output_path) / 1024
            print(f"✅ {os.path.basename(output_path)} ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"❌ Lỗi xử lý {input_path}: {e}")

# =============== LẤY DANH SÁCH ẢNH CẦN XỬ LÝ ===============
cover_paths = set()

def add_cover_paths(data, key="coverUrl"):
    for item in data:
        url = item.get(key)
        if url and url.startswith("covers/"):
            # Chuyển URL thành đường dẫn local
            local_path = os.path.join(BASE_DIR, url)
            if os.path.isfile(local_path):
                cover_paths.add(local_path)
            else:
                print(f"⚠️ Không tìm thấy ảnh: {local_path}")

# Đọc books.json
if os.path.isfile(BOOKS_JSON):
    with open(BOOKS_JSON, "r", encoding="utf-8") as f:
        books = json.load(f)
    add_cover_paths(books)
else:
    print(f"❌ Không tìm thấy books.json tại: {BOOKS_JSON}")

# Đọc series.json
if os.path.isfile(SERIES_JSON):
    with open(SERIES_JSON, "r", encoding="utf-8") as f:
        series = json.load(f)
    add_cover_paths(series)
else:
    print(f"❌ Không tìm thấy series.json tại: {SERIES_JSON}")

print(f"\nTìm thấy {len(cover_paths)} ảnh bìa hợp lệ. Bắt đầu tạo thumbnail...\n")

# =============== XỬ LÝ TỪNG ẢNH ===============
for cover_path in sorted(cover_paths):
    filename = os.path.basename(cover_path)
    name, _ = os.path.splitext(filename)
    output_path = os.path.join(THUMBNAILS_DIR, name + ".webp")
    process_image(cover_path, output_path)

print(f"\n✅ Hoàn tất! Thumbnail đã lưu vào: {THUMBNAILS_DIR}")