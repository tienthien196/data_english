@echo off
setlocal

echo.
echo 🚀 Bắt đầu triển khai...

:: 1. Chạy setup.py để tạo docs.json và cover
python setup.py
if %errorlevel% neq 0 (
    echo ❌ Lỗi khi chạy setup.py
    exit /b 1
)

:: 2. Git add tất cả file cần thiết
git add ./docs.json
git add ./covers/
git add ./docs/
git add ./index.html
git add ./setup.py
git add ./deploy.bat

:: 3. Commit
set /p COMMIT_MSG="📝 Nhập ghi chú commit (Enter để dùng mặc định): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Update documents and covers

git commit -m "%COMMIT_MSG%"
if %errorlevel% neq 0 (
    echo ⚠️ Không có thay đổi để commit.
)

:: 4. Push
echo 📤 Đang đẩy lên GitHub...
git push origin main
if %errorlevel% equ 0 (
    echo.
    echo ✅ Triển khai thành công!
) else (
    echo ❌ Lỗi khi push. Kiểm tra kết nối hoặc quyền truy cập.
)

pause