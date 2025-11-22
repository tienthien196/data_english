# setup.py


import fitz  # PyMuPDF
import os
import json
import sys
from pathlib import Path

PDF_DIR = r"./docs"
COVER_DIR = r"./covers"
OUTPUT_JSON = r"./docs.json"

os.makedirs(COVER_DIR, exist_ok=True)

def get_file_size_mb(filepath):
    return round(os.path.getsize(filepath) / (1024 * 1024), 2)

documents = []

for pdf_path in Path(PDF_DIR).glob("*.pdf"):
    filename = pdf_path.name
    stem = pdf_path.stem
    cover_path = Path(COVER_DIR) / f"{stem}.jpg"
    relative_pdf_path = str(pdf_path).replace("\\", "/")
    relative_cover_path = str(cover_path).replace("\\", "/")

    # Tạo ảnh bìa nếu chưa có
    if not cover_path.exists():
        print(f"🖼️  Đang tạo ảnh bìa: {cover_path}")
        try:
            doc = fitz.open(pdf_path)
            if len(doc) > 0:
                page = doc[0]
                mat = fitz.Matrix(1.3, 1.3)  # ~130 DPI – cân bằng chất lượng & kích thước
                pix = page.get_pixmap(matrix=mat)
                pix.save(str(cover_path))
            doc.close()
        except Exception as e:
            print(f"⚠️  Lỗi tạo cover cho {filename}: {e}")
            # Dùng ảnh placeholder nếu lỗi
            relative_cover_path = "https://placehold.co/300x400/d1d5db/6b7280?text=No+Cover"

    # Thêm vào danh sách
    documents.append({
        "id": len(documents) + 1,
        "name": filename,
        "path": relative_pdf_path,
        "coverUrl": relative_cover_path if cover_path.exists() else "https://placehold.co/300x400/d1d5db/6b7280?text=No+Cover",
        "size": f"{get_file_size_mb(pdf_path)} MB",
        "description": f"Tài liệu: {filename}"
    })

# Ghi JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2)

print(f"\n✅ Đã tạo {len(documents)} tài liệu trong '{OUTPUT_JSON}'")
print("📁 Đảm bảo các thư mục sau đã được git theo dõi:")
print(f"   - {PDF_DIR}/")
print(f"   - {COVER_DIR}/")
print(f"   - {OUTPUT_JSON}")