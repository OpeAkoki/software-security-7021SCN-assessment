# Task C — Automated Security Testing

## What this task covers

This task sets up a continuous integration pipeline that runs static analysis against the My Shop webapp automatically on every push to the main branch. The goal is to show that SAST tooling can catch real vulnerabilities before code ever reaches production, and to document which findings are genuine, which are acceptable risks, and which the tool got wrong.

## Tools used

**Semgrep** was chosen as the primary scanner because it supports rule packs built around the OWASP Top 10 and has specific packs for Flask and Python. It runs in CI via GitHub Actions and produces structured JSON output. A custom rule was also written to detect plain-text password storage, which is a gap in the standard rule packs.

**Bandit** was added as a secondary scanner. It is a well-known Python-specific tool that flags common insecure patterns. Running two tools side by side gives broader coverage.

## How the pipeline works

The workflow file is at `.github/workflows/sast.yml`. It triggers on every push and pull request to main. It runs in two passes:

1. **Vulnerable scan** — Semgrep and Bandit are run against the original `app.py`. The error gate is off here so the pipeline does not fail. The output is saved as an artefact (`semgrep-vulnerable.json`, `bandit-vulnerable.json`). This is the scan that produced the 46 findings documented in `triage.md`.

2. **Fixed scan** — Both tools are run against `app_fixed.py`, which is the same application rewritten with parameterised queries, Flask sessions, and `html.escape()` on all output. Both steps use `|| true` so the pipeline completes regardless of findings, allowing the JSON artefacts for both scans to be uploaded and compared. This is a deliberate design choice: Semgrep's pattern-based rules fire on certain HTML construction patterns even in the fixed version because they do not perform full taint analysis. The meaningful comparison is between the two JSON artefacts — the vulnerable scan returns 46 findings, the fixed scan returns significantly fewer — rather than a binary pass or fail gate.

## Custom rule

`custom-rules.yaml` contains a Semgrep rule that detects plain-text password storage. The rule looks for string assignments where the variable name contains "password" and the value is a string literal. This catches the hardcoded password in `init_db.py` that the built-in packs missed.

## Triage log

`triage.md` documents every category of finding from the vulnerable scan. It is split into three sections:

- **True positives** — confirmed vulnerabilities, including SQL injection across multiple routes and stored XSS in product descriptions
- **Accepted risk** — the hardcoded seed password in `init_db.py`, acknowledged as a demo-only limitation
- **False positives** — the generic secrets rule that fired on the variable name `secret_key` rather than real credential material

The triage log also explains what Semgrep cannot detect: the plain cookie used as identity, which is the most dangerous vulnerability in the application. This is why Task D (dynamic testing) is needed.

## Evidence

| File | What it shows |
|---|---|
| `evidence/semgrep.json` | Full Semgrep output from the first scan — 46 findings, all blocking |
| `evidence/01-semgrep-failing.png` | GitHub Actions run showing the first scan with findings |
| `evidence/02-semgrep-passing.png` | GitHub Actions run showing the fixed scan passing |
| `evidence/03-semgrep-passing-expanded.png` | Expanded view of the passing run showing individual step results |

## Files in this folder

| File | Purpose |
|---|---|
| `webapp/app.py` | Original vulnerable application — scanned for documentation |
| `webapp/app_fixed.py` | Remediated version with parameterised queries and session auth |
| `custom-rules.yaml` | Custom Semgrep rule for plain-text password detection |
| `triage.md` | Full triage log for all scan findings |
