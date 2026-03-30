@echo off
REM ZOYA - Background Voice Assistant Launcher
REM This runs Zoya without opening VS Code or any terminal window

echo Starting Zoya Voice Assistant in background...

REM Run Python script in background without window
start /B pythonw zoya_autostart.py

echo Zoya is now running in the background!
echo Say "Hey Zoya" to activate!
echo.
echo To stop Zoya, open Task Manager and end "pythonw.exe"
echo.

timeout /t 3 /nobreak > nul
exit
