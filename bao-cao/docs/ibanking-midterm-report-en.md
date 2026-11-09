# iBanking Tuition Payment Midterm Project Report

This report documents the implemented tuition payment subsystem for the Ton Duc Thang University coursework project. It follows the eight assessment requirements in order: business and data analysis, microservice architecture, REST API design, database implementation, service implementation, transactions and concurrency, user interface implementation, and product documentation and demonstration. The application is an educational simulation. Its demonstration stack uses local HTTP, PostgreSQL, and Mailpit; it does not connect to a bank or the university finance system.

## 1 Business Analysis and UML

### 1.1 Scope and business rules

An authenticated iBanking customer can view the payer account, look up a student's tuition by an eight-digit student ID, and pay the full outstanding amount. The student may be someone other than the payer. The payer's name, phone number, and email come from the logged-in account and are displayed read-only. The client does not choose a payment amount; Payment Service reads the amount from the tuition record. There is no registration or partial payment flow.

The main rules are: (R1) protected operations require a valid JWT; (R2) only an unpaid tuition item can be paid; (R3) available balance must cover the whole amount; (R4) the customer must accept the displayed terms; (R5) each payment has a six-digit email OTP valid for five minutes and usable once; (R6) balance and tuition status are checked again at OTP confirmation; (R7) debit, debt settlement, payment success, OTP use, and the receipt job commit atomically; (R8) receipt delivery happens after that commit and can be retried without reversing the payment.

### 1.2 Actors and system boundary

| Element | Role | UML treatment |
|---|---|---|
| Customer | Logs in, looks up tuition, accepts terms, enters the email OTP, and reviews results. The customer can pay another student's tuition. | Primary actor outside the iBanking boundary. |
| iBanking system | Coordinates authentication, tuition lookup, payment, and notification. | The system boundary, not an actor in its own use case diagram. |
| Email provider | Delivers OTP and receipt messages sent by the internal Notification Service. | Supporting external actor. Mailpit plays this role in the local demonstration. |
| Database | Persists users, wallets, students, tuition, payments, OTPs, and email jobs. | Internal data store shown in architecture and ERD, not a UML actor. |

### 1.3 Use case specifications

**UC01 Log in.** Primary actor: Customer. Precondition: a seeded user account exists. Main flow: the customer enters username and password; Account Service validates the request, verifies the Argon2 password hash, and issues an HS256 JWT containing the user ID and email. Exceptions: invalid request returns `400 VALIDATION_ERROR`; wrong credentials return `401 INVALID_CREDENTIALS`; an unexpected server error returns 500. Postcondition: on success the browser has a Bearer token; no financial data changes on failure.

**UC02 View profile and balance.** Primary actor: Customer. Precondition: valid JWT. Main flow: the browser calls Account `GET /users/me` and Payment `GET /wallet`, then displays the payer details and available VND balance read-only. Exceptions: a missing or expired JWT returns 401; a missing wallet returns 404. Postcondition: the customer sees current values, but this display does not reserve funds or replace the later server-side balance check.

**UC03 Look up tuition by student ID.** Primary actor: Customer. Precondition: valid JWT and an eight-digit student ID. Main flow: Payment finds the student and the associated tuition item and returns student name, item ID, amount, currency, status, and payment time if already paid. Exceptions: invalid format returns 400; an unknown student or absent tuition returns 404; a paid item is displayed but cannot be submitted again. Postcondition: the selected tuition is known and no payment has been created.

**UC04 Create full payment.** Primary actor: Customer. Precondition: authenticated user, selected unpaid tuition, and accepted terms. Main flow: the browser sends `tuitionId`, `termsAccepted`, and a UUID `requestId`; Payment reads the amount from the database, checks the wallet and tuition, creates a `PENDING_OTP` payment and hashed OTP with a five-minute expiry, commits them, and requests OTP email delivery. Exceptions: already paid returns 409, insufficient balance returns 422, missing records return 404, conflicting request ID returns 409, and an unavailable notification service results in a failed payment and 503. Postcondition: a successful creation returns payment information and sends an OTP; the wallet has not been debited.

