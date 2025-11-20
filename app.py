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

# API configuration
API_ENDPOINT = "https://pssrequest.cyberarklab.com/PSSAPI/API/PSSRequest"
REQUEST_KEY = "MU*@e7y8y3umho8urh3788n@MH8eh82oeuMH28uemhuhmO8M!EY27MOHUE!2817EM712=="


def get_epod_templates():
    """Fetch ePOD templates from SQL Server where template_visible = 1"""
    try:
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={SQL_SERVER};'
            f'DATABASE={SQL_DATABASE};'
            f'UID={SQL_USER};'
            f'PWD={SQL_PASSWORD}'
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        query = "SELECT * FROM automation_epod_templates WHERE template_visable = 1"
        cursor.execute(query)
        
        templates = []
        for row in cursor.fetchall():
            templates.append({
                "text": {
                    "type": "plain_text",
                    "text": str(row[1]) if len(row) > 1 else str(row[0])
                },
                "value": str(row[0])
            })
        
        cursor.close()
        conn.close()
        
        return templates if templates else [{"text": {"type": "plain_text", "text": "No templates available"}, "value": "none"}]
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
    channel_id = None
    
    # Try to get channel from trigger
    try:
        # Get the channel where the command was invoked
        # This requires storing it during the initial command
        channel_id = body.get("view", {}).get("private_metadata", {})
    except:
        pass
    
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
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
