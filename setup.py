#!/usr/bin/env python3
# setup.py

import os
import json
import requests
from pathlib import Path
from urllib.parse import quote
from PIL import Image
import fitz  # PyMuPDF

# === Cấu hình ===
PDF_ROOT = Path("./docs")
COVER_DIR = Path("./covers")
PREVIEW_DIR = Path("./previews")
BOOKS_JSON = Path("./books.json")
SERIES_JSON = Path("./series.json")
STATE_FILE = Path("./upload_state.json")  # Local only — KHÔNG commit

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise EnvironmentError("❌ GITHUB_TOKEN chưa được đặt! Dùng lệnh: set GITHUB_TOKEN=your_token")

OWNER = "tienthien196"
REPO = "data_english"
RELEASE_TAG = "v3"  # ← Tag cố định, public, bền vững
RELEASE_NAME = "PDF Library v1"

API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# === Chuẩn bị thư mục ===
COVER_DIR.mkdir(exist_ok=True)
PREVIEW_DIR.mkdir(exist_ok=True)

# === Hàm hỗ trợ ===
def get_file_size_mb(filepath: Path) -> float:
    return round(filepath.stat().st_size / (1024 * 1024), 2)

def create_2x2_preview(doc, preview_path: Path):
    pages_to_show = min(4, len(doc))
    images = []
    for i in range(pages_to_show):
        page = doc[i]
        mat = fitz.Matrix(0.75, 0.75)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = img.resize((540, 720), Image.Resampling.LANCZOS)
        images.append(img)
    
    placeholder = Image.new("RGB", (540, 720), "white")
    while len(images) < 4:
        images.append(placeholder)
    
    final = Image.new("RGB", (1080, 1440), "white")
    w, h = 540, 720
    final.paste(images[0], (0, 0))
    final.paste(images[1], (w, 0))
    final.paste(images[2], (0, h))
    final.paste(images[3], (w, h))
    final.save(preview_path, "JPEG", quality=88)

def get_or_create_public_release():
    """Lấy hoặc tạo release public với tag cố định 'v1'"""
    res = requests.get(f"{API_BASE}/releases", headers=HEADERS)
    if res.status_code == 200:
        for r in res.json():
            if r["tag_name"] == RELEASE_TAG and not r.get("draft", False):
                print(f"📦 Dùng release public: {r['name']}")
                return r["id"], r["upload_url"].replace("{?name,label}", "")
    
    print(f"🆕 Tạo release PUBLIC mới với tag: {RELEASE_TAG}")
    data = {
        "tag_name": RELEASE_TAG,
        "name": RELEASE_NAME,
        "body": "Public release for GitHub Pages — all PDFs are accessible via direct URL.",
        "draft": False,
        "prerelease": False
    }
    res = requests.post(f"{API_BASE}/releases", headers=HEADERS, json=data)
    if res.status_code == 201:
        r = res.json()
        return r["id"], r["upload_url"].replace("{?name,label}", "")
    else:
        raise Exception(f"❌ Tạo release public thất bại: {res.status_code} - {res.text}")

def get_existing_asset_names(release_id):
    """Lấy danh sách tên file đã có trong release trên GitHub"""
    assets_url = f"{API_BASE}/releases/{release_id}/assets"
    res = requests.get(assets_url, headers=HEADERS)
    if res.status_code == 200:
        return {asset["name"] for asset in res.json()}
    return set()

def upload_file(upload_url, filepath: Path):
    filename = filepath.name
    print(f"⬆️ Upload: {filename}")
    url = f"{upload_url}?name={quote(filename)}"
    with open(filepath, "rb") as f:
        headers = HEADERS.copy()
        headers["Content-Type"] = "application/pdf"
        res = requests.post(url, headers=headers, data=f)
    if res.status_code in (201, 200):
        return res.json()["browser_download_url"]
    else:
        raise Exception(f"❌ Upload thất bại ({filename}): {res.status_code}")

