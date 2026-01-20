# Security Policy

## Reporting a Vulnerability

Report security vulnerabilities via email to ged1182@gmail.com.

Do NOT create public GitHub issues for security vulnerabilities.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Considerations

This project demonstrates AI systems with transparent reasoning. Key security measures:

- API keys are stored in environment variables, never in code
- CORS is configured to allow only specific origins
- Codebase Oracle has path traversal protection
- All user inputs are validated through Pydantic models
