import re
import json
import shutil
from pathlib import Path

# --- Cấu hình đường dẫn ---
BOOKS_PATH = Path(r"E:\DATA\1_test_Src\src\python\web_up_pdf\books.json")
SERIES_PATH = Path(r"E:\DATA\1_test_Src\src\python\web_up_pdf\series.json")

# --- RULES: phát hiện chính xác TÊN SERIES CHÍNH THỨC ---
SERIES_RULES = [
    # 1. My Encyclopedia of Very Important…
    (r'\bMy Encyclopedia of Very Important\b', 'My Encyclopedia of Very Important'),

    # 2. DK Workbooks (Language Arts, Math and Science)
    (r'\bDK Workbooks\b.*?(Language Arts|Math|Science)', 'DK Workbooks'),

    # 3. DK Life Stories
    (r'\bDK Life Stories\b', 'DK Life Stories'),

    # 4. DK Eyewitness Books (kể cả Eyewitness Travel / Eyewitness)
    (r'\bDK Eyewitness\b', 'DK Eyewitness'),

    # 5. DK Children’s Encyclopedia / The New Children's Encyclopedia
    (r'\bDK Children.*Encyclopedia\b|\bThe New Children[\'’]?s Encyclopedia\b', 'DK Children’s Encyclopedia'),

    # 6. DK Pocket Genius
    (r'\bPocket Genius\b', 'DK Pocket Genius'),

    # 7. DK Let’s Look
    (r'\bDK Let[\'’]?s Look\b', 'DK Let’s Look'),

    # 8. DK First Steps / My First Board Book
    (r'\bDK First Steps\b|\bMy First (Number|Word|Bible) Board Book\b', 'DK First Steps'),

    # 9. DK Readers
    (r'\bDK Readers\b', 'DK Readers'),

    # 10. DK Visual Encyclopedia (bao gồm Science, Geography, Warfare, Universe, v.v.)
    (r'\bVisual Encyclopedia\b|\bDK.*Visual.*Encyclopedia\b|\bDK Science.*Visual\b|\bDK Geography.*Visual\b|\bDK.*Warfare.*Visual\b|\bDK.*Universe.*Visual\b', 'DK Visual Encyclopedia'),

    # 11. Complete Step-by-Step / DIY / Crafts (Knitting, Crochet, Woodwork, Baking…)
    (r'\bComplete Step.?by.?Step\b|\bFearless Knitting Workbook\b|\bDK Knitting Book\b|\bCrochet.*Complete\b|\bWoodwork.*Step\b|\bComplete.*Garden.*Guide\b|\bBaking.*Book\b', 'DK Complete Step-by-Step Guides'),

    # 12. DK Reference Atlas / Student Atlas / Complete Atlas
    (r'\bComplete Atlas of the World\b|\bStudent Atlas\b|\bReference World Atlas\b', 'DK Reference Atlas'),

    # 13. DK Illustrated Cook / Food & Kitchen (kể cả Visual Dictionary Food)
    (r'\bIllustrated Cook.*Book\b|\bVisual Dictionary.*Food\b|\bDK.*Kitchen\b|\bBest ever baking book\b', 'DK Food & Kitchen'),

    # 14. DK Art / Art School / How to Draw / Painting
    (r'\bDK Art School\b|\bIntroduction to Drawing\b|\bIntroduction to Oil Painting\b|\bHow to.*Ballet\b|\bBallet.*Definitive\b|\bGreat Paintings\b|\bHow to be an artist\b', 'DK Art & Design'),

    # 15. DK Science of… (Yoga, Running, Cooking, Nutrition…)
    (r'\bScience of (Yoga|Running|Cooking|Nutrition)\b', 'DK Science of…'),

    # 16. DK 100 / 1,000 Things / Big Quiz Books
    (r'\b100 Women Who Made History\b|\bOne Million Things\b|\bBig Trivia Quiz Book\b|\b1,?000 Things\b|\b1000 Words.*STEM\b', 'DK 100 / 1,000 Things'),

    # 17. DK Marvel / Star Wars / Licensed Media
    (r'\bMarvel.*Character Encyclopedia\b|\bStar Wars.*Character Encyclopedia\b|\bBlack Panther.*Wakanda\b|\bAvengers.*Guide\b', 'DK Licensed Media (Marvel / Star Wars)'),

    # 18. DK Wellness & Fitness / Health / Back Pain / Nutrition
    (r'\bStrengthen Your Back\b|\bEssential Strength Training\b|\bComplete Massage\b|\bMedical Checkup Book\b|\bAyurveda\b|\bArthritis\b', 'DK Wellness & Fitness'),

    # 19. DK Philosophy / Big Ideas Simply Explained
    (r'\bBig Ideas Simply Explained\b|\bSimply Philosophy\b|\bSimply Quantum Physics\b|\bHeads Up Psychology\b', 'DK Philosophy & Psychology'),

    # 20. DK History Map by Map / Visual History
    (r'\bHistory.*Map by Map\b|\bTimelines of History\b|\bHistory Year by Year\b|\bOn This Day.*History\b', 'DK History Map by Map'),
]

# --- Chuẩn hóa seriesId từ seriesName ---
def normalize_series_id(name: str) -> str:
    # Ví dụ: "DK Eyewitness" → "dk_eyewitness"
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

# --- Phát hiện series từ văn bản (filename + title) ---
def detect_series_name(text: str) -> str:
    for pattern, series_name in SERIES_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return series_name
    return "Others Book"

# --- Main logic ---
def main():
    # Backup files
    shutil.copy(BOOKS_PATH, BOOKS_PATH.with_suffix('.json.bak'))
    shutil.copy(SERIES_PATH, SERIES_PATH.with_suffix('.json.bak'))

    # Đọc books.json
    with open(BOOKS_PATH, 'r', encoding='utf-8') as f:
        books = json.load(f)

    updated_books = []
    series_dict = {}

    for book in books:
        source_text = (book.get("filename", "") + " " + book.get("title", "")).strip()
        detected_name = detect_series_name(source_text)
        detected_id = normalize_series_id(detected_name)

        book["seriesName"] = detected_name
        book["seriesId"] = detected_id
        updated_books.append(book)

        if detected_id not in series_dict:
            series_dict[detected_id] = {
                "seriesId": detected_id,
                "seriesName": detected_name,
                "description": f"Collection: {detected_name}",
                "coverUrl": book.get("coverUrl", ""),
                "books": []
            }
        series_dict[detected_id]["books"].append(book)

    # Ghi lại files
    with open(BOOKS_PATH, 'w', encoding='utf-8') as f:
        json.dump(updated_books, f, indent=2, ensure_ascii=False)

    with open(SERIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(list(series_dict.values()), f, indent=2, ensure_ascii=False)

    print(f"✅ Đã cập nhật {len(updated_books)} sách.")
    print(f"✅ Đã tạo {len(series_dict)} series.")
    print("📁 Đã sao lưu: *.json.bak")

if __name__ == "__main__":
    main()