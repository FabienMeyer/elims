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

    # Work branch for the leaf: <type>/<issue-number>-<scope>-<short-slug>.
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^(feat|fix|refactor|docs|test|chore|security|perf|migration)/\d+-[a-z0-9]+(-[a-z0-9]+)*$")]
    [string]$Branch,

    # Revision a new work branch starts from.
    [string]$BaseRef = "origin/main",

    # Directory that holds one worktree per leaf. Default: <repository>-worktrees next to the repository.
    [string]$WorktreeRoot,

    [ValidateRange(20, 1000)]
    [int]$MaxTurns = 200,

    [string]$LogDirectory = "artifacts/afk-implementation",

    # Also run 'npm ci' for the frontend in the worktree.
    [switch]$InstallFrontend,

    # Create or reuse the worktree and install dependencies, then stop before starting Claude Code.
    [switch]$PrepareOnly
)

$ErrorActionPreference = "Stop"

# A simple function, so that git options such as -C and -b pass through unchanged in $args.
function Invoke-Git {
    $output = & git @args
    if ($LASTEXITCODE -ne 0) {
        throw "git $($args -join ' ') failed with exit code $LASTEXITCODE."
    }
    return $output
}

function Test-GitRef {
    param([Parameter(Mandatory = $true)][string]$Ref)

    & git show-ref --verify --quiet $Ref
    return ($LASTEXITCODE -eq 0)
}

function Resolve-ArtifactPath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label does not exist or is not a file: $Path"
    }
    $fullPath = (Resolve-Path -LiteralPath $Path).Path
    $rootWithSeparator = $RepositoryRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $fullPath.StartsWith($rootWithSeparator, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label must be inside the repository: $fullPath"
    }
    return $fullPath.Substring($rootWithSeparator.Length).Replace('\', '/')
}

function Resolve-EligibleIssue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$IssueReference
    )

    $requiredLabel = "rdy-to-implement"

    if (Test-Path -LiteralPath $IssueReference -PathType Leaf) {
        throw "A local issue file is not evidence of '$requiredLabel'. Pass the GitHub issue number or URL."
    }

    $ghCommand = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $ghCommand) {
        throw "GitHub CLI is unavailable. Install 'gh' to verify the '$requiredLabel' label on the GitHub issue."
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

    return $issueData
}

function Resolve-ClaudeCommand {
    $command = Get-Command claude -ErrorAction SilentlyContinue
    if (-not $command) {
        $nativeInstall = Join-Path $env:USERPROFILE ".local/bin/claude.exe"
        $command = Get-Command $nativeInstall -ErrorAction SilentlyContinue
    }
    if (-not $command) {
        throw "Install Claude Code or add its executable to PATH."
    }
    return $command
}

function New-LeafWorktree {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$BranchName,
        [Parameter(Mandatory = $true)][string]$StartCommit
    )

    if (Test-Path -LiteralPath $Path) {
        $currentBranch = & git -C $Path rev-parse --abbrev-ref HEAD
        if ($LASTEXITCODE -ne 0 -or $currentBranch -ne $BranchName) {
            throw "'$Path' exists but is not a worktree on branch '$BranchName'. Remove it or choose another -WorktreeRoot."
        }
        Write-Host "Reusing worktree $Path on branch $BranchName."
        return
    }

    if (Test-GitRef "refs/heads/$BranchName") {
        Write-Host "Adding worktree $Path for existing branch $BranchName."
        Invoke-Git worktree add $Path $BranchName | Out-Null
    }
    else {
        Write-Host "Creating branch $BranchName at $StartCommit in worktree $Path."
        Invoke-Git worktree add -b $BranchName $Path $StartCommit | Out-Null
    }
}

$repositoryRoot = [System.IO.Path]::GetFullPath(((Invoke-Git rev-parse --show-toplevel) | Select-Object -First 1))
$issueData = Resolve-EligibleIssue -IssueReference $Issue

$issueNumber = [regex]::Match($Branch, '/(\d+)-').Groups[1].Value
if ($issueNumber -ne [string]$issueData.number) {
    throw "Branch '$Branch' names issue $issueNumber, but the GitHub issue is #$($issueData.number)."
}

$artifacts = [ordered]@{
    "PRD"                 = Resolve-ArtifactPath -Path $Prd -Label "PRD" -RepositoryRoot $repositoryRoot
    "Specification"       = Resolve-ArtifactPath -Path $Specification -Label "Specification" -RepositoryRoot $repositoryRoot
    "Architecture result" = Resolve-ArtifactPath -Path $ArchitectureResult -Label "Architecture result" -RepositoryRoot $repositoryRoot
}

