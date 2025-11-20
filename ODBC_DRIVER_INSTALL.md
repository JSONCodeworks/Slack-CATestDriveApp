# ODBC Driver Installation Guide

## The Error You're Seeing

```
Error fetching templates: ('IM002', '[IM002] [Microsoft][ODBC Driver Manager] 
Data source name not found and no default driver specified (0) (SQLDriverConnect)')
```

This means the **ODBC Driver for SQL Server is not installed** on your system.

---

## Windows Installation (EASIEST)

### Option 1: Direct Download (Recommended)

1. **Download ODBC Driver 18:**
   - Go to: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
   - Click "Download ODBC Driver 18 for SQL Server"
   - Choose: `msodbcsql_18.x.x.x_x64.msi` (64-bit)

2. **Run the installer:**
   - Double-click the downloaded .msi file
   - Click "Next" through the installation wizard
   - Accept the license agreement
   - Click "Install"

3. **Verify installation:**
   ```cmd
   odbcinst -q -d
   ```
   You should see `ODBC Driver 18 for SQL Server` or `ODBC Driver 17 for SQL Server` in the list

4. **Try your app again:**
   ```cmd
   python app.py
   ```

### Option 2: Using winget (Windows 10/11)

```cmd
winget install Microsoft.ODBC.18
```

---

## macOS Installation

### Using Homebrew (Recommended)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Microsoft's tap
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release

# Update brew
brew update

# Install ODBC Driver 18
HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql18

# Or install ODBC Driver 17
HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql17
```

### Verify Installation

```bash
odbcinst -j
```

---

## Linux Installation

### Ubuntu/Debian

```bash
# Add Microsoft package repository
curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc

# For Ubuntu 22.04
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

# For Ubuntu 20.04, use:
# curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Update package list
sudo apt-get update

# Install ODBC Driver 18
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Or install ODBC Driver 17
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Install unixODBC if not present
sudo apt-get install -y unixodbc-dev
```

### Red Hat/CentOS/Fedora

```bash
# Add Microsoft repository
sudo curl -o /etc/yum.repos.d/mssql-release.repo https://packages.microsoft.com/config/rhel/8/prod.repo

# Remove conflicting packages
sudo yum remove unixODBC-utf16 unixODBC-utf16-devel

# Install ODBC Driver 18
sudo ACCEPT_EULA=Y yum install -y msodbcsql18

# Or install ODBC Driver 17
sudo ACCEPT_EULA=Y yum install -y msodbcsql17

# Install unixODBC if not present
sudo yum install -y unixODBC-devel
```

### Verify Installation

```bash
odbcinst -q -d
```

You should see something like:
```
[ODBC Driver 18 for SQL Server]
[ODBC Driver 17 for SQL Server]
```

---

## Automated Installation Script

I've created an installation script for Linux/macOS:

```bash
chmod +x install_odbc_driver.sh
./install_odbc_driver.sh
```

---

## Testing Your Installation

### Step 1: Check Available Drivers

**Windows:**
```cmd
odbcinst -q -d
```

**Linux/macOS:**
```bash
odbcinst -q -d
```

You should see one of these:
- `ODBC Driver 18 for SQL Server`
- `ODBC Driver 17 for SQL Server`
- `ODBC Driver 13 for SQL Server`

### Step 2: Test Database Connection

Run the test script:
```cmd
python test_db.py
```

Expected output:
```
Available ODBC drivers: ['ODBC Driver 18 for SQL Server', ...]
Using ODBC driver: ODBC Driver 18 for SQL Server
✓ Successfully connected to SQL Server
```

### Step 3: Run Your App

```cmd
python app.py
```

The app now detects available drivers automatically!

---

## Troubleshooting

### "odbcinst: command not found"

**Windows:** odbcinst should be available after installing ODBC driver

**Linux/macOS:** Install unixODBC:
```bash
# Ubuntu/Debian
sudo apt-get install unixodbc

# macOS
brew install unixodbc

# Red Hat/CentOS
sudo yum install unixODBC
```

### Driver installed but still getting errors

1. **Restart your terminal/command prompt**
2. **Check if driver name matches:**
   ```python
   import pyodbc
   print(pyodbc.drivers())
   ```

3. **Try a different driver version:**
   - If 18 doesn't work, try 17
   - If 17 doesn't work, try 13

### Permission errors on Linux

Some installations require sudo:
```bash
sudo python3 app.py
```

Or fix permissions:
```bash
sudo chmod -R 755 /opt/microsoft/msodbcsql*
```

### macOS: "Can't open lib"

Ensure you accepted the EULA:
```bash
HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew reinstall msodbcsql18
```

---

## What Changed in the App

The app now:
1. ✅ **Auto-detects available ODBC drivers** (tries 18, 17, 13, 11, etc.)
2. ✅ **Shows helpful error messages** with installation links
3. ✅ **Verifies driver on startup** before connecting to Slack
4. ✅ **Provides clear console output** showing which driver is being used

---

## Quick Reference

### Download Links

- **Windows:** https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- **macOS:** `brew install msodbcsql18`
- **Ubuntu/Debian:** `sudo apt-get install msodbcsql18`
- **Red Hat/CentOS:** `sudo yum install msodbcsql18`

### Verification Commands

```bash
# List installed ODBC drivers
odbcinst -q -d

# Check ODBC configuration
odbcinst -j

# Test with Python
python -c "import pyodbc; print(pyodbc.drivers())"

# Test database connection
python test_db.py

# Run the app
python app.py
```

---

## Still Having Issues?

1. **Check the main README:** Installation prerequisites section
2. **Review TROUBLESHOOTING.md:** ODBC Driver Issues section
3. **Verify Python version:** Should be 3.8-3.13
4. **Check network access:** Can you reach the SQL Server?

---

## Success!

Once you see this message when running `python app.py`:
```
✓ ODBC Driver detected: ODBC Driver 18 for SQL Server
```

Your database connection is ready! 🎉
