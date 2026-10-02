Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   Personal Signal Deployment Helper    " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check git status
git status

Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Code pushed to GitHub!" -ForegroundColor Green
    Write-Host "Now visit https://dashboard.render.com to connect the repo or view your live build." -ForegroundColor Cyan
} else {
    Write-Host "`n[ACTION REQUIRED] If the repository does not exist on GitHub yet:" -ForegroundColor Yellow
    Write-Host "1. Go to https://github.com/new"
    Write-Host "2. Name: personal-signal-news"
    Write-Host "3. Leave it empty (uncheck README, .gitignore, and license)"
    Write-Host "4. Click 'Create repository'"
    Write-Host "5. Run: git push -u origin main"
}
