# iBanking Tuition Payment Report Part A

This report documents the implemented Part A: Account Service, Notification Service, and the web interface. Integration with the real Payment Service, actual email delivery, and financial concurrency require end to end verification. The Payment mock is useful for development but does not prove financial correctness.

## 1. Introduction and scope

The project simulates tuition payment through an iBanking application. A payer signs in, looks up a student's tuition by student ID, pays the full outstanding amount, confirms the transaction with an email OTP, and views the result and transaction history. Part A owns authentication, payer profiles, email notification, and the web interface. Part B owns wallets, tuition records, transactions, OTP validation, and financial consistency.

The main technical requirements are JWT authentication, service owned data, documented API schemas and errors, protection of internal credentials, responsive handling of slow requests, independent development using a mock, and configurable integration endpoints.

## 2. Business analysis

The use case source is `docs/use-case-A.puml`. The payer is the primary actor; the email system is an external actor. The main flow is sign in, view the profile and balance, look up tuition, accept the terms, create a transaction, receive and enter an OTP, and view the result and history. Payer information comes from the signed in account and is read only. Tuition must be paid in full.

The demonstration should cover incorrect credentials, an unknown student ID, no outstanding tuition, tuition already paid, insufficient balance, invalid or expired OTP, and email delivery failure. The interface displays loading and error states, while the backend remains responsible for authoritative validation.

## 3. Architecture

The diagrams and explanation are in `docs/architecture.md`. Part A implements Account Service on port 8081, Notification Service on port 8083, and the frontend on port 5173. Part B's Payment Service uses port 8082; Part A uses a mock on port 8089 during independent development. Account DB stores users, Payment DB stores financial data, and Notification DB stores email delivery state. Payment calls Notification using `X-Internal-Key`; the browser must never receive this key.

Grouping wallets, tuition, transactions, and OTP in Payment allows financial updates within one database transaction. Notification sends email after commit, with retry through an email job owned by Payment.

## 4. Part A data model

Account uses `users(id, username UNIQUE, password_hash, full_name, phone, email)`. Passwords are hashed with Argon2 and are never stored as plaintext. Notification uses `email_messages(message_id PRIMARY KEY, payload_hash, status, updated_at)`. The message ID identifies repeated send requests; the payload hash rejects reuse of the same ID with different content. Migrations are in `services/account/migrations` and `services/notification/migrations`; `services/migrate.py` records applied versions. Account seed data reads `02-du-lieu-mau.json` and preserves user IDs u1 and u2 for integration with Part B.

## 5. Part A REST APIs

| Method | Endpoint | Main response and errors |
|---|---|---|
| POST | `/api/v1/auth/login` | Bearer JWT with `expiresIn=3600`; invalid credentials return 401. |
| GET | `/api/v1/users/me` | Payer profile from the token; invalid token returns 401. |
| POST | `/internal/v1/notifications/email` | Send OTP or success email; invalid key returns 403; duplicate identical message returns 200; conflicting content returns 409; SMTP failure returns 503. |
| GET | `/api/v1/health` | Service name and `UP` status. |

Request models reject extra fields; validation failures return `400 VALIDATION_ERROR`. JWT validation accepts only HS256 and checks the signature, issuer, audience, issued at time, and expiry. The internal email API requires its own `X-Internal-Key`. Both FastAPI services expose runtime OpenAPI documentation at `/docs`; the shared contract is `01-openapi.json`.

## 6. Web interface and email implementation

The React interface includes sign in, a read only payer profile and balance, automatic lookup when the student ID reaches eight digits, tuition details, terms, full payment confirmation, OTP entry, results, and history. It cancels stale lookup requests and uses request sequence numbers so an earlier student lookup cannot overwrite a newer result. After payment, the frontend fetches the wallet and history again instead of calculating a balance locally.

Notification accepts OTP and `PAYMENT_SUCCESS` templates, builds the email body, and sends it through SMTP. For a `messageId` already marked `SENT` with identical content, the service returns the earlier result without contacting the provider again. If the provider fails, `FAILED` status allows retry with the same ID and content. An SMTP timeout alone cannot establish whether mail reached the inbox; the final demonstration must inspect the actual mailbox.

## 7. Transactions and concurrency

Part B implements the financial transaction. After integration, Part A must help verify two cases: two payments of 7 million from the same wallet holding 10 million, and two wallets attempting to pay the same tuition record. The team should compare the UI result, wallet, tuition state, history, and database or log evidence from Part B. The Part A mock cannot validate these concurrency properties.

## 8. Tests and observed results

`python -m pytest tests/test_a.py -q` reported **3 passed**. The tests cover valid and invalid login, profile access, missing JWT, extra request fields, internal key enforcement, repeated emails with the same `messageId`, content conflicts, retry after simulated SMTP failure, and a UI contract flow with the Payment mock. `npm run build` in `frontend` completed successfully. Docker Compose built and ran PostgreSQL, Account, Notification, the Payment mock, and the frontend; health endpoints and the frontend returned HTTP 200. Account DB contained two users with Argon2 password hashes.

An API flow in Compose returned login 200, payment creation 201, invalid mock OTP 422, and valid mock OTP 200; the mock balance changed from 10 million to 3 million. The Payment mock was restarted afterward to reset demonstration data. Notification returned 403 without its internal key; without SMTP configuration, a valid request returned 503 and stored `FAILED`. Actual inbox delivery and real financial transactions remain unverified without SMTP and Part B. Shared test matrix cases should only be marked PASS after executing each case against the intended integrated system.

## 9. Installation and use

Follow `src/README-A.md` to install Python dependencies, run migrations and seed data, start Account, Notification, and the Payment mock, and start the frontend. `src/compose-A.yaml` also runs Part A on PostgreSQL. During integration, change the Payment URL from 8089 to 8082, align JWT secret, issuer, audience, and internal key settings, then configure real SMTP and demonstration email accounts.

## 10. Conclusion and remaining work

Part A provides source code, diagram sources, migrations and seed data, APIs, a frontend, mock, tests, and run instructions. It supports independent development of authentication and the interface. Completion of the full project still depends on integration with the real Part B Payment Service, actual email delivery, transaction and concurrency verification, demonstration evidence, and updates to the final report and slides based on observed results.
