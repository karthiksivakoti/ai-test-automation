# Create the file in the app directory
# Path: ai-test-automation/app/app.py

from flask import Flask, render_template, request, jsonify
import asyncio
import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiqatester.director import TestDirector
from aiqatester.utils.config import Config

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_test', methods=['POST'])
def run_test():
    url = request.form.get('url')
    task = request.form.get('task')
    headless = request.form.get('headless', 'true') == 'true'
    
    # Create config
    config = Config()
    config.headless = headless
    
    # Run test asynchronously
    results = asyncio.run(run_test_async(url, task, config))
    
    return jsonify(results)

async def run_test_async(url, task, config):
    director = TestDirector(config)
    try:
        results = await director.run(url, task)
        return results
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))