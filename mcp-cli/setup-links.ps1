
# 1. ?꾨줈?앺듃 猷⑦듃 寃쎈줈 ?뺤쓽 (?꾩옱 ?대뜑??遺紐?
$root = ".."

# 2. ?꾩슂???대뜑 ?앹꽦 (?꾨줈?앺듃 猷⑦듃 湲곗?)
$folders = ".cursor", ".windsurf", ".github"
foreach ($f in $folders) { 
    $path = Join-Path $root $f
    if (!(Test-Path $path)) { mkdir $path -Force } 
}

# 3. 湲곗〈 留곹겕 ?쒓굅 (以묐났 諛⑹?)
$links = ".cursor\rules", ".windsurf\rules", ".clinerules", ".github\copilot-instructions.md", "CLAUDE.md"
foreach ($l in $links) { 
    $targetPath = Join-Path $root $l
    if (Test-Path $targetPath) { Remove-Item $targetPath -Force } 
}

# 4. ?щ낵由?留곹겕 ?앹꽦 
# Target 寃쎈줈??留곹겕 ?뚯씪(.cursor/rules ?????낆옣?먯꽌 ?먮낯(.ai/rules)?쇰줈 媛???곷? 寃쎈줈?낅땲??
New-Item -ItemType SymbolicLink -Path "$root\.cursor\rules" -Target "..\.ai\rules"
New-Item -ItemType SymbolicLink -Path "$root\.windsurf\rules" -Target "..\.ai\rules"
New-Item -ItemType SymbolicLink -Path "$root\.github\copilot-instructions.md" -Target "..\.ai\rules\rules.md"
New-Item -ItemType SymbolicLink -Path "$root\CLAUDE.md" -Target "..\.ai\rules\rules.md"

Write-Host "All AI Tool Rules have been linked to Project Root from mcp-cli!" -ForegroundColor Green