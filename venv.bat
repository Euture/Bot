@Echo Off
If Not Exist virtualenv python -m venv virtualenv
.\virtualenv\Scripts\python  .\virtualenv\Scripts\pip.exe install --upgrade pip
.\virtualenv\Scripts\python .\virtualenv\Scripts\pip.exe install -r requirements.txt