# Network Connectivity Issue - Troubleshooting Guide

## Your Error

```
Login timeout expired
Named Pipes Provider: Could not open a connection to SQL Server
Server is not found or not accessible
```

This means your computer **cannot reach the SQL Server** over the network.

---

## 🔍 Step 1: Pull Updated Code & Test

I've updated the test script to diagnose the exact problem.

```cmd
cd C:\path\to\Slack-CATestDriveApp
git pull origin main
python test_db.py
```

The new test will check:
1. ✅ DNS resolution (can your computer find the server name?)
2. ✅ Port connectivity (can you reach port 1433?)
3. ✅ SQL authentication (can you log in?)

---

## 🎯 Most Likely Causes

### 1. VPN Required ⭐ MOST COMMON

Many corporate SQL Servers require VPN access.

**Check:**
- Are you on your company VPN?
- Does this server require VPN to access?

**Solution:**
```
1. Connect to your company VPN
2. Run: python test_db.py
3. Should now connect successfully
```

### 2. Firewall Blocking Connection

Your firewall or the server's firewall may be blocking port 1433.

**Check Windows Firewall:**
```cmd
# Run PowerShell as Administrator
Test-NetConnection -ComputerName public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com -Port 1433
```

**Expected if working:**
```
TcpTestSucceeded : True
```

**If blocked:**
```
TcpTestSucceeded : False
WARNING: TCP connect to (IP:1433) failed
```

**Solution:**
- Allow outbound connections to port 1433
- Contact your IT department
- Or connect to VPN

### 3. IP Address Not Whitelisted

AWS RDS instances (like this one) often restrict connections to specific IP addresses.

**Check:**
- Contact the database administrator
- Ask if your IP needs to be whitelisted
- Provide your current public IP: https://whatismyipaddress.com

**Solution:**
Have admin add your IP to the RDS security group inbound rules.

### 4. Wrong Server Address/Port

Less likely, but possible.

**Verify:**
- Server: `public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com`
- Port: `1433` (SQL Server default)

---

## 🧪 Quick Network Tests

### Test 1: Can you resolve the hostname?

```cmd
nslookup public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com
```

**Good response:**
```
Server:  your-dns-server
Address:  x.x.x.x

Name:    public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com
Address:  52.x.x.x
```

**Bad response:**
```
*** can't find public-mssql-db-01...: Non-existent domain
```
→ DNS issue or server doesn't exist

### Test 2: Can you ping the server?

```cmd
ping public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com
```

**Note:** Some servers block ping (ICMP), so this may timeout even if the server is accessible.

### Test 3: Can you reach port 1433?

**PowerShell:**
```powershell
Test-NetConnection -ComputerName public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com -Port 1433
```

**Command Prompt (alternative):**
```cmd
telnet public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com 1433
```

**If you see a blank screen or connection message** → Port is open! ✅
**If you see "Could not open connection"** → Port is blocked ❌

---

## 🔧 Solutions by Scenario

### Scenario A: You're working from home

**Solution:** Connect to company VPN first
```
1. Open VPN client (Cisco AnyConnect, FortiClient, etc.)
2. Connect to VPN
3. Verify connection
4. Run: python test_db.py
```

### Scenario B: You're in the office

**Possible issues:**
- Corporate firewall blocking outbound connections
- Need to request firewall rule from IT
- Server may restrict to specific office IPs

**Solution:**
Contact your IT department and request:
- Allow outbound TCP to port 1433
- Whitelist destination: `public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com`

### Scenario C: Server is on AWS RDS

**Most common issue:** Security group rules

**Solution:**
1. Log into AWS Console
2. Go to RDS → Databases → your database
3. Click on VPC security group
4. Check Inbound Rules
5. Should have rule: `Type: MSSQL, Port: 1433, Source: Your IP or 0.0.0.0/0`
6. If missing, add it

**Or ask your AWS admin to:**
- Add your public IP to the security group
- Or allow your VPN range

### Scenario D: Different network location

**If it worked before but doesn't now:**
- Your IP address changed
- You're on a different network
- VPN disconnected

**Solution:**
- Reconnect to VPN
- Or update IP whitelist

---

## 📋 Checklist for Database Access

Before the app will work, you need:

- [ ] VPN connected (if required)
- [ ] Firewall allows outbound port 1433
- [ ] Your IP is whitelisted on server
- [ ] Can resolve hostname: `nslookup public-mssql-db-01...`
- [ ] Can reach port: `Test-NetConnection ... -Port 1433`
- [ ] `python test_db.py` shows: ✓ Port 1433 is reachable
- [ ] `python test_db.py` shows: ✓ Connection successful

---

## 🚀 Once Network Works

After you fix the network issue:

```cmd
python test_db.py
```

Should show:
```
✓ DNS resolved to: 52.x.x.x
✓ Port 1433 is reachable
✓ Connection successful!
SQL Server version: Microsoft SQL Server...
✓ Found X template(s)
```

Then run your app:
```cmd
python app.py
```

Should show:
```
✓ ODBC Driver detected: ODBC Driver 18 for SQL Server
✓ Database connection OK (X templates available)
⚡️ Bolt app is running!
```

---

## 🆘 Still Can't Connect?

### Get More Help:

1. **Run updated test:**
   ```cmd
   git pull origin main
   python test_db.py
   ```
   The test will pinpoint the exact issue

2. **Contact your database/network admin:**
   - Provide server name: `public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com`
   - Provide port: `1433`
   - Ask if VPN is required
   - Ask if your IP needs to be whitelisted
   - Provide your public IP: https://whatismyipaddress.com

3. **Alternative: Use different network:**
   - Try from office if you're at home (or vice versa)
   - Try with VPN on/off
   - Ask coworker if they can connect

---

## 💡 Pro Tips

1. **Always check VPN first** - This is the #1 cause of database connection issues
2. **Test after every change** - Run `python test_db.py` to verify
3. **Save working configuration** - Once it works, document what you did
4. **Check firewall logs** - Your IT team can see if connections are being blocked

---

## 📞 Who to Contact

Depending on the issue:

- **VPN issues** → Your IT helpdesk
- **Firewall issues** → Your network team
- **IP whitelisting** → Database administrator or AWS admin
- **Server issues** → Database administrator

Provide them:
- Server: `public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com`
- Port: `1433`
- Your public IP: https://whatismyipaddress.com
- Error: "Login timeout expired, server not accessible"

---

## ✅ Success Indicator

You'll know it's working when:

```cmd
python test_db.py
```

Shows all green checkmarks:
```
✓ DNS resolved
✓ Port 1433 is reachable
✓ Connection successful!
✓ Found X templates
```

**Then you're ready to run the app!** 🎉
