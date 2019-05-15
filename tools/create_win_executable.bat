pyinstaller ^
    --clean ^
    --onefile ^
    --noconsole ^
    --add-binary nch\newgrf.ico;nch ^
    --icon nch\newgrf.ico ^
    --name "NewGRF Cargo Helper" ^
    bin\run.py