**UC05 Confirm with email OTP.** Primary actor: Customer; supporting actor: Email provider. Precondition: an owned payment is `PENDING_OTP` and the OTP has not expired. Main flow: the customer enters the six-digit code; Payment locks the payment and OTP rows, compares the code hash, checks expiry and one-time use, and proceeds to UC06. Exceptions: invalid or used code returns `422 INVALID_OTP`; expired code returns `422 OTP_EXPIRED` and records `EXPIRED`; a payment owned by another user returns 403. Postcondition: a valid code permits the financial transaction; an invalid code never debits the wallet.

**UC06 Commit payment and send receipt.** Primary actor: Customer; supporting actor: Email provider. Precondition: UC05 has accepted an OTP for the payment. Main flow: Payment locks the wallet and tuition rows, rechecks balance and unpaid status, debits the wallet, marks tuition `PAID`, marks payment `SUCCESS`, records OTP use, creates a pending receipt job, and commits. It then asks Notification to send the receipt. Exceptions: another payment may have consumed funds (`422 INSUFFICIENT_BALANCE`) or paid the tuition (`409 TUITION_ALREADY_PAID`); a pre-commit database failure rolls back the financial changes. A post-commit receipt failure leaves the payment successful and the job pending for retry. Postcondition: the financial records agree and the customer sees the result and history.

The use case diagram places the Customer and Email Provider outside the iBanking boundary. OTP confirmation leads to payment commit only after validation. The database is represented in the ERD and architecture instead of as an actor.

Figure 1. Use Case Diagram. Editable source: `bao-cao/docs/01-use-case-final.drawio`.

### 1.4 Conceptual data model

The initial five-entity model comprises `Users`, `Students`, `Tuitions`, `Transactions`, and `OTPs`. One student may have tuition items; a user may initiate transactions; each transaction concerns one tuition item and has at most one OTP in the implemented flow. The conceptual `Transactions` entity maps to the physical `payments` table. Actual account balance is held in `wallets` within Payment DB, so the physical model has more tables than the five-entity brief.

Figure 2. Conceptual ERD. Editable source: `bao-cao/docs/03-conceptual-erd-final.drawio`.

## 2 Microservice Architecture

### 2.1 Service decomposition and data ownership

| Component | Responsibility | Owned data |
|---|---|---|
| React frontend | Renders login, account overview, tuition lookup, payment confirmation, and history; calls public APIs. | No server database. JWT is held in browser `sessionStorage`. |
| Account Service | Verifies passwords, issues JWTs, and returns the current user's profile. | `ibanking_account.users`. |
| Payment Service | Owns wallets, tuition records, OTP verification, payment lifecycle, financial transaction, and receipt jobs. | `ibanking_payment.wallets`, `students`, `tuitions`, `payments`, `otps`, `email_jobs`. |
| Notification Service | Validates internal email requests, sends SMTP messages, and tracks message IDs and delivery state. | `ibanking_notification.email_messages`. |

The three logical databases run in a single PostgreSQL 16 container in Docker Compose. Each service connects to its own database. Payment's `user_id` is a logical reference to Account's user ID, not a cross-database foreign key. Payment sends a receipt using a stable message ID; the relation between its `email_jobs` and Notification's `email_messages` is through an API request, not a database constraint.

### 2.2 Communication and architecture choice

The browser calls Account and Payment over local HTTP. Account issues a JWT; the browser sends `Authorization: Bearer <token>` to authenticated routes. Payment verifies JWT claims locally using the configured shared secret, issuer, and audience. Payment calls Notification synchronously via internal REST using `X-Internal-Key`; Notification sends SMTP to Mailpit in the demo configuration. The internal key stays on the server side. The code does not currently deploy HTTPS/TLS for the local stack.

