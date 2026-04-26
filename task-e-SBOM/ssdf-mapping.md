# SSDF Mapping — Software Security Portfolio

## Overview

NIST SP 800-218 (the SSDF) breaks secure development down into named practices across four groups: Prepare the Organisation, Protect the Software, Produce Well-Secured Software, and Respond to Vulnerabilities. This document does two things. First, it maps each finding from the assessment to the SSDF practice it violates and explains what should have been done differently. Second, it demonstrates how the artifacts produced in this portfolio actively satisfy those same practices.

## Part 1: Violations Found in the My Shop Webapp

| SSDF Practice | Practice ID | Finding | Remediation |
| --- | --- | --- | --- |
| Use well-secured functions and avoid dangerous ones | PW.5.1 | `strcpy` used in Task A C program with no bounds check, which caused the buffer overflow directly | Replace with `snprintf` and add length validation before copying |
| Store and transmit data securely | PW.5.2 | Passwords stored as plain text in the SQLite database | Hash passwords with bcrypt before storing. Never store readable credentials |
| Use established authentication mechanisms | PW.5.3 | Authentication relies on a plain unsigned browser cookie containing the username | Replace with Flask's signed session, add HttpOnly and Secure cookie flags |
| Protect data at rest and in transit | PW.5.2 | No HTTPS enforced, so session cookies and credentials are sent in plain text over HTTP | Enforce HTTPS in production, set the Secure cookie flag |
| Validate all inputs | PW.6.1 | User input pasted directly into SQL queries via f-strings across multiple routes | Use parameterised queries with `?` placeholders throughout |
| Sanitise outputs | PW.6.2 | Product descriptions and review comments rendered into HTML without escaping | Enable Jinja2 autoescaping or apply `markupsafe.escape()` on all user-derived output |
| Design software to meet security requirements | PD.1.1 | No authorisation check on the role upgrade route, so any buyer becomes a seller instantly | Require admin approval for role changes at the design stage |
| Review the code for security | PW.7.1 | SQL injection and XSS were present across the whole codebase without any prior code review | Run SAST tooling (Semgrep, Bandit) and peer review on every pull request |
| Test software for security using static analysis | PW.8.1 | No static analysis was in place before this assessment | Add automated SAST in CI and run it on every push to main |
| Test software for security using dynamic analysis | PW.8.2 | No dynamic testing or penetration testing was carried out before this assessment | Run DAST tools such as OWASP ZAP against a staging environment before every release |
| Receive and manage vulnerability reports | RV.1.1 | No process exists for reporting or tracking vulnerabilities | Create a responsible disclosure policy and a process for triaging reported issues |
| Identify and confirm vulnerabilities | RV.1.2 | Vulnerabilities were only discovered during this assessment with no prior identification process in place | Run regular SAST and DAST scans, maintain a vulnerability register |
| Track and manage the remediation of vulnerabilities | RV.2.1 | No remediation tracking or patch process in place | Use a ticketing system to track each finding from discovery through to fix and verification |
| Analyse vulnerabilities to identify root causes | RV.3.1 | SQL injection across multiple routes shares the same root cause: f-string query construction | A root cause analysis would identify the pattern and fix every instance at once rather than one by one |

---

## Part 2: How This Portfolio Satisfies SSDF Practices

The artifacts produced across Tasks A through E are not just documentation of problems. Each one directly implements or demonstrates an SSDF practice. The table below maps each portfolio artifact to the practice it satisfies.

| SSDF Practice | Practice ID | Portfolio Artifact | How it satisfies the practice |
| --- | --- | --- | --- |
| Use well-secured functions and avoid dangerous ones | PW.5.1 | `task-a-vulnerability/vulnerable-code-fixed.c` | Replaces `strcpy` with `snprintf` and adds explicit length validation, directly addressing the unsafe function at the source level |
| Test software for security using static analysis | PW.8.1 | `.github/workflows/sast.yml`, `task-c-testing/triage.md` | The GitHub Actions pipeline runs Semgrep and Bandit automatically on every push to main. The triage log shows every finding was reviewed and categorised, satisfying the requirement to both run and act on static analysis results |
| Test software for security using dynamic analysis | PW.8.2 | `task-d-dynamictesting/exploits.md`, `task-d-dynamictesting/zap-report/` | OWASP ZAP was run against the live application and four additional vulnerabilities were exploited manually. The ZAP HTML report and exploit write-up together constitute the DAST evidence this practice requires |
| Review the code for security | PW.7.1 | `task-c-testing/webapp/app_fixed.py` | The fixed version of the application was produced by reviewing every finding from the Semgrep scan and rewriting the vulnerable patterns. This replicates what a security-focused code review produces |
| Archive and protect each software release | PS.3.1 | `task-e-SBOM/sbom/sbom.cdx.json` | The CycloneDX SBOM generated by Syft provides a point-in-time record of all software components and their versions, which is the artifact this practice requires to be produced and retained for each release |
| Keep all development tools and components up to date | PO.3.2 | Grype scan output in `task-e-SBOM/evidence/02-grype-scan.png` | Grype identified two vulnerabilities in pip 24.0 (GHSA-4xh5-x5gv-qwph and GHSA-6vgw-5pg2-w6jp). Scanning the SBOM against a CVE database is the mechanism SSDF PO.3.2 describes for keeping tooling patched |
| Identify and confirm vulnerabilities | RV.1.2 | `task-c-testing/triage.md`, `task-d-dynamictesting/exploits.md` | The triage log from Task C and the exploit write-up from Task D together form a vulnerability register: each finding is identified, confirmed, classified, and its impact is assessed |
| Analyse vulnerabilities to identify root causes | RV.3.1 | `task-c-testing/triage.md` | The triage log identifies that SQL injection across multiple routes shares a single root cause: f-string query construction. Fixing one pattern eliminates the whole class of vulnerability rather than patching routes one at a time |

---

## Supply Chain

The SBOM was generated using Syft (CycloneDX JSON format) against the webapp directory. Grype scanned the SBOM and identified two vulnerabilities in `pip` version 24.0:

| Package | Installed | Fixed In | Vulnerability | Severity |
| --- | --- | --- | --- | --- |
| pip | 24.0 | 25.3 | GHSA-4xh5-x5gv-qwph | Medium |
| pip | 24.0 | 26.0 | GHSA-6vgw-5pg2-w6jp | Low |

Both findings are in pip itself rather than in the webapp's own dependencies. Neither one affects the running application directly, but pip should be upgraded to 26.0 to clear both. This maps to SSDF PO.3.2, which requires development tools to be kept patched.

The SBOM file is at `sbom/sbom.cdx.json`. In a production setup, the SBOM would be generated on every build and run through Grype automatically as part of the CI pipeline, so any new CVE affecting a dependency is flagged immediately rather than discovered during a manual audit. This is the model described by SSDF PS.3.1 and PO.3.2 together.
