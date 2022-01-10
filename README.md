# Core-API

![pylint Score](https://github.com/FirstCloud-Hosting/core-api/actions/workflows/pylint.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/FirstCloud-Hosting/core-api/badge.svg?branch=main)](https://coveralls.io/github/FirstCloud-Hosting/core-api?branch=main)
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

On core API we integrates all tools for manage the security, cryptography, cache management (with Memcached only at this time), emailing, 

This API is compatible with MySQL only at this time.

## Usage

All the code that is not part of the core API mustbe created and stored in "custom" folder.