This decomposition keeps the balance, tuition, payment, and OTP updates within one Payment database transaction. It avoids a distributed financial transaction across services. Notification is separated because email delivery can fail independently; the durable `email_jobs` record allows receipt retry after a successful payment. The architecture is appropriate for the coursework demonstration, although shared-secret configuration, HTTP transport, and deployment hardening require further work before production use.

Figure 3. Microservices Architecture Diagram. Editable source: `bao-cao/docs/02-microservices-architecture-final.drawio`.

## 3 REST API Design

### 3.1 Conventions and endpoint inventory

Public API paths use `/api/v1`; the email endpoint uses `/internal/v1`. Request and response bodies are JSON. Protected public endpoints require Bearer JWT, while the internal email endpoint requires `X-Internal-Key`. Validation rejects extra body fields. Errors use `{"code":"ERROR_CODE","message":"Readable message"}`. Request schema errors return 400; authentication and authorization errors return 401 and 403; absent resources return 404. Business conflicts use 409, invalid financial or OTP state uses 422, unavailable email delivery uses 503, and unexpected errors use 500.

| Service | Method | URI | Main success |
|---|---|---|---|
| Account | POST | `/api/v1/auth/login` | 200, access token. |
| Account | GET | `/api/v1/users/me` | 200, payer profile. |
| Payment | GET | `/api/v1/wallet` | 200, current user's wallet. |
| Payment | GET | `/api/v1/tuition/{mssv}` | 200, student and tuition item. |
| Payment | POST | `/api/v1/payments` | 201 new payment, or 200 idempotent repeat. |
| Payment | GET | `/api/v1/payments` | 200, current user's payment list. |
| Payment | GET | `/api/v1/payments/{paymentId}` | 200, owned payment. |
| Payment | POST | `/api/v1/payments/{paymentId}/confirm` | 200, confirmed payment. |
| Notification | POST | `/internal/v1/notifications/email` | 200, sent message status. |
| All backend services | GET | `/api/v1/health` | 200, process health response. |

### 3.2 Account API

`POST /api/v1/auth/login` takes `{"username":"demo3","password":"Demo!2026"}`. Both fields are required nonempty strings; username is limited to 50 characters, password to 128. A successful response is `{"accessToken":"<JWT>","tokenType":"Bearer","expiresIn":3600}` under the default configuration. Invalid input returns `400 VALIDATION_ERROR`; wrong credentials return `401 INVALID_CREDENTIALS`; unhandled server failure returns `500 INTERNAL_ERROR`.

`GET /api/v1/users/me` takes no body or query parameters and requires Bearer JWT. It returns `userId`, `fullName`, `phone`, and `email`; it never returns the password hash. Missing, invalid, or expired credentials return `401 UNAUTHORIZED`.

### 3.3 Payment API

`GET /api/v1/wallet` requires Bearer JWT and returns `{"userId":"u3","balance":20000000,"currency":"VND"}` for the current user, with the balance depending on prior transactions. A missing wallet returns `404 WALLET_NOT_FOUND`; invalid authentication returns 401.

`GET /api/v1/tuition/{mssv}` takes an eight-digit path parameter. It returns `studentId`, `studentName`, `tuitionId`, `amount`, `currency`, `status`, and `paidAt`. The item may be `PAID` for display, but creation is blocked. Invalid MSSV returns `400 VALIDATION_ERROR`; absent student or tuition returns `404 STUDENT_NOT_FOUND` or `TUITION_NOT_FOUND`.

`POST /api/v1/payments` takes `{"tuitionId":"<item ID>","termsAccepted":true,"requestId":"<UUID>"}`. The server looks up the full amount; the client does not send it. A new payment returns 201 and a Payment response with `paymentId`, `tuitionId`, `studentId`, `studentName`, `amount`, `currency`, `status`, `createdAt`, `otpExpiresAt`, `paidAt`, and `failureCode`. Repeating the same user request ID for the same tuition returns the existing payment with 200. Relevant errors include 400 validation, 401 authentication, 404 wallet/tuition missing, 409 paid tuition or request ID conflict, 422 insufficient balance, and 503 unavailable OTP delivery.

