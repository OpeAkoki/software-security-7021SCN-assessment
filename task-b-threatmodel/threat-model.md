# Task B — Threat Modelling and SDLC Mapping

## Data Flow Diagram

See `dfd.png` for the Data Flow Diagram created using OWASP Threat Dragon.

## System Description

 My Shop is a small e-commerce web application built with Flask and a SQLite database. It has three user roles (buyer, seller, and administrator) and supports product listings, reviews, and buyers can elevate their role to seller without any authorisation or approval. Authentication is handled by a plain browser cookie that carries the logged-in username between requests, with no signing or encryption applied to it. The admin panel allows user management and removal of a product from listing.

## STRIDE Threat Analysis

### Spoofing

The app identifies users by reading a plain browser cookie that contains just their username. There is no signature or verification on this cookie, so an attacker can open browser DevTools, set `Cookie: username=admin`, and gain full administrator access without knowing any password. This flaw is in `app.py` at lines 15 and 146.

The fix is to replace the plain cookie with Flask's built-in signed session, which cryptographically ties the session to the server's secret key. The secret key itself should be loaded from an environment variable rather than hardcoded. The cookie should also have the HttpOnly and Secure flags set so it cannot be read by JavaScript or sent over plain HTTP.

### Tampering

**SQL Injection**

The app builds its database queries by pasting user input directly into the query string using f-strings. This means an attacker can type `admin' --` as the username on the login page and get straight in as administrator without a password. The `--` turns the rest of the query into a comment, so the password check never runs. This affects the login route at `app.py` line 140 and many other routes throughout the file.

The fix is to use parameterised queries instead of f-strings, where a placeholder is put in the query and the actual value is passed separately, so the database never treats user input as part of the instruction.

**Stored Cross-Site Scripting (XSS)**

Product descriptions and review comments are pasted directly into the HTML page without any checks. An attacker can submit a product with a script tag in the description field and that script will run in the browser of every user who visits the page, including the admin. This is in `app.py` at lines 62 to 64 and 395 to 397.

The fix is to turn on Jinja2's autoescaping, which converts any HTML characters in user input into harmless text before rendering them on the page.

### Repudiation

There is no audit logging anywhere in the application. If a seller deletes a product, a user escalates their role, or an admin makes changes, there is no record of who did what or when. This means if something goes wrong, there is no way to prove who was responsible.

The fix is to add an append-only audit log table to the database that records the username, the action taken, the timestamp, and the IP address before any sensitive action is committed. This gives administrators a trail they can refer back to.

### Information Disclosure

There are two information disclosure issues in the app.

The first is that the app is running in debug mode at line 465 of `app.py`. Debug mode is a developer tool that shows detailed error pages including server file paths and source code when something goes wrong. If the app were ever deployed with this still on, an attacker could deliberately trigger an error and read sensitive information directly from the browser.

The second is that passwords are stored as plain readable text in the database, as seen in `init_db.py` at line 14. If an attacker ever got hold of the database file, every user's password would be immediately visible with no effort required.

The fixes are to turn debug mode off before any deployment, and to store passwords as hashed values using a library like bcrypt so that even if the database is stolen, the actual passwords cannot be read.

### Denial of Service

The app has no rate limiting on any of its routes, including the login and registration pages. This means an attacker could send thousands of login attempts per second without being blocked, either to guess passwords through brute force or simply to overload the server and make it unavailable to real users.

A way to avoid this is to add rate limiting to the login and registration routes so that after a certain number of failed attempts from the same IP address, further requests are temporarily blocked. The Flask-Limiter library handles this with just a few lines of code.

### Elevation of Privilege

There are two privilege escalation issues in the app.

The first is the role upgrade route at `app.py` line 182. Any logged-in buyer can visit `/become_seller` and immediately become a seller with no admin approval required. There is no check, no confirmation, and no oversight on this action.

The second is the product deletion route at `app.py` line 320. The route checks that the user is a seller or admin before allowing deletion, but it does not check whether the product actually belongs to that seller. This means any seller can delete any other seller's products.

A way to avoid the first issue is to remove the self-service upgrade entirely and require an administrator to manually approve role changes. For the second issue, the delete query should include a check that the product belongs to the seller making the request before carrying out the deletion.

## SDLC Integration

The threats above map to different stages of the development lifecycle:

- **Requirements stage** :- Elevation of Privilege (self-service role upgrade) and Spoofing (unsigned cookie) are design decisions that should have been challenged before any code was written
- **Implementation stage** :- Tampering (SQL injection and XSS) and Information Disclosure (plaintext passwords) are coding failures that a code review or static analysis tool would have caught during development
- **Deployment stage** :- Information Disclosure (debug mode on) and Denial of Service (no rate limiting) are configuration issues that a deployment checklist would have prevented
- **Every Stage** :- Repudiation (no audit logging) requires a decision at design, implementation during coding, and verification at deployment
