"""
Test script to verify SQL Server connection and template retrieval
"""
import pyodbc

# SQL Server configuration
SQL_SERVER = "public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com"
SQL_USER = "admin"
SQL_PASSWORD = "TowerFlameWater123!!"
SQL_DATABASE = "master"

def test_connection():
    """Test SQL Server connection"""
    print("Testing SQL Server connection...")
    print(f"Server: {SQL_SERVER}")
    print(f"Database: {SQL_DATABASE}")
    print("-" * 50)
    
    try:
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={SQL_SERVER};'
            f'DATABASE={SQL_DATABASE};'
            f'UID={SQL_USER};'
            f'PWD={SQL_PASSWORD}'
        )
        
        print("\nConnecting to database...")
        conn = pyodbc.connect(conn_str, timeout=10)
        print("✓ Successfully connected to SQL Server")
        
        cursor = conn.cursor()
        
        # Test query
        print("\nTesting query on automation_epod_templates table...")
        query = "SELECT * FROM automation_epod_templates WHERE template_visable = 1"
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
        
        cursor.close()
        conn.close()
        print("\n✓ Connection closed successfully")
        
        return True
        
    except pyodbc.Error as e:
        print(f"\n✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SQL Server Connection Test")
    print("=" * 50)
    print()
    
    success = test_connection()
    
    print()
    print("=" * 50)
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed. Please check the error messages above.")
    print("=" * 50)
