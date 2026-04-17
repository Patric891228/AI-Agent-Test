New-Item -ItemType Directory -Force -Path build | Out-Null

$venvPythonPath = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"

if (Test-Path $venvPythonPath) {
    & $venvPythonPath -m PyInstaller --noconfirm AI-Agent-Test.spec
    exit $LASTEXITCODE
}

pyinstaller --noconfirm AI-Agent-Test.spec
