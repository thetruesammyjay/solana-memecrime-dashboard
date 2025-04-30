#!/bin/bash
set -e

# Configuration
FRONTEND_DIR="../frontend"
BUILD_DIR="dist"
DEPLOY_BRANCH="gh-pages"

echo "🚀 Starting frontend deployment..."

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
  echo "❌ Error: Uncommitted changes detected"
  exit 1
fi

# Install dependencies and build
cd "$FRONTEND_DIR"
echo "📦 Installing dependencies..."
npm install
echo "🔨 Building production version..."
npm run build

# Create temporary deploy directory
DEPLOY_DIR="../../deploy_temp"
mkdir -p "$DEPLOY_DIR"
cp -R "$BUILD_DIR"/* "$DEPLOY_DIR"

# Switch to deploy branch
cd ..
echo "🌿 Switching to deploy branch..."
git checkout "$DEPLOY_BRANCH" || git checkout --orphan "$DEPLOY_BRANCH"

# Clean existing files except .git
echo "🧹 Cleaning old files..."
find . -maxdepth 1 ! -name '.git' ! -name '.' -exec rm -rf {} +

# Move built files
echo "📂 Moving built files..."
mv "$DEPLOY_DIR"/* .
rm -rf "$DEPLOY_DIR"

# Commit and push
echo "📦 Committing changes..."
git add .
git commit -m "Deploy frontend $(date +'%Y-%m-%d %H:%M:%S')"
echo "🚀 Pushing to remote..."
git push origin "$DEPLOY_BRANCH"

# Switch back
git checkout main
echo "✅ Deployment complete!"