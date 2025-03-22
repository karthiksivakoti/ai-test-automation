# AIQATester: AI-Powered Automated Testing Framework 🤖

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=Python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-%232EAD33.svg?style=for-the-badge&logo=Playwright&logoColor=white)](https://playwright.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-%23412991.svg?style=for-the-badge&logo=OpenAI&logoColor=white)](https://openai.com/)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude-%236B3FA0.svg?style=for-the-badge)](https://www.anthropic.com/)
[![Flask](https://img.shields.io/badge/Flask-%23000000.svg?style=for-the-badge&logo=Flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-%232496ED.svg?style=for-the-badge&logo=Docker&logoColor=white)](https://www.docker.com/)

An intelligent web testing framework that uses AI to understand websites, generate test cases, and automate UI testing. Built with LLMs, Playwright, and Python to provide zero-configuration automated testing.

## 🌟 Features

- **AI-Powered Website Analysis**: Automatically scans and understands website structure
- **Intelligent Test Case Generation**: Creates relevant test cases based on site functionality
- **Automated Test Script Creation**: Converts test cases into executable browser automation
- **Self-Healing Tests**: Dynamically adapts to UI changes
- **Comprehensive Test Reporting**: Detailed insights on test execution and failures
- **LLM Integration**: Uses GPT-4 or Claude for intelligent decision making
- **Zero Configuration**: Works out of the box with minimal setup

## 🛠️ Technology Stack

<table>
<tr>
<td width="50%" valign="top">

### Backend & AI
- **Core:**
  - Python 3.10+
  - asyncio
  - Loguru
  
- **Browser Automation:**
  - Playwright
  - CSS/XPath Selectors
  - Screenshot Capture
  
- **AI & LLM:**
  - OpenAI API (GPT-4)
  - Anthropic API (Claude)
  - Prompt Engineering
  - BeautifulSoup4
  
- **Data Management:**
  - YAML Configuration
  - JSON Reporting
  - HTML Parsing
  - SQLite (optional)

</td>
<td width="50%" valign="top">

### Frontend & DevOps
- **Web Interface:**
  - Flask
  - Bootstrap
  - JavaScript
  - WebSockets

- **Deployment:**
  - Docker
  - Docker Compose
  - Google Cloud Run
  - Environment Variables
  
- **Development:**
  - Poetry (dependency management)
  - pytest
  - Black (formatting)
  - Virtual Environments

</td>
</tr>
</table>

## 🎯 Key Components

### Website Analysis
- **Site Analyzer**: Crawls websites to map structure and interactive elements
- **Element Finder**: Identifies and classifies UI components
- **Business Analyzer**: Detects key business flows and user journeys

### Test Strategy
- **Test Strategy Planner**: Creates a comprehensive testing strategy
- **Test Case Prioritizer**: Ranks test cases by importance and impact
- **Coverage Analyzer**: Identifies gaps in test coverage

### Test Generation
- **Script Generator**: Creates executable test scripts from test cases
- **Assertion Builder**: Adds verification points to test scripts
- **Data Requirements**: Identifies and provides test data

### Test Execution
- **Test Runner**: Executes tests in browser environment
- **Screenshot Manager**: Captures visual evidence at key points
- **Reporter**: Generates detailed test reports and insights

## 📊 System Architecture

```plaintext
┌─────────────────┐    ┌──────────────┐    ┌───────────────┐
│  Website        │────│  Analyzer    │────│  Business     │
│  URL Input      │    │  Engine      │    │  Flow Detector│
└─────────────────┘    └──────────────┘    └───────┬───────┘
                                                   │
                                                   ▼
┌─────────────────┐     ┌──────────────┐     ┌───────────────┐
│  Test Execution │◄────│  Test Script │◄────│  Strategy     │
│  Engine         │     │  Generator   │     │  Planner      │
└───────┬─────────┘     └──────────────┘     └───────────────┘
        │
        ▼
┌─────────────────┐     ┌──────────────┐     
│  Report         │────►│  Feedback    │     
│  Generator      │     │  Analyzer    │
└─────────────────┘     └──────────────┘
```

## 💾 Data Structure
### Test Strategy
```code
{
  "objectives": ["Verify core functionality", "Identify critical issues"],
  "key_areas": ["Business flows", "User interfaces"],
  "approach": "Manual and automated testing",
  "test_cases": [
    {
      "name": "Login Functionality Test",
      "description": "Test login with valid and invalid credentials",
      "priority": 5
    },
    # More test cases...
  ]
}
```
### Test Script
```code
{
  "name": "Login Functionality Test",
  "description": "Verify that users can log in with valid credentials",
  "steps": [
    {"step": 1, "action": "navigate", "selector": null, "value": "https://example.com", "wait_for": null},
    {"step": 2, "action": "click", "selector": "#login-button", "value": null, "wait_for": "#login-form"},
    {"step": 3, "action": "type", "selector": "#username", "value": "testuser", "wait_for": null},
    {"step": 4, "action": "type", "selector": "#password", "value": "password123", "wait_for": null},
    {"step": 5, "action": "click", "selector": "#submit", "value": null, "wait_for": ".dashboard"}
  ]
}
```

## 🔧 Configuration
Key configuration parameters in .env:
```code
# API Keys
OPENAI_API_KEY="your-openai-key"
ANTHROPIC_API_KEY="your-anthropic-key"

# Browser Settings
HEADLESS=true
BROWSER_TYPE=chromium
SLOW_MO=50
VIEWPORT_WIDTH=1280
VIEWPORT_HEIGHT=720
TIMEOUT=30000

# LLM Settings
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o
ANTHROPIC_MODEL=claude-3-opus-20240229

# Testing Settings
MAX_DEPTH=3
MAX_TEST_CASES=10
MAX_PAGES=20
```

## 🚀 Getting Started
### Clone the Repository
```code
git clone https://github.com/yourusername/ai-test-automation.git
cd ai-test-automation
```

### Install dependencies
```code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

### Set your API keys
### Run a test
```code
python main.py https://pikepass.com --task "Test login functionality"
```

## 📊 Understanding Results
All test results are saved in the following locations:

- ./exports/ - Detailed JSON data about site analysis, test strategy, and scripts
- ./reports/ - Test execution reports and metrics
- ./screenshots/ - Visual evidence captured during test execution

## 🙏 Acknowledgements
- OpenAI and Anthropic for their powerful language models
- Playwright team for the browser automation framework
- All open-source projects that made this tool possible

Made with 🧠 by Karthik Sivakoti
