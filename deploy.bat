@echo off
setlocal

echo 🚀 Bắt đầu triển khai (PDF lưu trên GitHub Releases)...

:: Chạy setup — tự động upload file mới nếu có
python setup.py
if %errorlevel% neq 0 (
    echo ❌ Lỗi khi chạy setup.py
    exit /b 1
)

:: Chỉ add file nhẹ (KHÔNG có PDF)
git add books.json
git add series.json
git add covers/
git add previews/
git add index.html
git add setup.py
git add deploy.bat
git add .gitignore

:: Commit
set /p MSG="📝 Ghi chú commit: "
if "%MSG%"=="" set MSG=Update document metadata & assets

git commit -m "%MSG%" --quiet
git push origin main

echo.
echo ✅ Deploy thành công!
echo 🌐 Web: https://tienthien196.github.io/data_english/
pause