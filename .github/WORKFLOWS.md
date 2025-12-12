# GitHub Actions CI/CD Workflows

This document describes the GitHub Actions workflows configured for this repository.

## Workflows Overview

### 1. CI/CD Pipeline (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
- **Lint**: Runs code quality checks
  - `flake8` for Python syntax and style checking
  - `black` for code formatting verification
  
- **Test Services**: Runs tests for each service
  - `test-booking`: Tests for booking service
  - `test-maintenance`: Tests for maintenance service
  - `test-user-management`: Tests for user management service
  - Each includes code coverage reporting
  
- **Docker Build**: Builds Docker images for services
  - Builds booking service image
  - Builds maintenance service image
  - Tags images with commit SHA
  
- **Integration Test**: Runs integration tests
  - Spins up PostgreSQL and Redis services
  - Runs integration test suite

**Usage:**
This workflow runs automatically on every push and pull request. It ensures code quality and functionality before merging.

### 2. Docker Build and Publish (`docker-publish.yml`)

**Triggers:**
- Push to `main` branch
- Version tags (e.g., `v1.0.0`)
- Release publication

**Jobs:**
- Builds Docker images for all services
- Pushes images to GitHub Container Registry (ghcr.io)
- Tags images with:
  - Branch name
  - Commit SHA
  - Version number (from tags)
  - `latest` for main branch

**Usage:**
Automatically publishes Docker images when code is merged to main or when releases are created.

**Image naming:**
```
ghcr.io/reivfts/end-to-end-mlops/booking:latest
ghcr.io/reivfts/end-to-end-mlops/maintenance:latest
```

### 3. CodeQL Security Analysis (`codeql-analysis.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Scheduled: Every Monday at midnight

**Jobs:**
- Analyzes Python code for security vulnerabilities
- Runs CodeQL security-extended queries
- Reports findings to GitHub Security tab

**Usage:**
Automatically scans code for security issues. Check the Security tab in GitHub for results.

### 4. Dependency Review (`dependency-review.yml`)

**Triggers:**
- Pull requests to `main` or `develop` branches

**Jobs:**
- Reviews dependency changes in pull requests
- Checks for known vulnerabilities in dependencies
- Fails on moderate or higher severity vulnerabilities
- Posts summary comment in pull request

**Usage:**
Automatically reviews dependency changes in pull requests to prevent introducing vulnerable dependencies.

### 5. Deploy to Environment (`deploy.yml`)

**Triggers:**
- Manual workflow dispatch (via GitHub Actions UI)

**Inputs:**
- `environment`: Choose development, staging, or production
- `version`: Specify version/tag to deploy (optional, defaults to latest)

**Jobs:**
- Deploys services to specified environment
- Supports version-specific deployments
- Includes deployment status notifications

**Usage:**
1. Go to Actions tab in GitHub
2. Select "Deploy to Environment" workflow
3. Click "Run workflow"
4. Choose environment and version
5. Click "Run workflow" button

### 6. PR Labeler (`labeler.yml`)

**Triggers:**
- Pull request opened, synchronized, or reopened

**Jobs:**
- Automatically labels pull requests based on changed files
- Labels include: booking, maintenance, user-management, gateway, notification, gpa-calculator, docker, documentation, ci/cd, dependencies

**Usage:**
Automatically adds labels to pull requests based on file changes. No manual action required.

## Setup Instructions

### 1. Enable GitHub Actions
GitHub Actions should be enabled by default. Check repository Settings > Actions > General.

### 2. Configure Secrets (Optional)

For deployment workflows, you may need to add secrets:
1. Go to Settings > Secrets and variables > Actions
2. Add repository secrets as needed:
   - Cloud provider credentials (AWS, Azure, GCP)
   - Container registry credentials
   - Notification service tokens

### 3. Enable GitHub Container Registry

To push Docker images:
1. Images will be pushed to GitHub Container Registry automatically
2. No additional setup required
3. Images are private by default

### 4. Branch Protection Rules (Recommended)

To enforce CI checks before merging:
1. Go to Settings > Branches
2. Add rule for `main` branch:
   - Require status checks before merging
   - Select: "Lint Python Code", "Test Booking Service", etc.
   - Require branches to be up to date

## Workflow Status Badges

Add these badges to your README.md:

```markdown
![CI/CD Pipeline](https://github.com/reivfts/end-to-end-MLOPs/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/reivfts/end-to-end-MLOPs/actions/workflows/codeql-analysis.yml/badge.svg)
```

## Customization

### Adding New Services

To add CI/CD for a new service:

1. Edit `.github/workflows/ci.yml`:
```yaml
test-new-service:
  name: Test New Service
  runs-on: ubuntu-latest
  needs: lint
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - run: |
        cd new-service
        pip install -r requirements.txt
        pytest
```

2. Edit `.github/workflows/docker-publish.yml`:
```yaml
strategy:
  matrix:
    service:
      - name: new-service
        context: ./new-service
        dockerfile: ./new-service/Dockerfile
```

3. Edit `.github/labeler.yml`:
```yaml
new-service:
  - new-service/**/*
```

### Modifying Linting Rules

Edit `.github/workflows/ci.yml`:
```yaml
- name: Run flake8
  run: |
    flake8 . --max-line-length=100 --exclude=venv,env
```

### Changing Test Commands

Edit the test job in `.github/workflows/ci.yml`:
```yaml
- name: Run tests
  run: |
    cd service-name
    pytest -v --cov=. --cov-report=html
```

## Troubleshooting

### Workflow Not Running
- Check if GitHub Actions is enabled in repository settings
- Verify branch name matches workflow triggers
- Check workflow syntax with `yamllint`

### Docker Build Fails
- Ensure Dockerfile exists in service directory
- Check if all dependencies are specified in requirements.txt
- Verify base image is available

### Tests Failing
- Run tests locally first: `pytest`
- Check if all dependencies are installed
- Verify test database/services are available

### Permission Errors
- Ensure repository has appropriate permissions for GitHub Actions
- Check if GITHUB_TOKEN has required scopes
- For Container Registry, ensure packages:write permission

## Best Practices

1. **Always run CI locally before pushing:**
   ```bash
   flake8 .
   black --check .
   pytest
   ```

2. **Use specific versions in dependencies:**
   - Pin Python package versions in requirements.txt
   - Use specific action versions (e.g., `@v4` not `@latest`)

3. **Keep workflows fast:**
   - Use caching for dependencies
   - Run tests in parallel
   - Use matrix builds for multiple versions

4. **Security:**
   - Never commit secrets to repository
   - Use GitHub Secrets for sensitive data
   - Review CodeQL findings regularly

5. **Documentation:**
   - Update this document when adding new workflows
   - Add comments in workflow files
   - Document required secrets and configurations

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build and Push Action](https://github.com/docker/build-push-action)
- [CodeQL Documentation](https://codeql.github.com/)
- [Dependency Review Action](https://github.com/actions/dependency-review-action)
