#!/usr/bin/env python3
# setup.py

import fitz  # PyMuPDF
import os
import json
import sys
from pathlib import Path
from PIL import Image

# ========== Cấu hình ==========
PDF_ROOT = Path("./docs")
COVER_DIR = Path("./covers")
PREVIEW_DIR = Path("./previews")  # thư mục cho ảnh 4-trang gộp
OUTPUT_JSON = Path("./books.json")

# ========== Chuẩn bị ==========
COVER_DIR.mkdir(exist_ok=True)
PREVIEW_DIR.mkdir(exist_ok=True)

def get_file_size_mb(filepath: Path) -> float:
    return round(filepath.stat().st_size / (1024 * 1024), 2)

def extract_cover_and_preview(pdf_path: Path, cover_path: Path, preview_path: Path):
    """Tạo ảnh bìa (trang 1) và preview (4 trang đầu gộp dọc)."""
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            doc.close()
            return False

        # --- 1. Tạo ảnh bìa (trang đầu) ---
        if not cover_path.exists():
            page0 = doc[0]
            mat = fitz.Matrix(1.3, 1.3)  # ~130 DPI
            pix = page0.get_pixmap(matrix=mat)
            pix.save(str(cover_path))

        # --- 2. Tạo preview 4 trang đầu (gộp dọc) ---
        if not preview_path.exists():
            images = []
            num_pages = min(4, len(doc))
            for i in range(num_pages):
                page = doc[i]
                mat = fitz.Matrix(0.8, 0.8)  # nhỏ hơn để tiết kiệm
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)

            # Gộp dọc
            total_height = sum(img.height for img in images)
            max_width = max(img.width for img in images)
            merged = Image.new("RGB", (max_width, total_height), "white")

            y_offset = 0
            for img in images:
                merged.paste(img, (0, y_offset))
                y_offset += img.height

            merged.save(preview_path, "JPEG", quality=85)

        doc.close()
        return True

    except Exception as e:
        print(f"⚠️  Lỗi xử lý {pdf_path.name}: {e}")
        return False

# ========== Quét thư mục ==========
all_books = []
series_map = {}  # seriesId -> {info + list books}

# Duyệt từng thư mục con trong ./docs/
for series_dir in PDF_ROOT.iterdir():
    if not series_dir.is_dir():
        continue  # bỏ qua file (nếu có)

    series_id = series_dir.name
    series_name = series_id.replace("_", " ").replace("-", " ").title()  # đơn giản hóa tên

    # Tạo cover đại diện cho bộ (tạm thời dùng cover của cuốn đầu)
    series_cover_url = None

    pdf_files = sorted(series_dir.glob("*.pdf"))
    books_in_series = []

    for pdf_path in pdf_files:
        stem = pdf_path.stem
        filename = pdf_path.name

        # Đường dẫn ảnh
        cover_path = COVER_DIR / f"{series_id}_{stem}.jpg"
        preview_path = PREVIEW_DIR / f"{series_id}_{stem}_preview.jpg"

        # Tạo ảnh nếu chưa có
        success = extract_cover_and_preview(pdf_path, cover_path, preview_path)

        # URL tương đối (cho web)
        rel_pdf = str(pdf_path).replace("\\", "/")
        rel_cover = str(cover_path).replace("\\", "/") if success else "https://placehold.co/300x400/d1d5db/6b7280?text=No+Cover"
        rel_preview = str(preview_path).replace("\\", "/") if success else None

        # Giữ lại cover đầu tiên làm cover bộ (nếu chưa có)
        if series_cover_url is None and success:
            series_cover_url = rel_cover

        book_entry = {
            "id": len(all_books) + 1,
            "filename": filename,
            "title": stem.replace("_", " ").title(),
            "path": rel_pdf,
            "coverUrl": rel_cover,
            "previewUrl": rel_preview,  # <-- mới: dùng ở trang chi tiết
            "size": f"{get_file_size_mb(pdf_path)} MB",
            "author": "Unknown",
            "uploadedAt": "2025-01-01T00:00:00Z",  # có thể lấy từ file stat nếu cần
            "pages": 0,  # có thể điền sau nếu mở lại PDF
            "seriesId": series_id,
        }
        books_in_series.append(book_entry)
        all_books.append(book_entry)

    # Thêm bộ vào map (dùng cho dashboard theo series)
    series_map[series_id] = {
        "seriesId": series_id,
        "seriesName": series_name,
        "description": f"Series: {series_name}",
        "coverUrl": series_cover_url or "https://placehold.co/300x400/cccccc/666666?text=Series",
        "createdAt": "2025-01-01T00:00:00Z",
        "books": books_in_series
    }

# ========== Xuất 2 file JSON ==========
# 1. Toàn bộ sách (dùng cho tìm kiếm toàn cục)
with open("books.json", "w", encoding="utf-8") as f:
    json.dump(all_books, f, ensure_ascii=False, indent=2)

# 2. Theo bộ (dùng cho dashboard admin)
with open("series.json", "w", encoding="utf-8") as f:
    json.dump(list(series_map.values()), f, ensure_ascii=False, indent=2)

# ========== Thông báo ==========
print(f"\n✅ Đã xử lý:")
print(f"   - {len(all_books)} sách")
print(f"   - {len(series_map)} bộ")
print(f"\n📁 Thư mục ảnh:")
print(f"   - Covers: {COVER_DIR}/")
print(f"   - Previews: {PREVIEW_DIR}/")
print(f"\n📄 JSON xuất ra:")
print(f"   - books.json (toàn bộ sách)")
print(f"   - series.json (theo bộ – dùng cho dashboard)")