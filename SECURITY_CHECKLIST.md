# IERL OS — Production Security Checklist

| Item | Verification | Status |
| :--- | :--- | :--- |
| **CORS Restriction** | Origins restricted to `ALLOWED_ORIGIN` env setting. Hostile origins rejected. Wildcard origin + credentials prohibited. | PASSED |
| **Security Headers** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, strict `Content-Security-Policy`, `Permissions-Policy`. | PASSED |
| **Rate Limiting** | Sliding-window limits are enforced on all non-health API routes; proxy headers are trusted only when explicitly configured. | IMPLEMENTED — load test required |
| **Authentication** | Optional API-key authentication is enforced when `REQUIRE_AUTH=true`; a deployment must validate its secret configuration. | IMPLEMENTED — deployment verification required |
| **Data Integrity** | A2 has no fabricated spot/probability fallback and is suspended until validated. Other analytical engines still require model and data validation. | PARTIAL — release blocker for investment use |
| **Secrets Protection** | `.env` and `API_KEYS_CONFIG.env` excluded from version control via `.gitignore`. Secrets never hardcoded. | PASSED |
| **Input Validation** | Typed Pydantic schemas enforce min/max constraints, symbol normalization, and prompt sanitization. | PASSED |
| **Production CSS** | Tailwind dev CDN script removed. The stylesheet is served by FastAPI and can be uploaded beside the static `index.html`. | IMPLEMENTED — deployment verification required |