`GET /api/v1/payments` requires Bearer JWT and returns `{"items":[...]}` for the current user, ordered by `createdAt` descending. `GET /api/v1/payments/{paymentId}` returns one owned Payment response; an unknown ID returns 404 and another user's payment returns 403.

`POST /api/v1/payments/{paymentId}/confirm` takes `{"otp":"123456"}`. The OTP must be six digits. It returns a Payment response with `SUCCESS` after the transaction commits; confirming an already successful owned payment returns its existing result without another debit. Error examples are 400 invalid body, 401 missing or bad JWT, 403 wrong owner, 404 missing payment/wallet, 409 tuition paid or payment no longer awaiting OTP, and 422 invalid/expired OTP or insufficient balance. An operational lock conflict can return `409 REQUEST_IN_PROGRESS`.

### 3.4 Notification API and error handling

`POST /internal/v1/notifications/email` requires `X-Internal-Key`. For an OTP, the JSON includes `messageId`, `type:"OTP"`, `to`, and `data` with `paymentId`, `otp`, and `expiresAt`. For a receipt, `type:"PAYMENT_SUCCESS"` uses `paymentId`, `studentId`, `studentName`, `amount`, `currency`, and `paidAt`. A successful or identical previously sent request returns `{"messageId":"...","status":"SENT"}`. Invalid schema returns 400; invalid internal key returns 403; conflicting message ID or in-progress delivery returns 409; SMTP failure returns 503.

The shared [common.py](../../src/services/common.py) maps FastAPI request validation errors to HTTP 400 and unexpected exceptions to HTTP 500. Business checks remain in the relevant service. The frontend reads the returned `code` and `message`; it does not infer financial success from email delivery. Actual confirmation can return 200 even while the receipt job remains pending, because the financial commit has already succeeded.

## 4 Database Design

### 4.1 Physical schema and constraints

The implemented business schema has eight tables. Account DB has `users` with primary key `id`, unique `username`, Argon2 `password_hash`, `full_name`, `phone`, and `email`. Notification DB has `email_messages` with primary key `message_id`, `payload_hash`, `status`, and `updated_at`. The two services also use `schema_migrations` metadata to record their applied SQL migrations.

Payment DB has `wallets(user_id, balance, currency)`, `students(student_id, full_name)`, `tuitions(tuition_id, student_id, amount, status, paid_at)`, `payments(payment_id, user_id, tuition_id, request_id, amount, status, created_at, otp_expires_at, paid_at, failure_code)`, `otps(otp_id, payment_id, code_hash, issued_at, expires_at, used_at)`, and `email_jobs(job_id, payment_id, email_to, status, attempts)`. Foreign keys within Payment DB connect tuition to student and payment to tuition; OTP and email job each reference a payment. `otps.payment_id` and `email_jobs.payment_id` are unique. `(payments.user_id, payments.request_id)` is unique. Check constraints require nonnegative wallet balance and positive tuition amount.

Figure 4. Physical ERD. Editable source: `bao-cao/docs/04-physical-erd-final.drawio`.

### 4.2 Initialization and consistency boundary

`src/docker/postgres-init.sql` creates the three logical databases on first volume initialization. Account and Notification apply versioned SQL migrations before serving requests. Payment currently uses SQLAlchemy `Base.metadata.create_all()` and an idempotent seed loader. Base demo data come from `src/data/demo-base.json`; `src/data/demo-extra.json` extends them. Re-running seeds does not reset an existing wallet balance or payment history. Payment's database is the atomic consistency boundary for the financial update and receipt job.

## 5 Service and API Implementation

### 5.1 Account and Notification

