# Application Agent — Ready Package

This package contains the complete Application Agent integration files.

Replace/add these files in the existing `job-match-agent` project:

- `app.py`
- `ui/application_agent.py`
- `services/application_browser.py`
- `services/application_answer_service.py`
- `services/application_review_launcher.py`
- `services/application_browser_runner.py`
- `tests/test_application_browser.py`

Dependency:

```bash
python -m pip install -r requirements_application_agent.txt
python -m playwright install chromium
```

For the main project `requirements.txt`, also add:

```text
playwright==1.62.0
```

The Application Agent now supports:

- public job-page inspection
- login redirect detection
- form-field detection
- English/German field classification
- applicant profile mapping
- resume upload
- manual field mapping overrides
- custom application answers
- local Ollama answer suggestions
- safe headless auto-fill preview
- screenshot/action report
- separate headed review browser
- manual final submission
- duplicate-aware save to the existing application tracker
- no automatic Submit/Apply/Continue clicks
- no password entry or authentication bypass
- no automatic consent checkbox/radio selection

Run the existing app normally:

```bash
streamlit run app.py --server.port 8502
```

Run tests:

```bash
python -m pytest tests/test_application_browser.py -q
```
