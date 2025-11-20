# ODBC Driver Installation Script for Windows
# Run as Administrator if needed

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ODBC Driver Installation Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Note: Some operations may require administrator privileges" -ForegroundColor Yellow
    Write-Host ""
}

# Check for existing ODBC drivers
Write-Host "Checking for existing ODBC drivers..." -ForegroundColor White
$drivers = Get-OdbcDriver | Where-Object { $_.Name -like "*SQL Server*" }

if ($drivers) {
    Write-Host ""
    Write-Host "Found existing SQL Server ODBC drivers:" -ForegroundColor Green
    foreach ($driver in $drivers) {
        Write-Host "  - $($driver.Name)" -ForegroundColor Green
    }
    Write-Host ""
    $response = Read-Host "Driver already installed. Reinstall anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Skipping installation." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Your app should work now. Try running:" -ForegroundColor Green
        Write-Host "  python app.py" -ForegroundColor White
        exit 0
    }
}

Write-Host ""
Write-Host "Attempting to install ODBC Driver 18 for SQL Server..." -ForegroundColor White
Write-Host ""

# Try using winget (Windows 10/11)
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Using winget to install..." -ForegroundColor White
    
    try {
        winget install Microsoft.ODBC.18 --accept-package-agreements --accept-source-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "Installation successful!" -ForegroundColor Green
            $installed = $true
        }
    } catch {
        Write-Host "winget installation failed" -ForegroundColor Yellow
    }
}

# If winget didn't work, try Chocolatey
if (-not $installed -and (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Trying Chocolatey..." -ForegroundColor White
    
    try {
        choco install sqlserver-odbcdriver -y
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "Installation successful!" -ForegroundColor Green
            $installed = $true
        }
    } catch {
        Write-Host "Chocolatey installation failed" -ForegroundColor Yellow
    }
}

# Manual download instructions
if (-not $installed) {
    Write-Host ""
    Write-Host "=========================================="
    Write-Host "Manual Installation Required"
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "Automated installation methods not available." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please follow these steps:" -ForegroundColor White
    Write-Host ""
    Write-Host "1. Open this URL in your browser:" -ForegroundColor White
    Write-Host "   https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Download: ODBC Driver 18 for SQL Server (64-bit)" -ForegroundColor White
    Write-Host "   File: msodbcsql_XX.X.X.X_x64.msi" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Run the downloaded installer" -ForegroundColor White
    Write-Host ""
    Write-Host "4. Follow the installation wizard" -ForegroundColor White
    Write-Host ""
    Write-Host "5. After installation, run this script again to verify" -ForegroundColor White
    Write-Host ""
    
    # Ask if user wants to open the download page
    $response = Read-Host "Open download page in browser now? (Y/n)"
    if ($response -ne "n" -and $response -ne "N") {
        Start-Process "https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server"
    }
    
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Verifying Installation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$drivers = Get-OdbcDriver | Where-Object { $_.Name -like "*SQL Server*" }

if ($drivers) {
    Write-Host "Available SQL Server ODBC drivers:" -ForegroundColor Green
    foreach ($driver in $drivers) {
        Write-Host "  - $($driver.Name)" -ForegroundColor Green
    }
    Write-Host ""
    Write-Host "Installation verified successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run your application:" -ForegroundColor White
    Write-Host "  python app.py" -ForegroundColor Cyan
} else {
    Write-Host "Could not verify ODBC driver installation" -ForegroundColor Red
    Write-Host "Please try manual installation" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
