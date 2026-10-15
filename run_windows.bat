@echo off
setlocal
if not exist .venv\Scripts\python.exe (
  echo Creating Python virtual environment...
  py -3 -m venv .venv || goto :error
)
call .venv\Scripts\activate.bat || goto :error
python -m pip install --upgrade pip || goto :error
pip install -r requirements.txt || goto :error
python main.py train || goto :error
python -m src.webapp
goto :eof
:error
echo Setup or launch failed. Confirm Python 3.10-3.12 is installed and review the error above.
pause
