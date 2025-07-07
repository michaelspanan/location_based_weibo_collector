# Security Policy

## Supported Versions

We actively maintain and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### 1. **DO NOT** create a public GitHub issue
Security vulnerabilities should be reported privately to prevent potential exploitation.

### 2. **Email us** at [security@example.com](mailto:security@example.com)
Include the following information:
- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Potential impact** assessment
- **Suggested fix** (if any)

### 3. **Response timeline**
- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Resolution**: As soon as possible, typically within 30 days

### 4. **Disclosure policy**
- We will acknowledge receipt of your report
- We will keep you updated on our progress
- We will credit you in the security advisory (unless you prefer to remain anonymous)
- We will coordinate the public disclosure

## Security Best Practices

### For Users
- **Keep dependencies updated**: Regularly update the package and its dependencies
- **Use secure cookies**: Ensure your Weibo cookies are obtained securely
- **Monitor rate limits**: Respect Weibo's terms of service and rate limits
- **Validate input data**: Always validate location names and coordinates

### For Developers
- **Code review**: All changes are reviewed for security implications
- **Dependency scanning**: We regularly scan for known vulnerabilities
- **Input validation**: All user inputs are validated and sanitized
- **Error handling**: Sensitive information is not exposed in error messages

## Known Security Considerations

### Authentication
- **Cookie-based authentication**: The tool uses Weibo cookies for authentication
- **Secure storage**: Store cookies securely and do not commit them to version control
- **Regular rotation**: Rotate cookies regularly to maintain security

### Data Privacy
- **User consent**: Ensure you have proper consent for data collection
- **Data handling**: Handle collected data according to privacy regulations
- **Data retention**: Implement appropriate data retention policies

### Rate Limiting
- **Respectful scraping**: The tool includes built-in delays to respect rate limits
- **Configurable delays**: Adjust delays based on your needs and Weibo's policies
- **Monitoring**: Monitor your usage to avoid being blocked

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2) and will be clearly marked in the changelog.

## Contact

For security-related questions or concerns:
- **Email**: [security@example.com](mailto:security@example.com)
- **PGP Key**: [Available upon request]

Thank you for helping keep Location-based Weibo Data Collector secure! 