# Security Policy

## Supported Versions

We take security seriously. The following versions of ELIMS are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.x.x   | :white_check_mark: |
| < 0.0.1 | :x:                |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

Instead, please report security vulnerabilities privately through one of these methods:

### 1. GitHub Security Advisories (Preferred)

Report vulnerabilities through GitHub's private vulnerability reporting:

1. Go to the [Security tab](https://github.com/FabienMeyer/elims/security)
1. Click "Report a vulnerability"
1. Fill in the details

### 2. Email (Alternative)

Send an email to: **fabien.meyer@outlook.com**

Subject: `[SECURITY] Brief description of vulnerability`

## What to Include

When reporting a security vulnerability, please include:

- **Type of vulnerability** (e.g., SQL injection, XSS, authentication bypass)
- **Location** (file path, URL, API endpoint, etc.)
- **Step-by-step instructions** to reproduce the vulnerability
- **Proof of concept** (if applicable)
- **Impact** of the vulnerability
- **Suggested fix** (if you have one)
- **Your contact information** for follow-up

## Response Timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Fix timeline**: Depends on severity
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Within 90 days
  - Low: Next regular release

## Severity Guidelines

### Critical

- Remote code execution
- Authentication bypass
- Data breach potential
- Privilege escalation to admin

### High

- SQL injection
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Sensitive data exposure

### Medium

- Information disclosure
- Denial of service
- Session fixation

### Low

- Security misconfiguration
- Missing security headers
- Path disclosure

## Security Best Practices

When deploying ELIMS:

### 1. Use Strong Secrets

```bash
# Generate strong secrets
openssl rand -hex 32
```

Never use default or weak passwords in production!

### 2. Keep Dependencies Updated

```bash
# Update dependencies regularly
uv sync --upgrade
```

### 3. Use HTTPS

Always deploy with HTTPS in production. Configure Traefik with Let's Encrypt certificates.

### 4. Secure Database Access

- Use strong database passwords
- Restrict database access to internal networks only
- Enable database SSL/TLS if possible

### 5. Environment Variables

- Never commit `.env` files
- Use secrets management in production
- Rotate secrets regularly

### 6. Docker Security

- Don't run containers as root
- Use minimal base images
- Scan images for vulnerabilities
- Keep Docker updated

### 7. Network Security

- Use internal Docker networks
- Restrict external access
- Use firewall rules
- Monitor unusual traffic

### 8. Monitoring & Logging

- Enable logging for all services
- Monitor for suspicious activity
- Set up alerts for security events
- Review logs regularly

## Known Security Considerations

### Current Security Measures

- JWT token authentication
- CORS configuration
- SQL injection protection via ORM
- Password hashing (bcrypt/argon2)
- Environment variable security
- Docker network isolation

### Areas of Active Development

- Rate limiting
- API key management
- Two-factor authentication
- Audit logging
- Role-based access control (RBAC)

## Security Resources

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLModel Security](https://sqlmodel.tiangolo.com/)

## Security Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who help improve ELIMS security:

- Your name (if you wish to be credited)
- Link to your profile/website
- Description of the vulnerability

## Disclosure Policy

- We follow coordinated disclosure
- We will notify you when a fix is released
- We will credit you in release notes (if desired)
- We ask for 90 days before public disclosure
- We may request your assistance in validating fixes

## Out of Scope

The following are typically not considered security vulnerabilities:

- Brute force attacks without actual compromise
- Social engineering
- Physical access attacks
- Denial of service without amplification
- Issues in third-party dependencies (report to them directly)
- Theoretical vulnerabilities without proof of concept

## ⚖️ Legal

We will not pursue legal action against security researchers who:

- Follow responsible disclosure practices
- Do not access more data than necessary
- Do not disrupt our services
- Do not violate any laws in their country
- Act in good faith

______________________________________________________________________

**Thank you for helping keep ELIMS and its users safe!** 🛡️
