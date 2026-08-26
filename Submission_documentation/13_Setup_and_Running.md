# 13 — Setup and Running the Application

## 1. Prerequisites

To run NetSage AI and verify the submission, the following software is required:
- **Python**: Version 3.9 or higher (Verified on 3.12.6)
- **Cisco Packet Tracer**: Any recent version (To open the `.pkt` lab file)
- **Internet Access**: Required only for the LLM fallback cases (NET-014 through NET-033)

---

## 2. Installation Instructions

1. **Clone or download the repository** to your local machine.
2. **Navigate to the project root directory**:
   ```bash
   cd ai_cisco
   ```
3. **Create a virtual environment** (Recommended to isolate dependencies):
   ```bash
   python -m venv venv
   ```
4. **Activate the virtual environment**:
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Windows (CMD):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
5. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Dependencies installed: `streamlit`, `pandas`, `anthropic`.

---

## 3. Configuration & API Keys

### Deterministic Cases (NET-001 to NET-013)
No API key is required. The deterministic regex engine runs entirely locally. You can demonstrate the primary NET-001 workflow completely offline.

### LLM Fallback Cases (NET-014 to NET-033)
To run these cases, you must provide an Anthropic API key to authenticate with Claude.

Set the environment variable:
- Windows (PowerShell):
  ```powershell
  $env:ANTHROPIC_API_KEY="sk-ant-api03-..."
  ```
- macOS/Linux:
  ```bash
  export ANTHROPIC_API_KEY="sk-ant-api03-..."
  ```

*(Do not modify `.env.example` directly or commit your API key to source control).*

---

## 4. Running the Dashboard

Launch the Streamlit web application:

```bash
streamlit run src/app.py
```

The application will start a local web server and automatically open your default browser to:
`http://localhost:8501`

---

## 5. Running the Test Suite

To verify the integrity of the application logic without starting the web UI, run the automated test suite.

Using pytest (recommended):
```bash
python -m pytest tests/ -v
```

Using standard unittest:
```bash
python -m unittest discover -s tests -v
```

Expect to see "7 passed" in less than a second. No API calls are made during the tests.
