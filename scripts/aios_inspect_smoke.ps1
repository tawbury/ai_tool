$ErrorActionPreference = "Stop"

python -m aios inspect
$humanExit = $LASTEXITCODE
if ($humanExit -ne 0 -and $humanExit -ne 1) {
    throw "python -m aios inspect returned unexpected exit code $humanExit"
}

python -m aios inspect --json
$jsonExit = $LASTEXITCODE
if ($jsonExit -ne 0 -and $jsonExit -ne 1) {
    throw "python -m aios inspect --json returned unexpected exit code $jsonExit"
}

Write-Host "aios inspect smoke completed. Human exit=$humanExit JSON exit=$jsonExit"