if ($BaseRef -match '^origin/(.+)$') {
    Invoke-Git fetch --quiet origin $Matches[1] | Out-Null
}
$startCommit = (Invoke-Git rev-parse --verify "$BaseRef^{commit}") | Select-Object -First 1

if (-not $WorktreeRoot) {
    $WorktreeRoot = Join-Path (Split-Path -Parent $repositoryRoot) ((Split-Path -Leaf $repositoryRoot) + "-worktrees")
}
$worktreePath = Join-Path ([System.IO.Path]::GetFullPath($WorktreeRoot)) ($Branch -replace '/', '-')

$pendingClaudeChanges = Invoke-Git -C $repositoryRoot status --porcelain -- .claude
if ($pendingClaudeChanges) {
    Write-Warning "The main checkout has uncommitted changes under .claude. The worktree uses only the skills and hooks committed on '$Branch'."
}

# Check the committed content before creating anything, so that a failed check leaves no worktree or branch.
if (Test-GitRef "refs/heads/$Branch") { $checkedRevision = $Branch } else { $checkedRevision = $startCommit }
$requiredFiles = @(
    ".claude/settings.json",
    ".claude/skills/05-implementation-orchestrator/SKILL.md",
    ".claude/skills/shared/hooks/guard_gated_mutations.py"
)
function Test-CommittedFile {
    param([string]$Revision, [string]$RelativePath)

    # ls-tree prints nothing for a missing path and writes no stderr, which is safe in Windows PowerShell 5.1.
    $listed = Invoke-Git ls-tree --name-only $Revision -- $RelativePath
    return [bool]$listed
}
foreach ($required in $requiredFiles) {
    if (-not (Test-CommittedFile $checkedRevision $required)) {
        throw "'$required' is not committed at '$checkedRevision'. Commit the ELIMS skills and gate hook before an AFK run."
    }
}
foreach ($entry in $artifacts.GetEnumerator()) {
    if (-not (Test-CommittedFile $checkedRevision $entry.Value)) {
        throw "$($entry.Key) '$($entry.Value)' is not committed at '$checkedRevision'. Approved artifacts must be committed at the base."
    }
}

New-Item -ItemType Directory -Path (Split-Path -Parent $worktreePath) -Force | Out-Null
New-LeafWorktree -Path $worktreePath -BranchName $Branch -StartCommit $startCommit

$anchorBase = (Invoke-Git -C $worktreePath merge-base HEAD $startCommit) | Select-Object -First 1

$unrelatedChanges = Invoke-Git -C $worktreePath status --porcelain
if ($unrelatedChanges) {
    Write-Warning "The worktree already has uncommitted changes. The orchestrator treats them as earlier work on this leaf."
}

$resolvedLogDirectory = [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot $LogDirectory))
New-Item -ItemType Directory -Path $resolvedLogDirectory -Force | Out-Null

Push-Location $worktreePath
try {
    Write-Host "Installing locked Python dependencies in the worktree."
    & uv sync --locked --all-packages --all-extras --group dev --group quality
    if ($LASTEXITCODE -ne 0) {
        throw "uv sync failed in $worktreePath."
    }
    if ($InstallFrontend) {
        Write-Host "Installing frontend dependencies in the worktree."
        & npm ci --prefix frontend
        if ($LASTEXITCODE -ne 0) {
            throw "npm ci failed in $worktreePath."
        }
    }

    Write-Host "Worktree:          $worktreePath"
    Write-Host "Branch:            $Branch"
    Write-Host "Review-anchor base: $anchorBase"

    if ($PrepareOnly) {
        Write-Host "Worktree prepared. Claude Code was not started (-PrepareOnly)."
        return
    }

    $claudeCommand = Resolve-ClaudeCommand
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $logPath = Join-Path $resolvedLogDirectory "implementation-$($issueData.number)-$timestamp.jsonl"

    $prompt = @"
/implementation-orchestrator "$($issueData.url)" "$($artifacts['PRD'])" "$($artifacts['Specification'])" "$($artifacts['Architecture result'])"

Run the complete workflow autonomously while the user is away.

You are in the dedicated Git worktree for this leaf on branch '$Branch'. Use commit $anchorBase as the review-anchor base and record it as base_commit in the traceability matrix. Do not switch branches or edit files outside this worktree.

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

    Write-Host "AFK implementation workflow finished. Review $logPath and the worktree $worktreePath."
}
finally {
    Pop-Location
}
