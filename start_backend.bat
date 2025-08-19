@echo off
echo ================================
echo   CASA DE PADUA - BACKEND
echo ================================
echo.
echo Activando entorno virtual...
call .\env\Scripts\activate.bat

echo.
echo Iniciando servidor backend...
echo Servidor disponible en: http://127.0.0.1:8000
echo Documentacion en: http://127.0.0.1:8000/docs
echo.
echo Para detener el servidor presiona Ctrl+C
echo.

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
