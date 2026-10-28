@echo off
chcp 65001 > nul
echo ====================================================================
echo DONG BO DU LIEU HOC BONG HANG NGAY LEN SUPABASE (PGVECTOR)
echo ====================================================================

cd /d "d:\Audio & Speech\scholarship_system"
python daily_crawler_sync.py

echo.
echo ====================================================================
echo HOAN THANH DONG BO!
echo ====================================================================
pause
