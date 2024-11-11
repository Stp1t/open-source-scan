import requests
from flask import Flask, request, jsonify
import time
import asyncio
from main import get_github_repo_info
from threading import Thread

app = Flask(__name__)

@app.route('/<owner>/<repo_name>', methods=['GET'])
def check_repo(repo_name, owner):

    repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"

#    asyncio.run(send_metrics(repo_url))
    thread = Thread(target = send_metrics, args = (repo_url,))
    thread.start()

    return jsonify({
        'message': f"Received the Repo: {repo_url}. Processing started..."
    }), 200

def send_metrics(repoUrl):
    metrics = get_github_repo_info(repoUrl)
    frontend_url = 'http://localhost:5173/sse/all/write'
    requests.post(frontend_url, data=metrics, headers={"Content-Type": "application/json"})


if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
