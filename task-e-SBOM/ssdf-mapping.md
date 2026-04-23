# SSDF Mapping — My Shop Webapp

## Overview

NIST SP 800-218 (the SSDF) breaks secure development down into named practices across four groups: Prepare the Organisation, Protect the Software, Produce Well-Secured Software, and Respond to Vulnerabilities. The table below takes each finding from this assessment and maps it to the practice it violates, along with what should have been done differently.

## Mapping Table

| SSDF Practice | Practice ID | Finding in My Shop | Remediation |
|---|---|---|---|
| Use well-secured functions and avoid dangerous ones | PW.5.1 | `strcpy` used in Task A C program with no bounds check, which caused the buffer overflow directly | Replace with `snprintf` and add length validation before copying |
| Store and transmit data securely | PW.5.2 | Passwords stored as plain text in the SQLite database | Hash passwords with bcrypt before storing. Never store readable credentials |
| Use established authentication mechanisms | PW.5.3 | Authentication relies on a plain unsigned browser cookie containing the username | Replace with Flask's signed session, add HttpOnly and Secure cookie flags |
| Protect data at rest and in transit | PW.5.2 | No HTTPS enforced, so session cookies and credentials are sent in plain text over HTTP | Enforce HTTPS in production, set the Secure cookie flag |
| Validate all inputs | PW.6.1 | User input pasted directly into SQL queries via f-strings across multiple routes | Use parameterised queries with `?` placeholders throughout |
| Sanitise outputs | PW.6.2 | Product descriptions and review comments rendered into HTML without escaping | Enable Jinja2 autoescaping or apply `markupsafe.escape()` on all user-derived output |
| Design software to meet security requirements | PD.1.1 | No authorisation check on the role upgrade route, so any buyer becomes a seller instantly | Require admin approval for role changes at the design stage |
| Review the code for security | PW.7.1 | SQL injection and XSS were present across the whole codebase. A code review would have caught these | Run SAST tooling (Semgrep, Bandit) and peer review on every pull request |
| Test software for security | PW.8.1 | No testing of any kind was in place before this assessment | Add automated SAST in CI (implemented in Task C) and run DAST against staging before release |
| Receive and manage vulnerability reports | RV.1.1 | No process exists for reporting or tracking vulnerabilities | Create a responsible disclosure policy and a process for triaging reported issues |
| Identify and confirm vulnerabilities | RV.1.2 | Vulnerabilities were only discovered during this assessment with no prior identification process in place | Run regular SAST and DAST scans, maintain a vulnerability register |
| Track and manage the remediation of vulnerabilities | RV.2.1 | No remediation tracking or patch process in place | Use a ticketing system to track each finding from discovery through to fix and verification |
| Analyse vulnerabilities to identify root causes | RV.3.1 | SQL injection across multiple routes shares the same root cause: f-string query construction | A root cause analysis would identify the pattern and fix every instance at once rather than one by one |

## Supply Chain

The SBOM generated using Syft (CycloneDX JSON format) lists all Python packages present in the webapp environment. Grype scanned the SBOM and identified two vulnerabilities in `pip` version 24.0:

| Package | Installed | Fixed In | Vulnerability | Severity |
|---|---|---|---|---|
| pip | 24.0 | 25.3 | GHSA-4xh5-x5gv-qwph | Medium |
| pip | 24.0 | 26.0 | GHSA-6vgw-5pg2-w6jp | Low |

Both findings are in pip itself rather than in the webapp's own dependencies. Neither one affects the running application directly, but pip should be upgraded to 26.0 to clear them. This maps to SSDF PO.3.2, which is about keeping development tools patched.

The SBOM file is at `sbom/sbom.cdx.json`. In a real production setup you would generate one on every build and run it through Grype automatically, so any new CVE that affects your dependencies gets flagged immediately rather than discovered during a manual audit.
