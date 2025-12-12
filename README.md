# end-to-end-MLOPs

![CI/CD Pipeline](https://github.com/reivfts/end-to-end-MLOPs/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/reivfts/end-to-end-MLOPs/actions/workflows/codeql-analysis.yml/badge.svg)
![Docker Publish](https://github.com/reivfts/end-to-end-MLOPs/actions/workflows/docker-publish.yml/badge.svg)

Build and deploy a machine learning pipeline that serves real-time predictions via an API, collects user or system feedback, evaluates model updates, and retrains only when the new model meets performance thresholds. The entire pipeline should run on AWS, optionally using SageMaker for model training and hosting.

## CI/CD

This project uses GitHub Actions for continuous integration and deployment. See [.github/WORKFLOWS.md](.github/WORKFLOWS.md) for detailed documentation on all workflows.

### Quick Overview

- **CI Pipeline**: Runs linting, testing, and Docker builds on every push and PR
- **Security Scanning**: CodeQL analysis and dependency review
- **Docker Publishing**: Automatic image builds and publishing to GitHub Container Registry
- **Deployment**: Manual workflow dispatch for deploying to different environments

For more information, see the [Workflows Documentation](.github/WORKFLOWS.md).
