# Installs (or updates) sqid-convert on Windows without cloning the repository.
#
# Usage (PowerShell):
#   irm https://raw.githubusercontent.com/djotanas/sqids-cli/main/install.ps1 | iex
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/djotanas/sqids-cli/main/install.ps1))) -Uninstall
#
# Environment:
#   INSTALL_DIR     target directory (default: %LOCALAPPDATA%\Programs\sqid-convert)
#   SQIDS_CLI_REF   branch, tag or commit to install from (default: main)
#   NO_MODIFY_PATH  set to 1 to skip adding INSTALL_DIR to your user PATH
#
# The install directory is added to the user PATH (registry, read by every new
# terminal) and to $env:Path of the current session, so `sqid-convert` works
# right away in the PowerShell window that ran the installer.

& {
  $ErrorActionPreference = 'Stop'
  $uninstall = $args -contains '-Uninstall'

  $installDir = if ($env:INSTALL_DIR) { $env:INSTALL_DIR.TrimEnd('\', '/') } `
                else { Join-Path $env:LOCALAPPDATA 'Programs\sqid-convert' }
  $ref = if ($env:SQIDS_CLI_REF) { $env:SQIDS_CLI_REF } else { 'main' }
  $baseUrl = "https://raw.githubusercontent.com/djotanas/sqids-cli/$ref"
  $configDir = if ($env:XDG_CONFIG_HOME) { Join-Path $env:XDG_CONFIG_HOME 'sqid-convert' } `
               else { Join-Path $HOME '.config\sqid-convert' }

  function Test-SamePath([string]$a, [string]$b) {
    $a.Trim().TrimEnd('\') -ieq $b.Trim().TrimEnd('\')
  }

  # Reads/writes HKCU\Environment\Path without expanding %VARS% stored in it.
  function Get-UserPath {
    $key = Get-Item -Path 'HKCU:\Environment'
    $key.GetValue('Path', '', [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
  }
  function Set-UserPath([string]$value) {
    Set-ItemProperty -Path 'HKCU:\Environment' -Name 'Path' -Value $value -Type ExpandString
    # Setting any user variable through .NET broadcasts WM_SETTINGCHANGE, so
    # Explorer (and terminals started from it) pick up the new PATH.
    [Environment]::SetEnvironmentVariable('SQID_CONVERT_PATH_REFRESH', '1', 'User')
    [Environment]::SetEnvironmentVariable('SQID_CONVERT_PATH_REFRESH', $null, 'User')
  }
  function Split-PathList([string]$value) {
    @($value -split ';' | Where-Object { $_.Trim() -ne '' })
  }

  if ($uninstall) {
    if (Test-Path $installDir) { Remove-Item -Recurse -Force $installDir }
    $entries = Split-PathList (Get-UserPath)
    $kept = @($entries | Where-Object { -not (Test-SamePath $_ $installDir) })
    if ($kept.Count -ne $entries.Count) {
      Set-UserPath ($kept -join ';')
      Write-Host "Removed $installDir from your user PATH."
    }
    $env:Path = (@(Split-PathList $env:Path | Where-Object { -not (Test-SamePath $_ $installDir) })) -join ';'
    Write-Host "sqid-convert removed from $installDir."
    Write-Host "Config kept at $configDir (delete it manually if you want)."
    return
  }

  # Find a real Python 3. "python"/"python3" may be the Microsoft Store stub,
  # so each candidate is actually run.
  $python = $null
  foreach ($candidate in 'py -3', 'python', 'python3') {
    $parts = [string[]]($candidate -split ' ')
    $exe = $parts[0]
    if (-not (Get-Command $exe -CommandType Application -ErrorAction SilentlyContinue)) { continue }
    try {
      $pyArgs = [string[]]($parts[1..($parts.Length)] | Where-Object { $_ }) + @('-c', 'import sys; print(sys.version_info[0])')
      $out = & $exe @pyArgs 2>$null
      if ($LASTEXITCODE -eq 0 -and "$out".Trim() -eq '3') { $python = $candidate; break }
    } catch { }
  }
  if (-not $python) {
    throw 'Python 3 is required but was not found. Install it from https://www.python.org/downloads/ (or "winget install Python.Python.3.12") and run the installer again.'
  }

  # Windows PowerShell 5.1 may default to TLS 1.0, which GitHub rejects.
  [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

  New-Item -ItemType Directory -Force -Path $installDir | Out-Null
  $tmp = Join-Path $installDir 'sqid_convert.py.download'
  Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/sqid_convert.py" -OutFile $tmp
  Move-Item -Force $tmp (Join-Path $installDir 'sqid_convert.py')

  # A .cmd shim works from PowerShell, cmd.exe and Explorer, and is not
  # affected by the PowerShell execution policy.
  $shim = @(
    '@echo off'
    "$python `"%~dp0sqid_convert.py`" %*"
    'exit /b %ERRORLEVEL%'
  ) -join "`r`n"
  Set-Content -Path (Join-Path $installDir 'sqid-convert.cmd') -Value $shim -Encoding Ascii

  Write-Host "sqid-convert installed to $installDir (using '$python')."

  if ($env:NO_MODIFY_PATH -eq '1') {
    if (-not (Split-PathList $env:Path | Where-Object { Test-SamePath $_ $installDir })) {
      Write-Warning "$installDir is not in your PATH (NO_MODIFY_PATH=1, PATH left untouched)."
    }
    return
  }

  $userEntries = Split-PathList (Get-UserPath)
  if (-not ($userEntries | Where-Object { Test-SamePath $_ $installDir })) {
    Set-UserPath ((@($userEntries) + $installDir) -join ';')
    Write-Host "Added $installDir to your user PATH."
  }
  if (-not (Split-PathList $env:Path | Where-Object { Test-SamePath $_ $installDir })) {
    $env:Path = (@(Split-PathList $env:Path) + $installDir) -join ';'
  }
  Write-Host 'Run: sqid-convert'
} @args
