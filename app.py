import os
import json
import uuid
import requests
import pyodbc
from datetime import datetime
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# SQL Server configuration
SQL_SERVER = "public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com"
SQL_USER = "admin"
SQL_PASSWORD = "TowerFlameWater123!!"
SQL_DATABASE = "master"
SQL_PORT = "1433"

# API configuration
API_ENDPOINT = "https://pssrequest.cyberarklab.com/PSSAPI/API/PSSRequest"
REQUEST_KEY = "MU*@e7y8y3umho8urh3788n@MH8eh82oeuMH28uemhuhmO8M!EY27MOHUE!2817EM712=="


def get_odbc_driver():
    """Detect available ODBC driver for SQL Server"""
    drivers = [
        'ODBC Driver 18 for SQL Server',
        'ODBC Driver 17 for SQL Server',
        'ODBC Driver 13 for SQL Server',
        'ODBC Driver 11 for SQL Server',
        'SQL Server Native Client 11.0',
        'SQL Server'
    ]
    
    available_drivers = pyodbc.drivers()
    
    for driver in drivers:
        if driver in available_drivers:
            return driver
    
    raise Exception(f"No SQL Server ODBC driver found. Available: {available_drivers}")


def get_connection_string(driver):
    """Get connection string optimized for ODBC Driver 18"""
    # ODBC Driver 18 requires special handling for SSL
    if 'ODBC Driver 18' in driver:
        # Use Encrypt=optional for maximum compatibility
        conn_str = (
            f'DRIVER={{{driver}}};'
            f'SERVER={SQL_SERVER},{SQL_PORT};'
            f'DATABASE={SQL_DATABASE};'
            f'UID={SQL_USER};'
            f'PWD={SQL_PASSWORD};'
            f'Encrypt=optional;'
        )
    else:
        # Older drivers use simpler connection string
        conn_str = (
            f'DRIVER={{{driver}}};'
            f'SERVER={SQL_SERVER},{SQL_PORT};'
            f'DATABASE={SQL_DATABASE};'
            f'UID={SQL_USER};'
            f'PWD={SQL_PASSWORD};'
        )
    
    return conn_str


def get_epod_templates():
    """Fetch ePOD templates from SQL Server where template_visible = 1"""
    try:
        driver = get_odbc_driver()
        conn_str = get_connection_string(driver)
        
        print(f"Connecting to SQL Server: {SQL_SERVER}...")
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        
        query = "SELECT * FROM automation_epod_templates WHERE template_visable = 1"
        cursor.execute(query)
        
        templates = []
        for row in cursor.fetchall():
            # Assuming first column is ID and second is name
            template_name = str(row[1]) if len(row) > 1 else str(row[0])
            template_value = str(row[0])
            templates.append({
                "text": {
                    "type": "plain_text",
                    "text": template_name
                },
                "value": template_value
            })
        
        cursor.close()
        conn.close()
        
        print(f"Successfully fetched {len(templates)} templates")
        return templates if templates else [{"text": {"type": "plain_text", "text": "No templates available"}, "value": "none"}]
        
    except pyodbc.Error as e:
        error_msg = str(e)
        print(f"Database error: {error_msg}")
        
        if "SSL" in error_msg or "certificate" in error_msg:
            print("ERROR: SSL certificate validation failed")
            print("This is usually fixed by using Encrypt=optional")
            print("Please run: python test_db.py")
        elif "08001" in error_msg or "timeout" in error_msg.lower():
            print("ERROR: Cannot connect to SQL Server")
            print("Check VPN connection or network access")
        elif "IM002" in error_msg:
            print("ERROR: ODBC Driver not found!")
        
        return [{"text": {"type": "plain_text", "text": "Error: Cannot connect to database"}, "value": "error"}]
        
    except Exception as e:
        print(f"Error fetching templates: {e}")
        return [{"text": {"type": "plain_text", "text": "Error loading templates"}, "value": "error"}]


def get_user_email(client, user_id):
    """Get user email address"""
    try:
        user_info = client.users_info(user=user_id)
        return user_info["user"]["profile"]["email"]
    except Exception as e:
        print(f"Error getting user email: {e}")
        return ""


def get_user_phone(client, user_id):
    """Get user phone number if available"""
    try:
        user_info = client.users_info(user=user_id)
        return user_info["user"]["profile"].get("phone", "")
    except Exception as e:
        print(f"Error getting user phone: {e}")
        return ""


