# Local comparison API

This API calls the existing System A, System B, and System C experiment functions. It does not rebuild the static index, change prompts or retrieval behavior, or return mock answers. A request runs only the systems named in its `systems` array.

## Setup and run (PowerShell)

From the repository root, using the project's Python 3.10 interpreter:

```powershell
C:\Users\shikh\AppData\Local\Programs\Python\Python310\python.exe -m pip install -r requirements.txt
$env:GEMINI_API_KEY = "your-key"
C:\Users\shikh\AppData\Local\Programs\Python\Python310\python.exe -m uvicorn webapp.app:app --host 127.0.0.1 --port 8000
```

Alternatively, keep the key in the project `.env`; the existing System A dotenv loader reads it without overriding process environment variables. Never commit `.env`.

Try the endpoints from a second PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
$body = @{ question = "What powers did the Governor have under Article 174?"; reference_date = "1951-02-01"; systems = @("A", "B", "C") } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/compare -ContentType "application/json" -Body $body
Invoke-RestMethod "http://127.0.0.1:8000/api/history?limit=20"
```

`/api/health` checks local prerequisites only; it does not call Gemini or download embedding weights. Compare failures and System C abstentions are returned explicitly. Comparison history is appended to `results/web_interface/comparison_history.jsonl`; the existing benchmark outputs are not used as history.

Run API tests without Gemini:

```powershell
C:\Users\shikh\AppData\Local\Programs\Python\Python310\python.exe -m unittest discover -s tests -p test_web_api.py -v
```