Account is implemented in FastAPI with SQLAlchemy. It verifies the submitted password against an Argon2 hash, issues an HS256 JWT with `sub`, `email`, issuer, audience, issue time, and expiry, and returns profile fields only after JWT verification. The configured frontend origin is allowed by CORS. Notification validates a discriminated request body for `OTP` or `PAYMENT_SUCCESS`, checks the internal key, records the payload hash under `messageId`, and sends through SMTP. A repeated sent message with the same payload returns `SENT`; reusing an ID for different content returns 409. Mailpit receives mail in the demo stack.

### 5.2 Payment and OTP flow

Payment creates the `PENDING_OTP` payment and a six-digit OTP hash before asking Notification to deliver the code. At confirmation it verifies ownership, state, expiry, one-time use, and hash, then obtains database row locks and rechecks the wallet and tuition. The financial changes and receipt job are committed together. Receipt sending runs after commit; a background task retries pending receipt jobs about every 30 seconds. The Payment response never exposes the OTP or hash.

Figure 5. Payment and OTP Flow. Editable source: `bao-cao/docs/05-payment-otp-flow-final.drawio`.

## 6 Transactions and Concurrency

PostgreSQL `SELECT FOR UPDATE` row locks are applied when Payment confirms an OTP. The code locks payment and OTP rows, then wallet and tuition rows, and rechecks business conditions after obtaining the locks. For SQLite unit tests, it uses `BEGIN IMMEDIATE`. The wallet debit, tuition settlement, payment success, OTP use, and receipt job are committed in the same Payment DB transaction. A failure before commit leaves no partial financial update.

In **T21**, one wallet starts with VND 10,000,000 and two unpaid tuition items each cost VND 7,000,000. Concurrent confirmations yield one HTTP 200 success and one HTTP 422 insufficient-balance response; the final wallet balance is VND 3,000,000. In **T22**, two wallets confirm payment for the same VND 7,000,000 tuition item. Only one receives HTTP 200; the other receives HTTP 409 tuition-already-paid, and the losing wallet remains unchanged. The test script verifies both cases on the running PostgreSQL stack.

Idempotency is handled at three levels: a unique `(user_id, request_id)` pair prevents duplicate payment creation, repeated confirmation of an already successful payment returns its previous result, and a stable Notification `messageId` prevents resending a completed email request. No distributed financial transaction is required across Account, Payment, and Notification.

Figure 6. Concurrency and Consistency. Editable source: `bao-cao/docs/06-concurrency-final.drawio`.

## 7 User Interface Implementation and API Integration

### 7.1 Screens and user interaction

The React/Vite application implements a login view, an account overview at `/`, and a separate tuition payment page at `/tuition-payment`. The overview shows the logged-in customer's profile, current wallet balance, and recent payment activity. On the payment page, the payer's name, phone, email, and balance are displayed read-only from authenticated API responses. The customer enters an eight-digit student ID; the page shows the returned student, tuition item, full amount, and status. A paid item cannot be submitted again. The customer must accept the displayed terms before starting payment, then enters the six-digit code received by email to confirm it.

### 7.2 Frontend integration with backend APIs

The frontend's shared `api()` function sends JSON and attaches the Bearer JWT to protected Account and Payment calls. After login, `refresh()` requests `GET /users/me`, `GET /wallet`, and `GET /payments` together. Tuition lookup uses `GET /tuition/{mssv}`. Payment creation sends only `tuitionId`, `termsAccepted`, and a generated UUID `requestId`; it does not send or calculate the amount. OTP confirmation calls `POST /payments/{paymentId}/confirm`. On success, the page reloads wallet and history from the backend and updates the displayed tuition status. Error responses are shown using their returned messages; the server remains the authority on balance and payment state.

Lookup requests are delayed by 300 ms and aborted when the input changes. A request sequence number also prevents a slower response for an old student ID from replacing the current result. The UI disables payment when the displayed balance is below the tuition amount, while Payment Service checks that condition again when creating and confirming the transaction. The history view uses `paidAt` for a successful transaction and `createdAt` otherwise, formatted in the Vietnam time zone. These behaviors are implemented in `src/frontend/src/main.jsx`, with presentation rules in `src/frontend/src/style.css`.

