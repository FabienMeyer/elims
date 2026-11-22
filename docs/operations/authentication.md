# Authentication

Authentication and authorization behavior must be specified before protected workflows are implemented. Specifications must identify actors, permissions, session behavior, audit requirements, sensitive data, and failure handling.

Production business routes return HTTP 503 until an approved identity and authorization implementation replaces `require_application_access`. Health and readiness probes remain available.
