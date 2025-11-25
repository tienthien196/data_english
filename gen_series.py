import re
import json
import shutil
from pathlib import Path

# --- Cấu hình đường dẫn ---
BOOKS_PATH = Path(r"E:\DATA\1_test_Src\src\python\web_up_pdf\books.json")
THEMES_PATH = Path(r"E:\DATA\1_test_Src\src\python\web_up_pdf\themes.json")

# --- THEME RULES ---
THEME_RULES = [
    (r'\b(english|englisch|vocab|collocation|idiom|grammar|pronunciation|aviation english|cabin crew|cambridge|oxford|ielts|toeic|b2|dialogue|ngu phap|language|words\b.*\d{4}|\d{4}.*words)\b', 'Language Learning & English'),
    (r'\bdinosaur[s]?\b|\bprehistoric\b|\bJurassic\b|\bT\.?Rex\b', 'Dinosaurs & Prehistoric Life'),
    (r'\bspace\b|\bastronomy\b|\buniverse\b|\bstar[s]?\b|\bplanet[s]?\b|\bmoon\b|\bsolar system\b|\bnight sky\b|\bstarfinder\b', 'Space & Astronomy'),
    (r'\banimal[s]?\b|\bbug[s]?\b|\binsect[s]?\b|\bocean\b|\bsea\b|\bjungle\b|\bforest\b|\bnature\b|\bwildlife\b|\bbird[s]?\b|\bfish\b|\bsupernatural creatures\b|\bzoology\b|\bflora\b|\bearth\'s incredible\b', 'Nature & Animals'),
    (r'\bhistory\b|\bhistorical\b|\bancient\b|\brome\b|\begypt\b|\bcivil war\b|\bworld war\b|\bvietnam war\b|\bmedieval\b|\bemperor\b|\bking\b|\bqueen\b|\bleaders who changed\b|\bhistory of the world\b|\bon this day\b', 'History'),
    (r'\batlas\b|\bgeography\b|\bcountry[s]?\b|\bnation[s]?\b|\bworld\b.*\bmap\b|\btravel guide\b|\bjapan\b|\bgermany\b|\bcanada\b|\bsicily\b|\bcroatia\b|\bvietnam\b|\birish\b|\brussia\b|\bgreat cities\b|\bman-made wonders\b', 'Geography & World Cultures'),
    (r'\bscience\b|\bphysics\b|\bchemistry\b|\brobot[s]?\b|\btech\b|\btechnology\b|\binvention[s]?\b|\bsteam(?:punk)?\b|\bhow everything works\b|\bsuper simple (physics|chemistry)\b|\bSTEM\b|\bcoding\b|\bpython\b|\bquantum\b', 'Science & Technology'),
    (r'\bart\b|\bdesign\b|\bpainting[s]?\b|\bsculpture\b|\bfashion\b|\bphotograph[y]\b|\bcalligraphy\b|\bwatercolor\b|\bgreat paintings\b|\bart that changed\b', 'Art, Design & Photography'),
    (r'\bmath\b|\bmaths\b|\bmathematics\b|\bnumber[s]?\b|\bpi\b|\bwhy pi\b|\bthink of a number\b|\bmath wizard\b', 'Math & Logic'),
    (r'\bhealth\b|\bmedical\b|\bmedicine\b|\byoga\b|\barthritis\b|\bayurveda\b|\bback pain\b|\bstrength training\b|\bwellness\b|\bself care\b|\bhuman body\b|\bbrain\b', 'Health, Wellness & Medicine'),
    (r'\bcook\b|\bfood\b|\bkitchen\b|\bnutrition\b|\bdiet\b|\bweight loss\b|\bchocolate\b|\bbaking\b|\brecipe[s]?\b|\bfermenting\b|\beat beautiful\b|\bhealing foods\b', 'Cooking, Food & Nutrition'),
    (r'\bcraft[s]?\b|\bdiy\b|\bsewing\b|\bknit\b|\bcrochet\b|\bwoodwork\b|\bgarden[s]?\b|\bpaper craft\b|\bdressmaking\b|\bmake\b.*\bworld\b', 'Crafts, DIY & Sewing'),
    (r'\bwar\b|\bwarfare\b|\bmilitary\b|\bcombat\b|\bnaval\b|\bsoldier\b|\bweapon[s]?\b|\bbattle\b|\bworld war\b|\bmachines of war\b|\bfirearms\b', 'Military, Warfare & Weapons'),
    (r'\bbible\b|\breligion\b|\bislam\b|\bmyth[s]?\b|\bwitchcraft\b|\boccult\b|\bastrology\b|\bnorse\b|\bgreek\b|\bsikhs\b|\bphilosophy\b|\bfeminism book\b|\bbig ideas\b', 'Religion, Mythology & Philosophy'),
    (r'\bpsychology\b|\bmemory\b|\bconfidence\b|\bgoals\b|\bperformance\b|\bmanagement\b|\bpresentation[s]?\b|\bglobal citizen\b|\bhow to\b.*\bbetter\b|\bpersonal\b|\bmind\b', 'Psychology & Personal Development'),
    (r'\bsport[s]?\b|\bsoccer\b|\bfootball\b|\brunning\b|\bchess\b|\bballer\b|\bdance\b', 'Sports & Physical Activity'),
    (r'\bmusic\b|\bmusicians\b|\bchoreography\b|\bballet\b|\brecital\b', 'Music, Dance & Performing Arts'),
    (r'\bfirst\b.*\b(number|word|board)\b|\bplease and thank you\b|\bthings that go\b|\bflaptastic\b|\bbaby\b|\bchildren.*school\b|\bstuff to know\b', 'Children’s Early Learning'),
    (r'\bhappiful\b|\bauto express\b|\blove sewing\b|\bnational geographic\b|_freemagazines\.top\b', 'Magazines & Periodicals'),
]

