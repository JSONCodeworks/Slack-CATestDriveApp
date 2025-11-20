"""
Test script to verify SQL Server connection and template retrieval
"""
import pyodbc
import socket

# SQL Server configuration
SQL_SERVER = "public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com"
SQL_USER = "admin"
SQL_PASSWORD = "TowerFlameWater123!!"
SQL_DATABASE = "master"
SQL_PORT = "1433"


def test_network_connectivity():
    """Test basic network connectivity to SQL Server"""
    print("Testing network connectivity...")
    print(f"Server: {SQL_SERVER}")
    print(f"Port: {SQL_PORT}")
    print("-" * 50)
    
    # Test DNS resolution
    try:
        print("\nResolving hostname...")
        ip_address = socket.gethostbyname(SQL_SERVER)
        print(f"✓ DNS resolved to: {ip_address}")
    except socket.gaierror as e:
        print(f"✗ DNS resolution failed: {e}")
        return False
    
    # Test port connectivity
    try:
        print(f"\nTesting TCP connection to port {SQL_PORT}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((SQL_SERVER, int(SQL_PORT)))
        sock.close()
        
        if result == 0:
            print(f"✓ Port {SQL_PORT} is reachable")
            return True
        else:
            print(f"✗ Port {SQL_PORT} is not reachable (error code: {result})")
            print("\nPossible causes:")
            print("  - Firewall blocking outbound connections")
            print("  - VPN required to access this server")
            print("  - Server firewall blocking your IP address")
            print("  - Server is down or not accessible")
            return False
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False


def get_odbc_driver():
    """Detect available ODBC driver for SQL Server"""
    drivers = [
        'ODBC Driver 18 for SQL Server',
        'ODBC Driver 17 for SQL Server',
        'ODBC Driver 13 for SQL Server',
        'ODBC Driver 11 for SQL Server',
    ]
    
    available_drivers = pyodbc.drivers()
    
    for driver in drivers:
        if driver in available_drivers:
            return driver
    
    raise Exception(f"No SQL Server ODBC driver found. Available: {available_drivers}")


def test_connection_method(driver, connection_params):
    """Test a specific connection method"""
    try:
        conn_str = ';'.join([f'{k}={v}' for k, v in connection_params.items()])
        print(f"\nTrying connection with: {driver}")
        print(f"Parameters: {', '.join([k for k in connection_params.keys() if k not in ['PWD']])}")
        
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        
        # Simple test query
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"✓ Connection successful!")
        print(f"  SQL Server version: {version[:80]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {str(e)[:200]}")
        return False


def test_connection():
    """Test SQL Server connection with multiple methods"""
    print("=" * 60)
    print("SQL Server Connection Test")
    print("=" * 60)
    print()
    
    # Step 1: Network connectivity
    if not test_network_connectivity():
        print("\n" + "=" * 60)
        print("Network connectivity test FAILED")
        print("=" * 60)
        print("\nThe server is not reachable from your network.")
        print("\nPossible solutions:")
        print("  1. Check if you need VPN to access this server")
        print("  2. Check your firewall settings")
        print("  3. Verify the server address is correct")
        print("  4. Contact your network administrator")
        return False
    
    print("\n" + "=" * 60)
    print("Network connectivity: OK")
    print("=" * 60)
    
    # Step 2: ODBC Driver check
    try:
        driver = get_odbc_driver()
        print(f"\nUsing ODBC driver: {driver}")
    except Exception as e:
        print(f"\n✗ {e}")
        return False
    
    # Step 3: Try different connection methods
    print("\n" + "=" * 60)
    print("Testing SQL Server Authentication")
    print("=" * 60)
    
    # Method 1: TCP/IP with explicit port
    params1 = {
        'DRIVER': f'{{{driver}}}',
        'SERVER': f'{SQL_SERVER},{SQL_PORT}',
        'DATABASE': SQL_DATABASE,
        'UID': SQL_USER,
        'PWD': SQL_PASSWORD,
        'TrustServerCertificate': 'yes',
        'Encrypt': 'yes'
    }
    
    if test_connection_method(driver, params1):
        print("\n✓ Connection method found!")
        test_queries(driver, params1)
        return True
    
    # Method 2: Without explicit port
    params2 = {
        'DRIVER': f'{{{driver}}}',
        'SERVER': SQL_SERVER,
        'DATABASE': SQL_DATABASE,
        'UID': SQL_USER,
        'PWD': SQL_PASSWORD,
        'TrustServerCertificate': 'yes',
        'Encrypt': 'yes'
    }
    
    if test_connection_method(driver, params2):
        print("\n✓ Connection method found!")
        test_queries(driver, params2)
        return True
    
    # Method 3: Disable encryption
    params3 = {
        'DRIVER': f'{{{driver}}}',
        'SERVER': f'{SQL_SERVER},{SQL_PORT}',
        'DATABASE': SQL_DATABASE,
        'UID': SQL_USER,
        'PWD': SQL_PASSWORD,
        'Encrypt': 'no'
    }
    
    if test_connection_method(driver, params3):
        print("\n✓ Connection method found!")
        test_queries(driver, params3)
        return True
    
    print("\n" + "=" * 60)
    print("All connection methods failed")
    print("=" * 60)
    print("\nThe server is reachable but authentication failed.")
    print("\nPossible causes:")
    print("  - SQL Server authentication not enabled")
    print("  - Credentials are incorrect")
    print("  - Your IP is not allowed by server firewall")
    print("  - Database does not exist")
    
    return False


def test_queries(driver, params):
    """Test actual queries once connected"""
    print("\n" + "=" * 60)
    print("Testing Database Queries")
    print("=" * 60)
    
    try:
        conn_str = ';'.join([f'{k}={v}' for k, v in params.items()])
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        
        # Test table query
        print("\nQuerying automation_epod_templates table...")
        query = "SELECT * FROM automation_epod_templates WHERE template_visable = 1"
        
        try:
            cursor.execute(query)
            
            print("\nTemplates found:")
            print("-" * 50)
            
            row_count = 0
            for row in cursor.fetchall():
                row_count += 1
                print(f"Template {row_count}:")
                for idx, column in enumerate(cursor.description):
                    print(f"  {column[0]}: {row[idx]}")
                print()
            
            if row_count == 0:
                print("⚠ No templates found where template_visable = 1")
            else:
                print(f"✓ Found {row_count} template(s)")
        
        except pyodbc.Error as e:
            print(f"✗ Query failed: {e}")
            print("\nThe table may not exist or you don't have permission.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    success = test_connection()
    
    print()
    print("=" * 60)
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed - see errors above")
    print("=" * 60)
