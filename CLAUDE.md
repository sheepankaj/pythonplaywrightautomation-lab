# CLAUDE.md — Project Context for Claude Code

## What this project is

A Python Playwright test automation framework

- **UI**: [saucedemo.com](https://www.saucedemo.com) — login flows
- **API**: [petstore.swagger.io/v2](https://petstore.swagger.io/v2) — Pet CRUD lifecycle

## Active Python environment

The project uses the **`.venv`** virtual environment at `.venv/Scripts/python.exe` (Windows) / `.venv/bin/python` (Mac/Linux). Always install packages into the venv:

```bash
# Activate (optional — VS Code picks it up automatically)
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install / sync dependencies
pip install -r requirements.txt
playwright install
```

VS Code is configured via `.vscode/settings.json` to use `.venv` automatically — no manual activation needed when running from the IDE.

## Key commands

```bash
pytest                              # run all tests (UI + API)
pytest tests/ui/ --headed           # UI tests in headed browser
pytest tests/api/                   # API tests only
pytest -m login_and_product_page    # by marker
python scripts/show_report.py       # open pytest-html report at localhost:9323
python scripts/show_allure_report.py # open Allure report (auto-opens browser)

# Code quality (run before committing)
ruff check .                        # lint
ruff check . --fix                  # lint + auto-fix
ruff format .                       # format (like Prettier)
pre-commit run --all-files          # run all pre-commit hooks manually
```

## Project structure

```
framework/
  api/petstore_client.py       # PetStoreClient — 4 methods, each @step decorated
  pages/saucedemo_login_page.py # SaucedemoLoginPage POM
  support/base_ui_test.py      # BaseUITest — autouse fixture injects self.page + self.login_page (with yield)
  support/base_api_test.py     # BaseAPITest — autouse fixture injects self.client (PetStoreClient) (with yield)
  testdata/pet_payload.py      # pet_id (epoch int) + new_pet_payload dict
  utils/step_decorator.py      # step class — @step decorator + context manager
  utils/api_helper.py          # attach_api_response() — logs + allure.attach JSON
  utils/auth_helper.py         # get_api_auth_headers()

tests/
  ui/test_saucedemo.py         # TestSaucedemoLoginAndShopping(BaseUITest)
  api/test_petstore.py         # TestPetstoreApiCrudLifecycle(BaseAPITest)

conftest.py                    # pytest hooks + base_url fixture + step table injection
pytest.ini                     # testpaths, addopts (html + allure + playwright options)
scripts/show_report.py         # HTTP server for pytest-html (port 9323)
scripts/show_allure_report.py  # allure serve wrapper with JAVA_HOME auto-detection
```

## Framework patterns

### OOP base classes instead of fixture parameters
Tests inherit from `BaseUITest` or `BaseAPITest`. The `@pytest.fixture(autouse=True)` inside each base class injects `self.page`, `self.login_page`, or `self.client`. Test methods take no fixture parameters.

### step decorator — dual reporting
`framework/utils/step_decorator.py` exports a `step` class that:
- Tracks steps in a thread-local registry → injected as an HTML table into pytest-html via `pytest_runtest_makereport` in conftest.py
- Simultaneously calls `allure.step()` → shows as expandable steps in Allure

Usage:
```python
@step("Method title")  # on page object / API client methods
def my_method(self): ...


with step("Assertion title"):  # inside test methods
    assert something
```

### Reporting stack
| Report | Generated to | View with |
|---|---|---|
| pytest-html | `reports/report.html` + `reports/assets/` | `python scripts/show_report.py` |
| Allure | `reports/allure-results/` | `python scripts/show_allure_report.py` |
| Playwright traces | `test-results/` (on failure) | `playwright show-trace <file>` |

Both reports generate on every `pytest` run via `pytest.ini` addopts.

### Allure decorators on tests
```python
@allure.feature("Authentication")   # sidebar grouping
@allure.story("Standard user login") # sub-group
@allure.title("Human readable title")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("Smoke", "Login")
```

### Environment variables
Loaded from `.env` via `python-dotenv` in `conftest.py`. Required keys:
```
STANDARD_USERNAME, PASSWORD, LOCKED_OUT_USER, PETSTORE_API_KEY
```

## Code quality

| Tool | Role | TypeScript equivalent |
|---|---|---|
| `ruff check` | Linter | ESLint |
| `ruff format` | Formatter | Prettier |
| `pre-commit` | Git hook runner | Husky |

Config files: `ruff.toml` (line length 100, E/W/F/I/UP rules), `.pre-commit-config.yaml`.

After cloning, run `pre-commit install` once to activate the git hook. The hook blocks commits if there are unfixable lint errors.

## Dependencies (venv)

```
pytest, pytest-playwright, pytest-html, allure-pytest, python-dotenv, ruff, pre-commit
```

External tools (not in pip):
- **Allure CLI**: installed via `npm install -g allure-commandline` (requires Node.js)
- **Java 17+**: required by Allure CLI — install via `winget install --id Microsoft.OpenJDK.17` (Windows) or `brew install --cask temurin` (Mac)
- `show_allure_report.py` auto-detects `JAVA_HOME` from common install locations — no manual setup needed

## pytest.ini summary

```ini
testpaths = tests
addopts = -v --html=reports/report.html --screenshot=only-on-failure
          --tracing=retain-on-failure --video=retain-on-failure
          --alluredir=reports/allure-results
markers = login_and_product_page, negative_test, incremental
```

`base_url = https://www.saucedemo.com` is set as a session-scoped fixture in `conftest.py` (not in pytest.ini) to avoid a pytest 9.x session-scoped fixture warning.

## conftest.py responsibilities

1. `load_dotenv()` — loads `.env`
2. `pytest_configure()` — creates `reports/` directory
3. `pytest_sessionfinish()` — writes `reports/allure-results/environment.properties`
4. `pytest_html_report_title()` — sets report title to "Playwright Automation Test Report"
5. `_reset_steps` autouse fixture — clears thread-local step registry before each test
6. `pytest_runtest_makereport` hook — injects steps HTML table into pytest-html extras
7. `base_url` session fixture — returns `"https://www.saucedemo.com"`

## VS Code configuration

- `launch.json`: 6 run configurations (headless, headed, UI only, API only, current file, show report)
- `settings.json`: `"python-envs.defaultEnvManager": "ms-python.python:system"` — uses system Python

## CI/CD

`.github/workflows/playwright.yml`:
- 3 sharded test jobs (matrix: [1,2,3])
- `allure-report` job merges shard results via `npm install -g allure-commandline` + `allure generate`
- `docker-publish` job builds multi-arch image to GHCR on merge to main/master

## Docker (future)

`Dockerfile` uses `mcr.microsoft.com/playwright/python:v1.49.0-jammy`. Not currently used for local runs.

## What NOT to do

- Do not reinstall packages into `.venv` — the project runs on system Python
- Do not add `filterwarnings = ignore::pytest.PytestRemovedIn10Warning` to pytest.ini — that class does not exist in pytest 9.2; the underlying warning was fixed by moving `base_url` to conftest.py
- Do not use `--self-contained-html` with pytest-html 4.x — that flag was removed
- Do not open `reports/allure-report/index.html` directly in Chrome — use `allure serve` or `python scripts/show_allure_report.py` to avoid CORS errors