DEFAULT_THEME = "Others / General Knowledge"

def normalize_theme_id(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

def detect_theme(text: str) -> str:
    text_lower = text.lower()
    for pattern, theme_name in THEME_RULES:
        if re.search(pattern, text_lower):
            return theme_name
    return DEFAULT_THEME

def main():
    # ✅ Sửa lỗi backup ở đây
    books_backup = BOOKS_PATH.with_name(BOOKS_PATH.name + '.bak')
    themes_backup = THEMES_PATH.with_name(THEMES_PATH.name + '.bak')
    
    shutil.copy(BOOKS_PATH, books_backup)
    if THEMES_PATH.exists():
        shutil.copy(THEMES_PATH, themes_backup)

    with open(BOOKS_PATH, 'r', encoding='utf-8') as f:
        books = json.load(f)

    updated_books = []
    theme_dict = {}

    for book in books:
        source = (book.get("filename", "") + " " + book.get("title", "")).strip()
        theme_name = detect_theme(source)
        theme_id = normalize_theme_id(theme_name)

        book["themeName"] = theme_name
        book["themeId"] = theme_id
        updated_books.append(book)

        if theme_id not in theme_dict:
            theme_dict[theme_id] = {
                "themeId": theme_id,
                "themeName": theme_name,
                "description": f"Books about: {theme_name}",
                "coverUrl": book.get("coverUrl", ""),
                "books": []
            }
        theme_dict[theme_id]["books"].append(book)

    with open(BOOKS_PATH, 'w', encoding='utf-8') as f:
        json.dump(updated_books, f, indent=2, ensure_ascii=False)

    with open(THEMES_PATH, 'w', encoding='utf-8') as f:
        json.dump(list(theme_dict.values()), f, indent=2, ensure_ascii=False)

    print(f"✅ Đã phân loại {len(updated_books)} sách theo chủ đề.")
    print(f"✅ Đã tạo {len(theme_dict)} chủ đề.")
    print(f"📁 Backup đã lưu: {books_backup}")

if __name__ == "__main__":
    main()