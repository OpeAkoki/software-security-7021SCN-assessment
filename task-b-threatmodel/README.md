# Task B — Threat Modelling and SDLC Mapping

## What this task covers

This task applies the STRIDE threat modelling methodology to the NovaTrust Bank Mobile Application and maps each threat category to the appropriate stage of the software development lifecycle.

## Threat Model

The full STRIDE analysis is in `threat-model.md`. It covers all six threat categories (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege) with a specific threat scenario, the affected data flow from the DFD, and a proposed fix for each.

## Data Flow Diagram

The DFD was created using OWASP Threat Dragon and models the NovaTrust Bank Mobile Application across three trust boundary zones: the Internet Zone (external actors), the Application DMZ (five backend services), and the Internal Network Zone (four databases). The diagram is saved as `dfd.png` and the Threat Dragon project file is `novatrust-bank-threat-model.json`.

## Files

| File | Purpose |
| --- | --- |
| `threat-model.md` | Full STRIDE analysis and SDLC mapping |
| `dfd.png` | Data Flow Diagram from OWASP Threat Dragon |
| `novatrust-bank-threat-model.json` | Threat Dragon project export |
