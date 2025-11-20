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


def test_connection():
    """Test SQL Server connection with multiple methods"""
    print("=" * 60)
    print("SQL Server Connection Test")
    print("=" * 60)
    print()
    
    print(f"Server: {SQL_SERVER}")
    print(f"Database: {SQL_DATABASE}")
    print(f"Port: {SQL_PORT}")
    print("-" * 60)
    
    # Get ODBC driver
    try:
        driver = get_odbc_driver()
        print(f"\nUsing ODBC driver: {driver}")
    except Exception as e:
        print(f"\n✗ {e}")
        return False
    
    print("\n" + "=" * 60)
    print("Testing Connection Methods")
    print("=" * 60)
    
    # Method 1: ODBC Driver 18 with TrustServerCertificate (most compatible)
    print("\n[Method 1] Driver 18 with TrustServerCertificate=yes, Encrypt=yes")
    conn_str_1 = (
        f'DRIVER={{{driver}}};'
        f'SERVER={SQL_SERVER},{SQL_PORT};'
        f'DATABASE={SQL_DATABASE};'
        f'UID={SQL_USER};'
        f'PWD={SQL_PASSWORD};'
        f'TrustServerCertificate=yes;'
        f'Encrypt=yes;'
    )
    
    if test_connection_method(conn_str_1):
        print("\n✓ Connection successful!")
        test_queries(conn_str_1)
        return True
    
    # Method 2: ODBC Driver 18 with optional encryption
    print("\n[Method 2] Driver 18 with Encrypt=optional")
    conn_str_2 = (
        f'DRIVER={{{driver}}};'
        f'SERVER={SQL_SERVER},{SQL_PORT};'
        f'DATABASE={SQL_DATABASE};'
        f'UID={SQL_USER};'
        f'PWD={SQL_PASSWORD};'
        f'Encrypt=optional;'
    )
    
    if test_connection_method(conn_str_2):
        print("\n✓ Connection successful!")
        test_queries(conn_str_2)
        return True
    
    # Method 3: No encryption
    print("\n[Method 3] Driver with Encrypt=no")
    conn_str_3 = (
        f'DRIVER={{{driver}}};'
        f'SERVER={SQL_SERVER},{SQL_PORT};'
        f'DATABASE={SQL_DATABASE};'
        f'UID={SQL_USER};'
        f'PWD={SQL_PASSWORD};'
        f'Encrypt=no;'
    )
    
    if test_connection_method(conn_str_3):
        print("\n✓ Connection successful!")
        test_queries(conn_str_3)
        return True
    
    # Method 4: Without explicit port
    print("\n[Method 4] Without explicit port, TrustServerCertificate=yes")
    conn_str_4 = (
        f'DRIVER={{{driver}}};'
        f'SERVER={SQL_SERVER};'
        f'DATABASE={SQL_DATABASE};'
        f'UID={SQL_USER};'
        f'PWD={SQL_PASSWORD};'
        f'TrustServerCertificate=yes;'
        f'Encrypt=yes;'
    )
    
    if test_connection_method(conn_str_4):
        print("\n✓ Connection successful!")
        test_queries(conn_str_4)
        return True
    
    print("\n" + "=" * 60)
    print("All connection methods failed")
    print("=" * 60)
    return False


def test_connection_method(conn_str):
    """Test a specific connection method"""
    try:
        # Hide password in output
        safe_conn_str = conn_str.replace(SQL_PASSWORD, "***")
        print(f"Trying: {safe_conn_str[:100]}...")
        
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        
        # Simple test query
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"✓ Connected! SQL Server version: {version[:60]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except pyodbc.Error as e:
        error_msg = str(e)
        print(f"✗ Failed: {error_msg[:150]}...")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)[:150]}...")
        return False


def test_queries(conn_str):
    """Test actual queries once connected"""
    print("\n" + "=" * 60)
    print("Testing Database Queries")
    print("=" * 60)
    
    try:
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
                print(f"\nTemplate {row_count}:")
                for idx, column in enumerate(cursor.description):
                    value = str(row[idx])[:100]  # Limit length
                    print(f"  {column[0]}: {value}")
            
            if row_count == 0:
                print("⚠ No templates found where template_visable = 1")
            else:
                print(f"\n✓ Found {row_count} template(s)")
        
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
        print("✓ Test completed successfully!")
        print()
        print("Your app should now work. Run:")
        print("  python app.py")
    else:
        print("✗ Test failed - see errors above")
    print("=" * 60)
