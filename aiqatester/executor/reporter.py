# ai-test-automation/aiqatester/executor/reporter.py
"""
Test Reporter module for AIQATester.

This module generates test reports from test results.
"""

from typing import Dict, List, Any
import datetime
import json
import os
import time

from loguru import logger

class TestReporter:
    """Generates test reports from test results."""
    
    def __init__(self, report_dir: str = "reports"):
        """
        Initialize the test reporter.
        
        Args:
            report_dir: Directory to save reports
        """
        self.report_dir = report_dir
        
        # Create report directory if it doesn't exist
        os.makedirs(report_dir, exist_ok=True)
        
        logger.info("TestReporter initialized")
        
    def generate_report(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a test report from test results.
        
        Args:
            test_results: Test results
            
        Returns:
            Test report
        """
        timestamp = datetime.datetime.now().isoformat()
        logger.info(f"Generating test report at {timestamp}")
        
        # Create summary
        summary = {
            "timestamp": timestamp,
            "total": test_results.get("total", 0),
            "passed": test_results.get("passed", 0),
            "failed": test_results.get("failed", 0),
            "skipped": test_results.get("skipped", 0),
            "error": test_results.get("error", 0),
            "duration": test_results.get("duration", 0)
        }
        
        # Format duration as human-readable
        if "duration" in summary:
            duration_seconds = summary["duration"]
            summary["duration_formatted"] = self._format_duration(duration_seconds)
        
        # Create details
        details = []
        for test_result in test_results.get("results", []):
            # Create test detail
            test_detail = {
                "name": test_result.get("name", "Unknown test"),
                "description": test_result.get("description", ""),
                "status": test_result.get("status", "unknown"),
                "duration": test_result.get("duration", 0),
                "duration_formatted": self._format_duration(test_result.get("duration", 0)),
                "steps_total": len(test_result.get("steps", [])),
                "steps_passed": sum(1 for step in test_result.get("steps", []) if step.get("status") == "passed"),
                "assertions_total": len(test_result.get("assertions", [])),
                "assertions_passed": sum(1 for assertion in test_result.get("assertions", []) if assertion.get("status") == "passed"),
                "screenshots": test_result.get("screenshots", [])
            }
            
            details.append(test_detail)
        
        # Create report
        report = {
            "summary": summary,
            "details": details
        }
        
        # Save report to file
        report_file = os.path.join(self.report_dir, f"report_{int(time.time())}.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test report saved to {report_file}")
        
        return report
    
    def generate_html_report(self, test_results: Dict[str, Any]) -> str:
        """
        Generate an HTML test report.
        
        Args:
            test_results: Test results
            
        Returns:
            Path to the HTML report
        """
        # First generate the JSON report
        report = self.generate_report(test_results)
        
        # Create HTML report
        html = self._generate_html(report)
        
        # Save HTML report to file
        report_file = os.path.join(self.report_dir, f"report_{int(time.time())}.html")
        with open(report_file, "w") as f:
            f.write(html)
        
        logger.info(f"HTML test report saved to {report_file}")
        
        return report_file
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in seconds as human-readable.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 1:
            return f"{int(seconds * 1000)}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            seconds = seconds % 60
            return f"{minutes}m {seconds:.2f}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            seconds = seconds % 60
            return f"{hours}h {minutes}m {seconds:.2f}s"
    
    def _generate_html(self, report: Dict[str, Any]) -> str:
        """
        Generate HTML report.
        
        Args:
            report: Report data
            
        Returns:
            HTML report
        """
        # Get summary and details
        summary = report.get("summary", {})
        details = report.get("details", [])
        
        # Calculate pass rate
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        pass_rate = (passed / total) * 100 if total > 0 else 0
        
        # Generate HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Test Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                h1, h2, h3 {{
                    color: #333;
                }}
                .summary {{
                    background-color: #f5f5f5;
                    padding: 20px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }}
                .summary-item {{
                    display: inline-block;
                    margin-right: 20px;
                    padding: 10px;
                    border-radius: 4px;
                    background-color: #fff;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .passed {{
                    color: #2ecc71;
                }}
                .failed {{
                    color: #e74c3c;
                }}
                .skipped {{
                    color: #f39c12;
                }}
                .error {{
                    color: #c0392b;
                }}
                .test-case {{
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .status-passed {{
                    border-left: 5px solid #2ecc71;
                }}
                .status-failed {{
                    border-left: 5px solid #e74c3c;
                }}
                .status-skipped {{
                    border-left: 5px solid #f39c12;
                }}
                .status-error {{
                    border-left: 5px solid #c0392b;
                }}
                .progress {{
                    height: 10px;
                    background-color: #f5f5f5;
                    border-radius: 5px;
                    overflow: hidden;
                }}
                .progress-bar {{
                    height: 100%;
                    background-color: #2ecc71;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                th, td {{
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f5f5f5;
                }}
                .screenshot {{
                    max-width: 300px;
                    cursor: pointer;
                }}
                .modal {{
                    display: none;
                    position: fixed;
                    z-index: 1;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    overflow: auto;
                    background-color: rgba(0,0,0,0.8);
                }}
                .modal-content {{
                    margin: auto;
                    display: block;
                    max-width: 80%;
                    max-height: 80%;
                }}
                .close {{
                    position: absolute;
                    top: 15px;
                    right: 35px;
                    color: #f1f1f1;
                    font-size: 40px;
                    font-weight: bold;
                    transition: 0.3s;
                    cursor: pointer;
                }}
            </style>
        </head>
        <body>
            <h1>Test Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Generated on: {summary.get('timestamp', 'Unknown')}</p>
                <div class="summary-item">
                    <strong>Total:</strong> {summary.get('total', 0)}
                </div>
                <div class="summary-item passed">
                    <strong>Passed:</strong> {summary.get('passed', 0)}
                </div>
                <div class="summary-item failed">
                    <strong>Failed:</strong> {summary.get('failed', 0)}
                </div>
                <div class="summary-item skipped">
                    <strong>Skipped:</strong> {summary.get('skipped', 0)}
                </div>
                <div class="summary-item error">
                    <strong>Error:</strong> {summary.get('error', 0)}
                </div>
                <div class="summary-item">
                    <strong>Duration:</strong> {summary.get('duration_formatted', '0s')}
                </div>
                <div class="progress">
                    <div class="progress-bar" style="width: {pass_rate}%;"></div>
                </div>
                <p>Pass Rate: {pass_rate:.2f}%</p>
            </div>
            
            <h2>Test Details</h2>
        """
        
        # Add test details
        for test in details:
            status = test.get('status', 'unknown')
            html += f"""
            <div class="test-case status-{status}">
                <h3>{test.get('name', 'Unknown test')}</h3>
                <p>{test.get('description', '')}</p>
                <p><strong>Status:</strong> <span class="{status}">{status.upper()}</span></p>
                <p><strong>Duration:</strong> {test.get('duration_formatted', '0s')}</p>
                <p><strong>Steps:</strong> {test.get('steps_passed', 0)}/{test.get('steps_total', 0)} passed</p>
                <p><strong>Assertions:</strong> {test.get('assertions_passed', 0)}/{test.get('assertions_total', 0)} passed</p>
            """
            
            # Add screenshots
            screenshots = test.get('screenshots', [])
            if screenshots:
                html += f"""
                <h4>Screenshots:</h4>
                <div class="screenshots">
                """
                
                for i, screenshot in enumerate(screenshots):
                    img_id = f"img_{int(time.time())}_{i}"
                    html += f"""
                    <img class="screenshot" src="{screenshot}" alt="Screenshot" id="{img_id}" onclick="showImage(this.id)">
                    """
                
                html += "</div>"
            
            html += "</div>"
        
        # Add image modal
        html += """
            <div id="imageModal" class="modal">
                <span class="close" onclick="closeModal()">&times;</span>
                <img class="modal-content" id="modalImage">
            </div>
            
            <script>
                function showImage(imgId) {
                    var modal = document.getElementById("imageModal");
                    var img = document.getElementById(imgId);
                    var modalImg = document.getElementById("modalImage");
                    modal.style.display = "block";
                    modalImg.src = img.src;
                }
                
                function closeModal() {
                    document.getElementById("imageModal").style.display = "none";
                }
            </script>
        </body>
        </html>
        """
        
        return html