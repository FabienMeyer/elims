[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [Alias("LeafIssue")]
    [string]$Issue,

    [Parameter(Mandatory = $true)]
    [string]$Prd,

    [Parameter(Mandatory = $true)]
    [string]$Specification,

    [Parameter(Mandatory = $true)]
    [string]$ArchitectureResult,

    [ValidateRange(20, 1000)]
    [int]$MaxTurns = 200,

    [string]$LogDirectory = "artifacts/afk-implementation"
)

$ErrorActionPreference = "Stop"

function Resolve-RequiredFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label does not exist or is not a file: $Path"
    }

    return (Resolve-Path -LiteralPath $Path).Path
}

function Resolve-EligibleIssue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$IssueReference
    )

    $requiredLabel = "rdy-to-implement"

    if (Test-Path -LiteralPath $IssueReference -PathType Leaf) {
        $resolvedPath = (Resolve-Path -LiteralPath $IssueReference).Path
        $content = Get-Content -LiteralPath $resolvedPath -Raw
        $metadataMatch = [regex]::Match($content, '(?im)^\s*labels\s*:\s*\[(?<labels>[^\]\r\n]*)\]\s*$')
        $localLabels = if ($metadataMatch.Success) {
            @($metadataMatch.Groups['labels'].Value -split ',' | ForEach-Object { $_.Trim().Trim('"').Trim("'") })
        } else {
            @()
        }

        if ($requiredLabel -cnotin $localLabels) {
            throw "Local issue is not eligible: metadata must contain labels: [$requiredLabel]."
        }

        return $resolvedPath
    }

    $ghCommand = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $ghCommand) {
        throw "The issue is not a local file and GitHub CLI is unavailable. Install 'gh' or provide a labeled local issue file."
    }

    $issueJson = & $ghCommand.Source issue view $IssueReference --json number,title,state,labels,url
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read GitHub issue: $IssueReference"
    }

    $issueData = $issueJson | ConvertFrom-Json
    if ($issueData.state -ne "OPEN") {
        throw "GitHub issue #$($issueData.number) is not open."
    }

    $labelNames = @($issueData.labels | ForEach-Object { $_.name })
    if ($requiredLabel -cnotin $labelNames) {
        throw "GitHub issue #$($issueData.number) does not have the exact '$requiredLabel' label."
    }

    return $issueData.url
}

$claudeCommand = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claudeCommand) {
    $nativeInstall = Join-Path $env:USERPROFILE ".local/bin/claude.exe"
    $claudeCommand = Get-Command $nativeInstall -ErrorAction SilentlyContinue
}
if (-not $claudeCommand) {
    throw "Install Claude Code or add its executable to PATH."
}

$resolvedIssue = Resolve-EligibleIssue -IssueReference $Issue
$resolvedPrd = Resolve-RequiredFile -Path $Prd -Label "PRD"
$resolvedSpecification = Resolve-RequiredFile -Path $Specification -Label "Specification"
$resolvedArchitecture = Resolve-RequiredFile -Path $ArchitectureResult -Label "Architecture result"

$resolvedLogDirectory = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $LogDirectory))
New-Item -ItemType Directory -Path $resolvedLogDirectory -Force | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$logPath = Join-Path $resolvedLogDirectory "implementation-$timestamp.jsonl"

$prompt = @"
/implementation-orchestrator "$resolvedIssue" "$resolvedPrd" "$resolvedSpecification" "$resolvedArchitecture"

Run the complete workflow autonomously while the user is away.

Complete Chapter 5 through TDD, Green implementation, refactoring, and independent code review. Follow the Chapter 5 correction loops. Stop at implementation-complete when code review passes, or implementation-blocked when an entry gate or required decision prevents progress.

Preserve unrelated work. Do not merge, push, deploy, publish, create or close external issues, change secrets, access production, or bypass a failed or blocked gate. Record the final bidirectional traceability matrix and all phase verdicts in the final response.

Before any implementation phase, independently confirm that the exact issue still has the rdy-to-implement label. If the label is absent or cannot be verified, return implementation-blocked without changing code.
"@

Write-Host "Starting AFK implementation workflow."
Write-Host "Streaming log: $logPath"
Write-Host "Maximum turns: $MaxTurns"

& $claudeCommand.Source `
    -p `
    --permission-mode auto `
    --max-turns $MaxTurns `
    --output-format stream-json `
    --verbose `
    $prompt | Tee-Object -FilePath $logPath

$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    throw "Claude Code exited with code $exitCode. Review $logPath."
}

Write-Host "AFK implementation workflow finished. Review $logPath."
