# Admin / White-Label / Transfer System

## Secure commercial model
1. Platform owner creates an organization tenant.
2. Tenant receives an immutable tenant ID.
3. Authorized owner verifies email OTP.
4. Authorized owner verifies contact OTP.
5. Optional MFA is required for ownership transfer.
6. Transfer creates a signed ownership-transfer transaction.
7. Recipient accepts through a separate verified account.
8. Old owner loses privileged access only after acceptance and grace-period checks.
9. All actions are written to an append-only audit log.
10. Billing, domains, branding, API keys, data ownership and model entitlements transfer according to explicit policy.
11. The platform never changes identity records merely to make the software appear to be owned by another person.
12. White-label branding can change legally controlled organization name, logo, domain and contact details.
13. Existing audit history remains immutable.
14. Data export/import is cryptographically signed.
15. Tenant isolation is mandatory.
16. Super-admin actions require step-up authentication.
17. Email OTP and contact OTP have expiry, attempt limits and replay protection.
18. Recovery requires verified ownership and documented support workflow.
19. Every transfer has a unique transaction ID.
20. Every transfer has before/after snapshots and a reason code.

## Required entities
- organizations
- organization_members
- ownership_transfer_requests
- verified_contacts
- otp_challenges
- branding_profiles
- billing_accounts
- tenant_domains
- api_credentials
- audit_events
- data_export_jobs
- model_entitlements
- knowledge_entitlements

## Anti-abuse controls
- No fake identity generation.
- No forged certificates or prescriptions.
- No deceptive medical claims.
- No transfer without recipient consent.
- No admin impersonation.
- No bypass of OTP/MFA.
- Rate-limit OTP requests.
- Device/risk scoring.
- IP reputation checks where lawful.
- Suspicious-transfer hold.
- Manual review for high-risk transfers.
