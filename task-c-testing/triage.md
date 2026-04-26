# Task C — SAST Triage Log

## Overview

Semgrep was run against the webapp source code using the OWASP Top 10, Python, Flask, 
and Secrets rule packs. The scan ran 212 rules across 19 files and returned 46 findings, 
all of which were blocking. This log documents how each category of finding was triaged.

## True Positives — Real Vulnerabilities

These findings are genuine security issues confirmed by reading the source code.

| Finding | Rule ID | File | Line | Action |
|---|---|---|---|---|
| SQL injection via f-string query | python.flask.security.injection.tainted-sql-string | app.py | 140 | Confirmed — login auth bypass possible with `admin' --` |
| SQL injection via f-string query | python.flask.security.injection.tainted-sql-string | app.py | 98 | Confirmed — register route inserts unsanitised input |
| SQL injection via f-string query | python.flask.security.injection.tainted-sql-string | app.py | 192 | Confirmed — become_seller route |
| SQL injection via f-string query | python.flask.security.injection.tainted-sql-string | app.py | 221, 233 | Confirmed — add product route |
| SQL injection via f-string query | python.flask.security.injection.tainted-sql-string | app.py | 270, 283, 291 | Confirmed — edit product route |
| SQL injection via f-string query | python.flask.security.injection.tainted-sql-string | app.py | 328, 336 | Confirmed — delete route |
| SQL injection via cursor execute | python.django.security.injection.sql.sql-injection-db-cursor-execute | app.py | multiple | Confirmed — raw SQL via cursor without parameterisation |
| XSS via raw HTML rendering | python.flask.security.injection.raw-html-concat.raw-html-format | app.py | 299-317 | Confirmed — product descriptions rendered without escaping |
| XSS via raw HTML format | python.django.security.injection.raw-html-format.raw-html-format | app.py | multiple | Confirmed — user input concatenated directly into HTML |
| Debug mode enabled | python.flask.security.audit.debug-enabled.debug-enabled | app.py | 465 | Confirmed — exposes server internals if deployed |
| Format string returned to user | python.flask.security.audit.directly-returned-format-string | app.py | multiple | Confirmed — user-controlled data returned directly |

## Accepted Risk — Known but Not Fixed in This Scope

These are real findings that have been acknowledged but not remediated within this 
demonstration scope.

| Finding | Rule ID | File | Line | Justification |
|---|---|---|---|---|
| Hardcoded admin password in seed data | python.lang.security.audit.hardcoded-password-string | init_db.py | 14 | Demo application only. In production this would be removed and passwords hashed with bcrypt. Risk accepted for assessment scope. |

## False Positives — Suppressed

These findings were raised by Semgrep but are not genuine security issues in this context.

| Finding | Rule ID | File | Line | Why False |
|---|---|---|---|---|
| Generic secret detected | generic.secrets.security.detected-generic-api-key | app.py | 11 | Rule fired on the word "secret" in the variable name `secret_key`. No actual credential material is present beyond a demo string. The fix is the same — move to environment variable — but this is not a credential leak. |

## Tool Limitations

Semgrep's pattern matching successfully identified every f-string SQL injection in the file 
and flagged XSS and debug mode correctly. However, it could not detect the most dangerous 
vulnerability in this application — the plain cookie used as identity at app.py lines 15 and 
146. An attacker can set `Cookie: username=admin` in their browser and gain full administrator 
access with no password. This flaw has no pattern that Semgrep can match because it is a 
trust model violation rather than a syntax error. This is why dynamic testing in Task D is 
necessary — some vulnerabilities only reveal themselves when the application is actually running.