@app.command("/testdrive")
def handle_testdrive_command(ack, body, client):
    """Handle /testdrive slash command"""
    ack()
    
    user_id = body["user_id"]
    user_email = get_user_email(client, user_id)
    user_phone = get_user_phone(client, user_id)
    
    # Get ePOD templates
    templates = get_epod_templates()
    
    # Check if there was a database error
    if templates and templates[0]["value"] == "error":
        try:
            client.chat_postMessage(
                channel=user_id,
                text="⚠️ Cannot connect to database. Please contact the administrator."
            )
        except:
            pass
        return
    
    # Open modal with form
    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "testdrive_form",
                "title": {
                    "type": "plain_text",
                    "text": "Test Drive Request"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Verify"
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel"
                },
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "owner_email",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "owner_email_input",
                            "initial_value": user_email
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Test Drive Owner"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "owner_phone",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "owner_phone_input",
                            "initial_value": user_phone
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Owner Phone Number"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "company_name",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "company_name_input"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Company Name"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "customer_contact_name",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "customer_contact_name_input"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Customer Contact Name"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "customer_contact_phone",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "customer_contact_phone_input"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Customer Contact Phone"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "customer_contact_email",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "customer_contact_email_input"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Customer Contact Email"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "customer_type",
                        "element": {
                            "type": "static_select",
                            "action_id": "customer_type_select",
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Internal"
                                    },
                                    "value": "Internal"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "External"
                                    },
                                    "value": "External"
                                }
                            ]
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Customer Type"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "expiry_date",
                        "element": {
                            "type": "datepicker",
                            "action_id": "expiry_date_picker"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Tenant Expiration Date"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "tenant_name",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "tenant_name_input"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Tenant Name"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "sf_url",
                        "optional": True,
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "sf_url_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "optional"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Salesforce URL (optional)"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "epod_template",
                        "element": {
                            "type": "static_select",
                            "action_id": "epod_template_select",
                            "options": templates
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "ePOD Template"
                        }
                    }
                ]
            }
        )
    except Exception as e:
        print(f"Error opening modal: {e}")


@app.view("testdrive_form")
def handle_testdrive_submission(ack, body, client, view):
    """Handle form submission and show verification"""
    ack()
    
    # Extract form values
    values = view["state"]["values"]
    
    # Create tdbuildJSON
    tdbuild_json = {
        "id": str(uuid.uuid4()),
        "owner_email": values["owner_email"]["owner_email_input"]["value"],
        "owner_phone": values["owner_phone"]["owner_phone_input"]["value"],
        "company_name": values["company_name"]["company_name_input"]["value"],
        "customer_type": values["customer_type"]["customer_type_select"]["selected_option"]["value"],
        "sf_url": values["sf_url"]["sf_url_input"].get("value", ""),
        "customer_name": values["customer_contact_name"]["customer_contact_name_input"]["value"],
        "customer_email": values["customer_contact_email"]["customer_contact_email_input"]["value"],
        "customer_phone": values["customer_contact_phone"]["customer_contact_phone_input"]["value"],
        "tenant_name": values["tenant_name"]["tenant_name_input"]["value"],
        "tenant_type": "POV",
        "expiry_date": values["expiry_date"]["expiry_date_picker"]["selected_date"],
        "skytap_userdata": ""
    }
    
    # Format JSON for display
    json_display = json.dumps(tdbuild_json, indent=2)
    
    # Open verification modal
    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "verify_submission",
                "private_metadata": json.dumps(tdbuild_json),
                "title": {
                    "type": "plain_text",
                    "text": "Verify Submission"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Submit"
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel"
                },
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Please verify your submission:*"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"```{json_display}```"
                        }
                    }
                ]
            }
        )
    except Exception as e:
        print(f"Error opening verification modal: {e}")


@app.view("verify_submission")
def handle_final_submission(ack, body, client, view):
    """Handle final submission to API"""
    ack()
    
    user_id = body["user"]["id"]
    
    # Parse tdbuildJSON from private_metadata
    tdbuild_json = json.loads(view["private_metadata"])
    
    # Create createJSON
    create_json = {
        "request_key": REQUEST_KEY,
        "request_type": "Deploy_ePOD_Template",
        "request_body": tdbuild_json
    }
    
    # Send POST request to API
    try:
        response = requests.post(
            API_ENDPOINT,
            json=create_json,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # Check if successful
        if response.status_code == 200 or response.status_code == 201:
            message = "Thank you for your submission, check your email shortly for more details."
        else:
            message = "An error has occurred"
            print(f"API Error: Status {response.status_code}, Response: {response.text}")
            
    except Exception as e:
        print(f"Error calling API: {e}")
        message = "An error has occurred"
    
    # Send message to user via DM
    try:
        client.chat_postMessage(
            channel=user_id,
            text=message
        )
    except Exception as e:
        print(f"Error sending message: {e}")


# Start the app
if __name__ == "__main__":
    print("=" * 60)
    print("Slack-CATestDriveApp Starting...")
    print("=" * 60)
    print()
    
    # Check for ODBC driver on startup
    try:
        driver = get_odbc_driver()
        print(f"✓ ODBC Driver detected: {driver}")
    except Exception as e:
        print("✗ ODBC Driver Error:")
        print(str(e))
        print()
        print("The app will start, but database features will not work.")
        print()
    
    # Test database connection on startup
    print("\nTesting database connection...")
    try:
        templates = get_epod_templates()
        if templates and templates[0]["value"] != "error":
            print(f"✓ Database connection OK ({len(templates)} templates available)")
        else:
            print("✗ Database connection FAILED")
            print("  Run: python test_db.py for diagnostics")
    except Exception as e:
        print(f"✗ Database test failed: {e}")
    
    print("\nStarting Slack Socket Mode handler...")
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
