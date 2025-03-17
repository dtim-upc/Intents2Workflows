@echo off
start cmd /k "cd /d %~dp0backend/api && uvicorn main:app --port=8080"
start cmd /k "cd /d %~dp0backend/modules/IntentSpecification2WorkflowGenerator && flask --app api\api_main.py run --port=8000"
start cmd /k "cd /d %~dp0backend/modules/IntentAnticipation && python .\start_apis.py"
start cmd /k "cd /d %~dp0frontend && quasar dev"



