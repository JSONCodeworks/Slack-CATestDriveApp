# Troubleshooting Guide

## Python 3.14 Compatibility Issue

### Problem
When installing requirements on Python 3.14, you see an error like:
```
error C2660: '_PyLong_AsByteArray': function does not take 5 arguments
Building wheel for pyodbc (pyproject.toml) ... error
```

### Root Cause
Python 3.14 introduced breaking changes to internal C API functions that pyodbc uses. The pyodbc package needs to be updated to support these changes.

### Solutions (Choose One)

#### Solution 1: Use Python 3.13 (Recommended)
The easiest and most reliable solution is to use Python 3.13 or earlier.

**Windows:**
1. Download Python 3.13 from [python.org](https://www.python.org/downloads/)
2. Install it
3. Create a virtual environment:
   ```cmd
   py -3.13 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

**macOS (using pyenv):**
```bash
brew install pyenv
pyenv install 3.13.0
pyenv local 3.13.0
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Linux (using pyenv):**
```bash
curl https://pyenv.run | bash
pyenv install 3.13.0
pyenv local 3.13.0
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Solution 2: Use Pre-built Wheels
Try installing a pre-compiled version of pyodbc:

```bash
pip install --only-binary :all: pyodbc
```

If this doesn't work, try:
```bash
pip install --only-binary :all: pyodbc==5.2.0
```

#### Solution 3: Use Older pyodbc Version
Install an older version that has pre-built wheels:

```bash
pip install pyodbc==4.0.39
pip install slack-bolt==1.18.0 slack-sdk==3.23.0 python-dotenv==1.0.0 requests==2.31.0
```

Note: Using an older pyodbc version should work fine for this application.

#### Solution 4: Wait for Update
Monitor the pyodbc GitHub repository for Python 3.14 support:
- https://github.com/mkleehammer/pyodbc

---

## ODBC Driver Issues

### Problem: "Driver not found"
```
pyodbc.Error: ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 17 for SQL Server'")
```

### Solutions

**Verify Installation:**
```bash
odbcinst -q -d
```

You should see `ODBC Driver 17 for SQL Server` in the list.

**Linux - Install/Reinstall:**
```bash
# Ubuntu/Debian
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | \
  sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Red Hat/CentOS
sudo curl -o /etc/yum.repos.d/mssql-release.repo https://packages.microsoft.com/config/rhel/8/prod.repo
sudo yum remove unixODBC-utf16 unixODBC-utf16-devel
sudo ACCEPT_EULA=Y yum install -y msodbcsql17
```

**macOS:**
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17
```

**Windows:**
Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

---

## Database Connection Issues

### Problem: Connection timeout or authentication failure

**Test the connection:**
```bash
python test_db.py
```

**Common Issues:**

1. **Firewall blocking connection**
   - Verify SQL Server allows connections from your IP
   - Check that port 1433 is open

2. **Invalid credentials**
   - Double-check username and password in `app.py`
   - Verify you have permission to access the database

3. **Network issues**
   - Try pinging the server:
     ```bash
     ping public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com
     ```
   - Test with SQL client (Azure Data Studio, DBeaver)

4. **Database doesn't exist**
   - Verify the database name is correct
   - Check if table `automation_epod_templates` exists

---

## Slack Connection Issues

### Problem: App doesn't respond to /testdrive command

**Checklist:**

1. **Verify Socket Mode is enabled**
   - Go to Slack API dashboard → Your App → Socket Mode
   - Should be ON

2. **Check tokens in .env**
   ```bash
   cat .env
   ```
   - `SLACK_BOT_TOKEN` should start with `xoxb-`
   - `SLACK_APP_TOKEN` should start with `xapp-`

3. **Verify app is running**
   - You should see connection messages in console:
     ```
     ⚡️ Bolt app is running!
     ```

4. **Check permissions**
   - Go to OAuth & Permissions
   - Verify these scopes are added:
     - `chat:write`
     - `commands`
     - `users:read`
     - `users:read.email`

5. **Reinstall app to workspace**
   - Sometimes needed after permission changes
   - Go to "Install App" and click "Reinstall to Workspace"

6. **Check slash command is created**
   - Go to "Slash Commands"
   - Verify `/testdrive` exists

### Problem: Modal doesn't open

Check console for errors. Common issues:
- Invalid trigger_id (expires after 3 seconds)
- Malformed view JSON
- Permission issues

---

## Import Errors

### Problem: ModuleNotFoundError

```bash
ModuleNotFoundError: No module named 'slack_bolt'
```

**Solution:**
Ensure you've installed requirements and activated virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate   # Windows

# Install requirements
pip install -r requirements.txt
```

---

## API Submission Issues

### Problem: API returns error

**Check:**
1. Verify API endpoint is accessible:
   ```bash
   curl https://pssrequest.cyberarklab.com/PSSAPI/API/PSSRequest
   ```

2. Check request format in console logs

3. Verify request_key is correct

4. Check if API requires additional authentication

---

## Performance Issues

### Problem: Slow template loading

The app queries SQL Server for templates on every form open. To improve:

1. **Add caching** - Cache templates for 5-10 minutes
2. **Reduce query frequency** - Load templates on app start
3. **Optimize query** - Add index on `template_visable` column

---

## Windows-Specific Issues

### Problem: Visual Studio Build Tools required

If you see errors about missing compiler:

**Solution:**
1. Download Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
2. Select "Desktop development with C++"
3. Install and restart
4. Try `pip install -r requirements.txt` again

Or use pre-built wheels (see Solution 2 above).

---

## Getting More Help

1. **Check logs:**
   ```bash
   python app.py
   ```
   Watch for errors in console output

2. **Enable debug mode:**
   Add to app.py:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Test components individually:**
   - Database: `python test_db.py`
   - Slack connection: Check console when starting app
   - API: Use curl or Postman to test endpoint

4. **Check Slack API logs:**
   - Go to Slack API dashboard
   - Your App → Event Subscriptions
   - Review recent events and errors
