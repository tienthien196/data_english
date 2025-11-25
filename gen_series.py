import re
import json
import shutil
from pathlib import Path

# --- Cấu hình đường dẫn ---
BOOKS_PATH = Path(r"E:\DATA\1_test_Src\src\python\web_up_pdf\books.json")
SERIES_PATH = Path(r"E:\DATA\1_test_Src\src\python\web_up_pdf\series.json")

# --- RULES: tên file → seriesName ---
SERIES_RULES = [
    # Loạt sách chính
    (r'\bDK Eyewitness\b', 'DK Eyewitness'),
    (r'\bDK Workbooks\b', 'DK Workbooks'),
    (r'\bMy Encyclopedia of Very Important\b', 'My Encyclopedia of Very Important'),
    (r'\bDK Life Stories\b', 'DK Life Stories'),
    (r'\bFearless Knitting Workbook\b', 'Crafts & DIY'),
    
    # Chủ đề cụ thể
    (r'\bAnimal[s]?\b', 'Nature & Animals'),
    (r'\bDinosaur[s]?\b', 'Dinosaurs'),
    (r'\bWarfare\b|\bCivil War\b|\bMilitary\b', 'Military & Warfare'),
    (r'\bPhotography\b', 'Art & Design'),
    (r'\bBallet\b|\bDance\b|\bMusician[s]?\b', 'Art & Design'),
    (r'\bJapan\b|\bJapanese\b', 'Culture & Travel'),
    (r'\bIslam\b', 'Religion & Philosophy'),
    (r'\bShakespeare\b', 'Literature & Philosophy'),
    (r'\bAncient Egypt\b', 'History'),
    (r'\bHistory\b', 'History'),
    (r'\bAtlas\b|\bPlanet\b|\bWorld\b', 'Geography'),
    (r'\bRocks\b|\bMinerals\b|\bEarth\b', 'Science'),
    (r'\bInventions\b|\bRobot[s]?\b', 'Science & Technology'),
    (r'\bChocolate\b|\bFood\b', 'Wellness & Lifestyle'),
    (r'\bCareers\b|\bManagement\b|\bPerformance\b|\bGoals\b|\bPresentations\b', 'Mind & Philosophy'),
    (r'\bGlobal Citizen\b', 'Social Studies'),
]


# --- Chuẩn hóa seriesId từ seriesName ---
def normalize_series_id(name: str) -> str:
    # Chuyển "DK Eyewitness" → "dk_eyewitness"
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

# --- Phân loại seriesName từ filename hoặc title ---
def detect_series_name(text: str) -> str:
    for pattern, series_name in SERIES_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return series_name
    return "Others Book"  # mặc định

# --- Main logic ---
def main():
    # Backup
    shutil.copy(BOOKS_PATH, BOOKS_PATH.with_suffix('.json.bak'))
    shutil.copy(SERIES_PATH, SERIES_PATH.with_suffix('.json.bak'))

    # Đọc books.json
    with open(BOOKS_PATH, 'r', encoding='utf-8') as f:
        books = json.load(f)

    # Cập nhật series cho từng sách
    updated_books = []
    series_dict = {}  # seriesId → {info + list books}

    for book in books:
        # Dùng filename hoặc title để phân loại
        source_text = book.get("filename", "") + " " + book.get("title", "")
        detected_name = detect_series_name(source_text)
        detected_id = normalize_series_id(detected_name)

        # Cập nhật thông tin sách
        book["seriesName"] = detected_name
        book["seriesId"] = detected_id
        updated_books.append(book)

        # Nhóm theo series
        if detected_id not in series_dict:
            series_dict[detected_id] = {
                "seriesId": detected_id,
                "seriesName": detected_name,
                "description": f"Collection: {detected_name}",
                "coverUrl": book.get("coverUrl", ""),  # lấy cover đầu tiên làm đại diện
                "books": []
            }
        series_dict[detected_id]["books"].append(book)

    # Ghi lại books.json
    with open(BOOKS_PATH, 'w', encoding='utf-8') as f:
        json.dump(updated_books, f, indent=2, ensure_ascii=False)

    # Ghi lại series.json
    series_list = list(series_dict.values())
    with open(SERIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(series_list, f, indent=2, ensure_ascii=False)

    print(f"✅ Đã cập nhật {len(updated_books)} sách vào {BOOKS_PATH}")
    print(f"✅ Đã tạo {len(series_list)} loạt sách trong {SERIES_PATH}")
    print("📁 Đã tạo file backup: *.json.bak")

if __name__ == "__main__":
    main()