### 7.3 User journey represented in the interface

The demonstrated path is login, account overview, open tuition payment, look up an unpaid student ID, accept terms, create a pending payment, read the OTP in Mailpit, confirm within five minutes, and review the updated balance, tuition status, transaction history, and receipt email. The payment page does not ask the customer to type payer details or a payment amount.

## 8 Product Documentation and Demonstration

### 8.1 Installation startup and usage guide

`src/README.md` documents Docker startup, local URLs, demo credentials, sample student IDs, the payment path, and test commands. The separate source guide `HUONG-DAN-DOC-CAU-TRUC-VA-SRC.md` explains each directory and service for a reader reviewing the implementation. The editable six-page draw.io master file and six individual diagrams are in `bao-cao/docs/`; this report embeds their rendered images.

The Compose configuration was checked with `docker compose -f compose.yaml config --quiet`. From `src`, run `docker compose -f compose.yaml up --build -d`, then inspect `docker compose -f compose.yaml ps`. Open the React UI at `http://localhost:5173` and Mailpit at `http://localhost:8025`. The default demo login is `demo3` with password `Demo!2026`. API documentation is under `/docs` on ports 8081, 8082, and 8083. The HTTP endpoints and demo credentials are intended for local coursework use.

### 8.2 Verification evidence

| Activity | Evidence and scope |
|---|---|
| `python -m pytest tests -q` | Account, Notification, and Payment unit tests, including invalid/expired OTP and concurrency behavior under SQLite. Six tests passed on 9 November 2026. |
| `npm run build` | Frontend compiles with Vite. |
| Docker demonstration | Six containers ran together. A verified payment flow covered login, OTP confirmation, updated balance and tuition, history, and two Mailpit messages. |
| `python tests/integration_postgres.py` | T21 and T22 use separate test records on live PostgreSQL and clean them afterward. The script checks response codes and final balances. |

These results establish the behavior of the demonstration stack and test cases, not production load tolerance or delivery to an Internet mailbox. The tests are in `src/tests/test_account_notification.py`, `src/tests/test_payment.py`, and `src/tests/integration_postgres.py`.

### 8.3 Suggested presentation sequence

Start with the six diagrams to explain the use cases, service boundaries, logical and physical data models, payment flow, and concurrency controls. Next, show the six Docker services running. Log in with a demo account, look up an unpaid tuition item, accept the terms, and create a payment. Open Mailpit to show the OTP, confirm it, then compare the updated wallet, paid tuition item, transaction time, and receipt email. Finally, describe the T21 and T22 PostgreSQL test results, emphasizing that only one conflicting payment succeeds in each case. `src/README.md` lists sample IDs for unpaid, already-paid, low-balance, and missing-data demonstrations.

### 8.4 Scope and limitations

The project is an educational simulation without a real bank ledger or TDTU debt system. Mailpit is a local test mailbox. The Compose defaults use local HTTP and demo secrets. Payment DB lacks versioned migrations, unlike Account and Notification. Before operating beyond a local demonstration, the project would need real secret management, transport protection, payment schema migrations, and additional load and failure testing. No claim is made here that those controls are already deployed.

## Conclusion

The implemented subsystem supports the full demo path from login and tuition lookup to email OTP, atomic payment, history, and receipt delivery. Its three backend services own separate logical databases, while Payment keeps all financial updates inside one database transaction. The PostgreSQL concurrency tests address both overspending from one wallet and duplicate payment of one tuition item. The editable UML, architecture, ERD, payment-flow, and concurrency diagrams accompany this report.

**Project sources:** `README.md`, `src/README.md`, `src/compose.yaml`, `src/services`, `src/data`, `src/frontend`, `src/tests`, and the six final diagrams under `bao-cao/docs`.