# === Main ===
def main():
    # Đọc trạng thái local
    state = {"uploaded_files": {}}
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    uploaded_files = state["uploaded_files"]

    # Quét toàn bộ PDF
    all_books = []
    series_dict = {}
    current_pdfs = set()

    for series_dir in PDF_ROOT.iterdir():
        if not series_dir.is_dir():
            continue
        series_id = series_dir.name
        series_name = series_id.replace("_", " ").replace("-", " ").title()
        books_in_series = []

        for pdf_path in sorted(series_dir.glob("*.pdf")):
            filename = pdf_path.name
            full_key = f"{series_id}/{filename}"
            current_pdfs.add(full_key)

            stem = pdf_path.stem
            cover_path = COVER_DIR / f"{series_id}_{stem}.jpg"
            preview_path = PREVIEW_DIR / f"{series_id}_{stem}_preview.jpg"

            if not cover_path.exists():
                doc = fitz.open(pdf_path)
                if doc:
                    pix = doc[0].get_pixmap(matrix=fitz.Matrix(1.3, 1.3))
                    pix.save(str(cover_path))
                doc.close()

            if not preview_path.exists():
                doc = fitz.open(pdf_path)
                create_2x2_preview(doc, preview_path)
                doc.close()

            # Dùng URL đã lưu nếu có
            url = uploaded_files.get(full_key)
            book = {
                "id": len(all_books) + 1,
                "filename": filename,
                "title": stem.replace("_", " ").title(),
                "path": url or f"./docs/{series_id}/{filename}",
                "coverUrl": str(cover_path).replace("\\", "/"),
                "previewUrl": str(preview_path).replace("\\", "/"),
                "size": f"{get_file_size_mb(pdf_path)} MB",
                "author": "Unknown",
                "seriesId": series_id,
                "seriesName": series_name
            }
            books_in_series.append(book)
            all_books.append(book)

        series_dict[series_id] = {
            "seriesId": series_id,
            "seriesName": series_name,
            "description": f"Collection: {series_name}",
            "coverUrl": books_in_series[0]["coverUrl"] if books_in_series else "",
            "books": books_in_series
        }

    # Phát hiện file mới (chưa có trong trạng thái local)
    new_files = []
    for series_dir in PDF_ROOT.iterdir():
        if not series_dir.is_dir():
            continue
        for pdf_path in series_dir.glob("*.pdf"):
            full_key = f"{series_dir.name}/{pdf_path.name}"
            if full_key not in uploaded_files:
                new_files.append((pdf_path, full_key))

    if new_files:
        print(f"\n📤 Có {len(new_files)} file mới cần xử lý...")
        release_id, upload_url = get_or_create_public_release()
        existing_assets = get_existing_asset_names(release_id)

        for pdf_path, full_key in new_files:
            filename = pdf_path.name
            if filename in existing_assets:
                # Dùng lại URL public (an toàn, bền vững)
                url = f"https://github.com/{OWNER}/{REPO}/releases/download/{RELEASE_TAG}/{quote(filename)}"
                print(f"⏭️  Đã tồn tại trên GitHub: {filename}")
            else:
                # Upload mới
                url = upload_file(upload_url, pdf_path)
            uploaded_files[full_key] = url

        # Cập nhật đường dẫn trong sách
        for book in all_books:
            full_key = f"{book['seriesId']}/{book['filename']}"
            if full_key in uploaded_files:
                book["path"] = uploaded_files[full_key]

        # Lưu trạng thái local
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"uploaded_files": uploaded_files}, f, ensure_ascii=False, indent=2)
        print("💾 Đã lưu trạng thái upload.")
    else:
        print("\n✅ Không có file mới để upload.")

    # Ghi JSON metadata
    with open(BOOKS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_books, f, ensure_ascii=False, indent=2)
    with open(SERIES_JSON, "w", encoding="utf-8") as f:
        json.dump(list(series_dict.values()), f, ensure_ascii=False, indent=2)

    print(f"\n✨ Hoàn tất! Tổng: {len(all_books)} sách, {len(series_dict)} bộ.")
    print("📁 Đã tạo ảnh cover & preview 2x2.")
    print("📄 Metadata đã xuất: books.json, series.json")

if __name__ == "__main__":
    main()