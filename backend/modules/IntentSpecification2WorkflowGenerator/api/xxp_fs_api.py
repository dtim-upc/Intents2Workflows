import base64

import requests
import json
from pathlib import Path
from requests.auth import HTTPBasicAuth


BASE_DIR = Path(__file__).resolve().parent
cred_path = BASE_DIR / "FS_credentials.json"

with cred_path.open() as f:
    creds = json.load(f)

USERNAME = creds["username"]
PASSWORD = creds["password"]


class FileSystemClient:

    def __init__(self, base_url, user):
        self.base_url = base_url
        self.username = USERNAME
        self.password = PASSWORD
        self.user = user

    def add_file(self, path:str, filename:str, file_contents:str):

        try:

            # Combine username:password and Base64 encode
            credentials = f"{self.username}:{self.password}"
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

            headers = {
                "Authorization": f"Basic {encoded_credentials}"
            }

            response = requests.post(f"{self.base_url}/create/{self.user}/{path}/{filename}", data=file_contents, headers=headers, timeout=60)  # <- prevents dropping Authorization
            
            print(response.status_code)
            print(response.headers)
            print(response.request.headers)
            print(response.request.url)

            # Check the response
            if response.status_code == 201:
                print("Success!")

            else:
                print(f"Request file system failed with status code {response.status_code}")
                print(response.text) 

        except Exception as e:
            print("File system connection error:", e)

        
        return response

    def add_experiment(self, filename:str, file_contents:str):
        response = self.add_file("experiments", filename, file_contents)
        return response.status_code
    
    def add_workflow(self, filename:str, file_contents:str):
        response = self.add_file("workflows", filename, file_contents)
        return response.status_code
    
    def add_task(self, task_name:str, dsl_content:str, python_content:str, requirements_content:str):
        responses_status= set()
        print("adding task.xxp")
        response = self.add_file(f"tasks/{task_name}", "task.xxp", dsl_content)
        responses_status.add(response.status_code)
        print("adding task.py")
        response = self.add_file(f"tasks/{task_name}", "task.py", python_content)
        responses_status.add(response.status_code)
        print("adding requirements.txt")
        response = self.add_file(f"tasks/{task_name}", "requirements.txt", requirements_content)
        responses_status.add(response.status_code)

        if len(responses_status) == 1:
            return responses_status.pop()
        else:
            print("Multiple problems",responses_status)
            return 500

