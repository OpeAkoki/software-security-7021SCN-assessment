# Task D — Dynamic Analysis and Exploit Development

## What this task covers

This task demonstrates hands-on exploitation of the My Shop vulnerable webapp. A fresh, unmodified copy of the original source code was used — not the version from Task C. This ensures the results reflect the application in its vulnerable state without any changes from the static analysis phase.

Four vulnerabilities were exploited manually and documented with screenshots. OWASP ZAP was then run as an automated scanner to confirm findings and identify additional issues.

## Vulnerabilities exploited

| # | Vulnerability | CVSS |
|---|---|---|
| 1 | Cookie forgery — gain admin access by setting a browser cookie | 9.8 Critical |
| 2 | SQL injection — bypass login with `admin' --` | 9.8 Critical |
| 3 | Stored XSS — inject a script via product description | 8.2 High |
| 4 | Privilege escalation — any buyer can become a seller instantly | 7.1 High |

Full details, payloads used, and screenshots are in `exploits.md`.

## ZAP scan

OWASP ZAP was run against the live application and returned 10 alerts including SQL injection, missing CSRF tokens, and absent security headers. The full HTML report is in `zap-report/`.

## Evidence

| File | What it shows |
|---|---|
| `evidence/01-cookie-forgery.png` | Admin access gained by setting cookie in DevTools |
| `evidence/02-sqli-login-form.png` | SQL injection payload entered in login form |
| `evidence/03-sqli-login-success.png` | Logged in as admin with wrong password |
| `evidence/04-stored-xss.png` | Alert box firing from stored XSS payload |
| `evidence/05-privilege-escalation-form.png` | Become a Seller page |
| `evidence/06-privilege-escalation-success.png` | Add a Product link visible after role upgrade |
| `evidence/07-zap-scan-results.png` | ZAP alerts panel showing 10 findings |

## Files

| File | Purpose |
|---|---|
| `exploits.md` | Full exploit write-up with steps, payloads, and CVSS scores |
| `zap-report/` | OWASP ZAP HTML report |
| `evidence/` | Screenshots for every exploit |
| `webapp/` | Original unmodified vulnerable application used for testing |
