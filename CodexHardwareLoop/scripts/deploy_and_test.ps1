param(
    [string]$Solution   = "${env:GITHUB_WORKSPACE}\CodexHardwareLoop.sln",
    [string]$BranchSha  = "${env:GITHUB_SHA}"
)

Write-Host "=== Building ==="
dotnet build $Solution -c Release -p:ContinuousIntegrationBuild=true
if ($LASTEXITCODE -ne 0) { Throw "Build failed." }

Write-Host "=== Running tests ==="
dotnet test "src/IntegrationTests/IntegrationTests.csproj" -c Release `
    --no-build --results-directory TestResults --logger "trx"
if ($LASTEXITCODE -ne 0) { Throw "Tests failed." }

Write-Host "=== Generating Allure report ==="
allure generate TestResults -o AllureReport --clean
if ($LASTEXITCODE -ne 0) { Throw "Allure CLI failed." }

Write-Host "=== Zipping report ==="
$zip = "allure-$($BranchSha.Substring(0,7)).zip"
Compress-Archive -Path AllureReport\* -DestinationPath $zip -Force

Write-Host "=== Publishing results branch ==="
git switch -C "results/$BranchSha"
git add $zip
git commit -m "Add Allure report for $BranchSha"
git push origin "results/$BranchSha" --force

Write-Host "Done."
