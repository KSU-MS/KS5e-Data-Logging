# Define variables
$pythonVersion = "3.8.0"
$repoUrl = "https://github.com/KSU-MS/KS5e-Data-Logging.git"
$repoDirectoryName = "logging"
$repoDirectory = Join-Path $env:USERPROFILE "Documents\$repoDirectoryName"
$requirementsFile = "requirements.txt"

# Function to install Python
function InstallPython {
    $pythonInstallerUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    
    # Download Python installer
    Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $pythonInstaller

    # Install Python silently
    Start-Process -Wait -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1"

    # Clean up
    Remove-Item -Path $pythonInstaller -Force
}

# Function to clone the repository and install requirements
function CloneRepoAndInstallPackages {
    # Clone repository
    git clone $repoUrl $repoDirectory

    # Navigate to repository directory
    cd $repoDirectory

    # Install Python packages
    python -m pip install -r $requirementsFile
}

# Check if Python is installed
if (-not (Test-Path (Join-Path $env:ProgramFiles "Python" $pythonVersion))) {
    InstallPython
}

# Check if Git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git is not installed. Please install Git and run the script again."
    exit
}

# Clone repository and install packages
CloneRepoAndInstallPackages
