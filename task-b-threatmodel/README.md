# Task B — Threat Modelling and SDLC Mapping

## What this task covers

This task analyses the My Shop webapp using the STRIDE threat modelling methodology and maps each threat category to the appropriate stage of the software development lifecycle.

## Threat Model

The full STRIDE analysis is in `threat-model.md`. It covers all six threat categories — Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege — with specific references to the vulnerable code in `app.py` and a proposed fix for each.

## Data Flow Diagram

The DFD was created using OWASP Threat Dragon and shows the data flows between the browser, the Flask application, and the SQLite database, with trust boundaries marked. The diagram is saved as `dfd.png` and the Threat Dragon project file is `threat-model.json`.

## Files

| File | Purpose |
|---|---|
| `threat-model.md` | Full STRIDE analysis and SDLC mapping |
| `dfd.png` | Data Flow Diagram from OWASP Threat Dragon |
| `threat-model.json` | Threat Dragon project export |
