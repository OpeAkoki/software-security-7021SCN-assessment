# Task B — Threat Modelling and SDLC Mapping

## Data Flow Diagram

See `dfd.png` for the Data Flow Diagram created using OWASP Threat Dragon. The diagram models the NovaTrust Bank Mobile Application across three trust boundary zones: the Internet Zone (external entities), the Application Zone (DMZ), and the Internal Network Zone (data stores).

## System Description

The NovaTrust Bank Mobile Application allows customers to log in using a username, password, and one-time passcode delivered by SMS, view account balances and transaction history, and send payments to other accounts via an external payment gateway. Bank administrators access a separate admin panel to manage user accounts. Every sensitive action is recorded by an audit logging service that writes to an append-only log database. The application services sit in a DMZ, with all databases held in a separate internal network zone that no external entity can reach directly.

## STRIDE Threat Analysis

### Spoofing

#### Threat: Attacker impersonates a legitimate customer

The authentication service accepts a username and password from the customer, then issues a session token that is used to identify the user on subsequent requests. If session tokens are generated with insufficient randomness, an attacker can predict or brute-force a valid token and hijack another user's session without ever knowing their password. This is a particular risk on the Customer to Authentication Service flow and the Authentication Service to Session Store write.

The fix is to generate session tokens using a cryptographically secure random number generator (for example, Python's `secrets.token_hex(32)`), set a short expiry time on the token, and invalidate the token on logout. The session cookie must have HttpOnly and Secure flags set so it cannot be read by JavaScript or transmitted over plain HTTP.

#### Threat: Attacker bypasses 2FA by replaying an OTP

The authentication service sends an OTP to the SMS gateway, which delivers it to the customer's phone. If the OTP has a long validity window or can be reused, an attacker who intercepts a code (through SIM-swapping or by compromising the SMS gateway) can use it to authenticate as the victim.

The fix is to set a short expiry (60 to 90 seconds) on every OTP, invalidate it immediately after first use, and rate-limit the number of OTP attempts allowed per session.

---

### Tampering

#### Threat: Attacker modifies a transaction in transit

The transaction processing service sends a payment instruction to the external payment gateway. If this request travels over plain HTTP, or if the message integrity is not verified, an attacker with a position on the network could modify the destination account number or the transfer amount before it reaches the gateway.

The fix is to enforce TLS on all connections between internal services and external services, including the payment gateway. Payment instructions should be signed with a server-side HMAC so the gateway can verify the instruction has not been altered in transit.

#### Threat: Attacker tampers with the audit log

The audit log database is described as append-only, but if the database user account used by the audit logging service has UPDATE or DELETE privileges, a compromised internal service could overwrite or delete log entries to conceal malicious activity.

The fix is to grant the audit logging service only INSERT privileges on the audit log table, and to deny UPDATE and DELETE to all application accounts. Write-once storage or a separate tamper-evident log store provides an additional layer of assurance.

#### Threat: SQL injection through account management queries

If the account management service constructs database queries by concatenating user-supplied values such as account numbers or search terms, an attacker can inject SQL syntax to read data from other accounts or alter account balances.

The fix is to use parameterised queries with placeholders throughout every service that communicates with the user accounts database and the transaction history database.

---

### Repudiation

#### Threat: Customer denies initiating a transaction

A customer who transfers money to the wrong account, or a fraudulent transfer made using a stolen session, could be denied if there is no reliable record of who authorised the action and when.

The audit logging service addresses this by recording every transaction event with the session token, the authenticated username, the source and destination accounts, the amount, a timestamp, and the originating IP address. The key requirement is that these records must be written before the transaction is committed, not after, and they must be stored in the append-only audit log database rather than the main transaction history database, so that a compromise of the transaction service cannot touch the audit trail.

#### Threat: Administrator denies making account changes

An administrator who disables or modifies a customer account could deny the action if there is no record of their admin session. Every action taken through the admin panel must be logged to the audit log database with the administrator's identity, the action taken, and the timestamp. This flow is shown in the DFD as Admin Panel to Audit Logging Service.

---

### Information Disclosure

#### Threat: Credentials or session tokens exposed over unencrypted connections

The customer sends their username and password to the authentication service. If this connection is not encrypted, an attacker on the same network can capture these credentials in plain text using a packet capture tool.

The fix is to enforce HTTPS on all externally facing endpoints and to reject any plain HTTP connections rather than redirecting them, since the redirect itself leaks the original request. All cookies must carry the Secure flag.

#### Threat: Account data returned to the wrong user

The account management service retrieves account balances and statements from the user accounts database and the transaction history database. If the session token is not verified before each query, or if the query does not scope its results to the authenticated user's account, one customer could retrieve another customer's data by manipulating the account number in the request.

The fix is to validate the session token against the session store on every request and to enforce that every query includes the user ID from the verified session rather than an account identifier supplied by the client.

#### Threat: Sensitive data stored in plain text

If the user accounts database stores passwords as plain text, a database breach exposes every customer's credentials immediately.

The fix is to store only bcrypt hashes of passwords, never the passwords themselves. The database should also encrypt sensitive fields such as account numbers and balances at rest, separate from application-level access controls.

---

### Denial of Service

#### Threat: Brute force or credential stuffing against the login endpoint

The authentication service is accessible from the internet. Without rate limiting, an attacker can send thousands of login attempts per second to either guess a customer's password or exhaust server resources and make the service unavailable.

The fix is to apply rate limiting at the authentication service (for example, a maximum of five failed attempts per username per fifteen minutes before a temporary lockout), and to add CAPTCHA or device fingerprinting for requests that show automated patterns. A web application firewall in front of the DMZ can also drop high-volume automated traffic before it reaches the application.

#### Threat: Transaction flood overwhelming the payment gateway

The transaction processing service calls the external payment gateway for every payment instruction. An attacker who has gained access to a valid session could submit a large volume of small payment requests, consuming payment gateway API quota and potentially creating a chargeable event for each one.

The fix is to enforce a per-user transaction rate limit and a daily transfer cap, and to queue payment instructions through an internal message queue rather than calling the payment gateway synchronously, so a spike in requests does not propagate directly to the external service.

---

### Elevation of Privilege

#### Threat: Customer accesses admin panel functions

The admin panel is intended only for bank administrators, but if the application enforces this by checking a role value that is stored in a client-controlled cookie or request parameter, a customer could modify that value to gain access to user management functions.

The fix is to store the user's role server-side in the session store and never trust any role information sent by the client. Every request to admin panel routes must check the session-held role against a server-side access control list before processing the request.

#### Threat: Horizontal privilege escalation between customer accounts

If the account management and transaction processing services use a user-supplied account number to look up data rather than deriving the account from the authenticated session, a customer could substitute another customer's account number in the request and read or transfer from that account.

The fix is to derive the acting account from the verified session on every request and to reject any request where the client-supplied account identifier does not match the session-held identity.

#### Threat: Compromised service escalates within the internal network

If a vulnerability in the transaction processing service is exploited, the attacker gains the privileges of that service within the internal network. If that service has direct access to all four data stores with broad permissions, the attacker can reach the audit log, the session store, and all account data.

The fix is to apply the principle of least privilege at the database level. Each service should have its own database user with permissions scoped only to the tables and operations it legitimately needs. The audit log database user should have insert-only access as described in the Tampering section above.

---

## SDLC Integration

The threats above map to different stages of the software development lifecycle:

- **Requirements stage**: Elevation of Privilege threats (role enforcement, account scoping) must be defined as explicit security requirements before any code is written. If the requirement says "users can only see their own accounts", the developer has a clear rule to implement and a tester has a clear condition to verify.

- **Design stage**: Repudiation (audit logging architecture), Information Disclosure (encryption at rest, HTTPS enforcement), and the trust boundary layout shown in the DFD are all design decisions. Getting them wrong at this stage means the whole codebase inherits the flaw.

- **Implementation stage**: Tampering (SQL injection, message integrity), Information Disclosure (plaintext passwords), and the session token generation issues under Spoofing are all coding failures. SAST tooling such as Semgrep and Bandit would flag parameterisation failures and hardcoded secrets during development, and code review would catch weak session token generation.

- **Testing stage**: Denial of Service (rate limiting gaps) and horizontal privilege escalation are best found through dedicated penetration testing and dynamic analysis. OWASP ZAP can test for missing rate limiting headers and probe for IDOR vulnerabilities through automated active scanning.

- **Deployment and operations stage**: Information Disclosure (HTTPS enforcement, cookie flags) and the least privilege database configuration are deployment concerns. A deployment checklist or infrastructure-as-code review would catch missing TLS configuration or overly broad database grants before the system goes live.

- **Every stage**: Spoofing (session management) cuts across all stages: the requirement defines what a valid session looks like, the design decides where session state is stored, the implementation generates and validates tokens, testing verifies that forged tokens are rejected, and operations monitors for anomalous session activity.
