# Deploy SRE Copilot Frontend to AWS Amplify via Git

## Prerequisites
- Git repository (GitHub, GitLab, Bitbucket, or CodeCommit)
- AWS account with Amplify access

## Deployment Steps

### 1. Push Code to Git Repository
```bash
# If not already in a git repo
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### 2. Create Amplify App via Console
1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click "New app" → "Host web app"
3. Choose your Git provider (GitHub/GitLab/Bitbucket/CodeCommit)
4. Authorize AWS Amplify to access your repository
5. Select your repository and branch (usually `main`)

### 3. Configure Build Settings
- **App root directory**: `platform/sre-copilot-frontend`
- Build specification will be auto-detected from `amplify.yml`
- Or manually configure:
  ```yaml
  version: 1
  frontend:
    phases:
      preBuild:
        commands:
          - npm ci
      build:
        commands:
          - npm run build
    artifacts:
      baseDirectory: dist
      files:
        - '**/*'
  ```

### 4. Configure Environment Variables
- In build settings, add environment variable:
- `VITE_API_BASE_URL` = `https://your-backend-api-url.com`

### 5. Deploy
- Click "Save and deploy"
- Amplify will automatically build and deploy
- Future commits to the branch will trigger automatic deployments

## Auto-Deploy Configuration
- **Automatic deployments**: Enabled on push to main branch
- **Build notifications**: Configure via SNS if needed
- **Custom domain**: Add in Domain management section

## Files Created for Deployment
- `amplify.yml` - Build specification (auto-detected)
- `.env.example` - Environment variables template
- Updated `config.ts` - Dynamic API URL configuration

## Environment Variables
- `VITE_API_BASE_URL` - Backend API endpoint URL

## Branch-based Deployments
- **Production**: `main` branch → production environment
- **Staging**: `develop` branch → staging environment (optional)
- Configure different environment variables per branch