# Create a new file: view_results.py
import os
import json
import argparse
import webbrowser
import http.server
import socketserver
import threading
from pathlib import Path
import time

def create_html_viewer(export_dir):
    """Create an HTML page to view the exported data."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Test Automation Results</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            pre { max-height: 500px; overflow: auto; }
            .tab-content { margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <h1>AI Test Automation Results</h1>
            
            <ul class="nav nav-tabs" id="resultTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="site-tab" data-bs-toggle="tab" data-bs-target="#site" 
                            type="button" role="tab" aria-controls="site" aria-selected="true">Site Model</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="strategy-tab" data-bs-toggle="tab" data-bs-target="#strategy" 
                            type="button" role="tab" aria-controls="strategy" aria-selected="false">Test Strategy</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="scripts-tab" data-bs-toggle="tab" data-bs-target="#scripts" 
                            type="button" role="tab" aria-controls="scripts" aria-selected="false">Test Scripts</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="results-tab" data-bs-toggle="tab" data-bs-target="#results" 
                            type="button" role="tab" aria-controls="results" aria-selected="false">Test Results</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="screenshots-tab" data-bs-toggle="tab" data-bs-target="#screenshots" 
                            type="button" role="tab" aria-controls="screenshots" aria-selected="false">Screenshots</button>
                </li>
            </ul>
            
            <div class="tab-content" id="resultTabsContent">
                <!-- Site Model Tab -->
                <div class="tab-pane fade show active" id="site" role="tabpanel" aria-labelledby="site-tab">
                    <h2>Site Model</h2>
                    <pre id="siteModelContent" class="bg-light p-3"></pre>
                </div>
                
                <!-- Test Strategy Tab -->
                <div class="tab-pane fade" id="strategy" role="tabpanel" aria-labelledby="strategy-tab">
                    <h2>Test Strategy</h2>
                    <pre id="testStrategyContent" class="bg-light p-3"></pre>
                </div>
                
                <!-- Test Scripts Tab -->
                <div class="tab-pane fade" id="scripts" role="tabpanel" aria-labelledby="scripts-tab">
                    <h2>Test Scripts</h2>
                    <pre id="testScriptsContent" class="bg-light p-3"></pre>
                </div>
                
                <!-- Test Results Tab -->
                <div class="tab-pane fade" id="results" role="tabpanel" aria-labelledby="results-tab">
                    <h2>Test Results</h2>
                    <pre id="testResultsContent" class="bg-light p-3"></pre>
                </div>
                
                <!-- Screenshots Tab -->
                <div class="tab-pane fade" id="screenshots" role="tabpanel" aria-labelledby="screenshots-tab">
                    <h2>Screenshots</h2>
                    <div id="screenshotsContent" class="row"></div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Load JSON data
            async function loadJsonFile(url, elementId) {
                try {
                    const response = await fetch(url);
                    if (!response.ok) {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    const data = await response.json();
                    document.getElementById(elementId).textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    console.error('Error loading data:', error);
                    document.getElementById(elementId).textContent = `Error loading data: ${error.message}`;
                }
            }
            
            // Load screenshots
            async function loadScreenshots() {
                try {
                    const response = await fetch('screenshots.json');
                    if (!response.ok) {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    const screenshots = await response.json();
                    const container = document.getElementById('screenshotsContent');
                    
                    screenshots.forEach(screenshot => {
                        const col = document.createElement('div');
                        col.className = 'col-md-4 mb-4';
                        
                        const card = document.createElement('div');
                        card.className = 'card';
                        
                        const img = document.createElement('img');
                        img.src = screenshot;
                        img.className = 'card-img-top';
                        img.alt = 'Screenshot';
                        
                        const cardBody = document.createElement('div');
                        cardBody.className = 'card-body';
                        
                        const cardTitle = document.createElement('h5');
                        cardTitle.className = 'card-title';
                        cardTitle.textContent = screenshot.split('/').pop();
                        
                        cardBody.appendChild(cardTitle);
                        card.appendChild(img);
                        card.appendChild(cardBody);
                        col.appendChild(card);
                        container.appendChild(col);
                    });
                } catch (error) {
                    console.error('Error loading screenshots:', error);
                    document.getElementById('screenshotsContent').innerHTML = `
                        <div class="alert alert-danger">Error loading screenshots: ${error.message}</div>
                    `;
                }
            }
            
            // Load data when page loads
            window.addEventListener('DOMContentLoaded', () => {
                loadJsonFile('site_model.json', 'siteModelContent');
                loadJsonFile('test_strategy.json', 'testStrategyContent');
                loadJsonFile('test_scripts.json', 'testScriptsContent');
                loadJsonFile('test_results.json', 'testResultsContent');
                loadScreenshots();
            });
        </script>
    </body>
    </html>
    """
    
    # Create viewer.html file
    with open(os.path.join(export_dir, "viewer.html"), "w") as f:
        f.write(html_content)
    
    # Create screenshots.json file
    screenshots_dir = os.path.join(os.getcwd(), "screenshots")
    if os.path.exists(screenshots_dir):
        screenshots = [f"/{os.path.relpath(os.path.join(screenshots_dir, f), export_dir)}" 
                      for f in os.listdir(screenshots_dir) if f.endswith(".png")]
        
        with open(os.path.join(export_dir, "screenshots.json"), "w") as f:
            json.dump(screenshots, f)

def start_server(directory, port=8000):
    """Start a simple HTTP server."""
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        httpd.serve_forever()

def main():
    parser = argparse.ArgumentParser(description="View AI Test Automation results")
    parser.add_argument("--run", help="Specific run ID (e.g., run_20250321_123456)")
    args = parser.parse_args()
    
    exports_dir = os.path.join(os.getcwd(), "exports")
    
    if not os.path.exists(exports_dir):
        print(f"Exports directory not found: {exports_dir}")
        return
    
    if args.run:
        run_dir = os.path.join(exports_dir, args.run)
        if not os.path.exists(run_dir):
            print(f"Run directory not found: {run_dir}")
            return
    else:
        # Find the latest run
        run_dirs = [d for d in os.listdir(exports_dir) if d.startswith("run_")]
        if not run_dirs:
            print("No test runs found in exports directory")
            return
        
        run_dir = os.path.join(exports_dir, max(run_dirs))
    
    # Create HTML viewer
    create_html_viewer(run_dir)
    
    # Open the viewer in browser
    webbrowser.open(f"http://localhost:8000/viewer.html")
    
    # Start server in a thread
    server_thread = threading.Thread(target=start_server, args=(run_dir,))
    server_thread.daemon = True
    server_thread.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopped")

if __name__ == "__main__":
    main()