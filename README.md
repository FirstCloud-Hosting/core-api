# Core-API

![pylint Score](https://github.com/FirstCloud-Hosting/core-api/actions/workflows/pylint.yml/badge.svg)
![Docker Image](https://github.com/FirstCloud-Hosting/core-api/actions/workflows/docker-image.yml/badge.svg)
![CodeQL Status](https://github.com/FirstCloud-Hosting/core-api/actions/workflows/codeql-analysis.yml/badge.svg)

This is core API used for more applications created by FirstCloud-Hosting team.

## Fundamental basis

All applications created by FirstCloud-Hosting team are web applications with a frontend in PHP/HTML and background in Python. This background is based on core API.
This core API integrates all basis functions: 

- Organizations management
- Groups management
- Users management
- API Keys management
- Modules management
- Languages management
- Permissions management
- Countries management
- Configurations management

On core API we integrates all tools for manage the security, cryptography, cache management (with Redis and Memcached), emailing.

This API is compatible with MySQL only at this time.

## Security

The security is implemented with sereval functions:

 - Password are encrypted and stored with [Argon2](https://en.wikipedia.org/wiki/Argon2) algorithm
 - AES256 algorithm is available to encrypt secrets
 - Password hardening is available. If enabled, the following policy is required: minimum length of 12 characters, numbers, upper and lower case letters and special characters are required
 - Email validation is available with list of blocked domains

## Usage

All the code that is not part of the core API must be created and stored in "custom" folder.
