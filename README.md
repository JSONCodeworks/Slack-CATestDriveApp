# Slack-CATestDriveApp

A Slack application for managing CyberArk Test Drive deployment requests. This app provides an interactive form interface within Slack to collect deployment details, verify submissions, and automatically submit requests to the CyberArk API.

## Features

- **Interactive Form**: Multi-step form with various input types (text, email, phone, date picker, dropdowns)
- **Dynamic Dropdown**: ePOD templates loaded from SQL Server database
- **User Information Auto-fill**: Automatically populates owner email and phone from Slack user profile
- **Verification Step**: Shows formatted JSON preview before final submission
- **API Integration**: Submits approved requests to CyberArk PSS API
- **Error Handling**: Provides user feedback on success or failure

## Prerequisites

- Python 3.8 or higher
- Slack workspace with admin access
- ODBC Driver 17 for SQL Server installed
- Access to SQL Server database
- Access to CyberArk PSS API endpoint

## Installation

### 1. Install ODBC Driver

**Linux (Ubuntu/Debian):**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

**macOS:**
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17
```

**Windows:**
Download and install from [Microsoft Download Center](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 2. Clone Repository

```bash
git clone https://github.com/JSONCodeworks/Slack-CATestDriveApp.git
cd Slack-CATestDriveApp
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Slack App

1. Go to [Slack API](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name it "Slack-CATestDriveApp" and select your workspace
4. Navigate to "OAuth & Permissions" and add these Bot Token Scopes:
   - `chat:write`
   - `commands`
   - `users:read`
   - `users:read.email`
5. Install the app to your workspace
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)
7. Navigate to "Socket Mode" and enable it
8. Generate an App-Level Token with `connections:write` scope
9. Copy the App-Level Token (starts with `xapp-`)
10. Navigate to "Slash Commands" and create a new command:
    - Command: `/testdrive`
    - Request URL: Not needed (using Socket Mode)
    - Short Description: "Submit a test drive request"

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your tokens:
```
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
```

## Usage

### Start the Application

```bash
python app.py
```

The app will connect to Slack via Socket Mode and start listening for commands.

### Using the Slash Command

In any Slack channel or DM, type:
```
/testdrive
```

This will open an interactive form with the following fields:

1. **Test Drive Owner** - Auto-filled with your email
2. **Owner Phone Number** - Auto-filled with your phone (if available)
3. **Company Name** - Text input
4. **Customer Contact Name** - Text input
5. **Customer Contact Phone** - Text input
6. **Customer Contact Email** - Email input
7. **Customer Type** - Dropdown (Internal/External)
8. **Tenant Expiration Date** - Date picker
9. **Tenant Name** - Text input
10. **Salesforce URL** - Optional text input
11. **ePOD Template** - Dropdown populated from SQL database

### Workflow

1. Fill out the form and click "Verify"
2. Review the JSON payload displayed
3. Click "Submit" to send to API or "Cancel" to abort
4. Receive confirmation message in Slack

## Database Configuration

The app connects to the following SQL Server:

- **Server**: `public-mssql-db-01.c4oalnzekxpd.us-west-1.rds.amazonaws.com`
- **Database**: `master`
- **Table**: `automation_epod_templates`
- **Filter**: `template_visable = 1`

## API Configuration

Submissions are sent to:
- **Endpoint**: `https://pssrequest.cyberarklab.com/PSSAPI/API/PSSRequest`
- **Method**: POST
- **Content-Type**: application/json

## JSON Structure

### tdbuildJSON (Verification Display)
```json
{
    "id": "<generated-guid>",
    "owner_email": "user@example.com",
    "owner_phone": "+1234567890",
    "company_name": "Acme Corp",
    "customer_type": "External",
    "sf_url": "https://salesforce.com/opportunity/123",
    "customer_name": "John Doe",
    "customer_email": "john@acme.com",
    "customer_phone": "+1987654321",
    "tenant_name": "acme-testdrive",
    "tenant_type": "POV",
    "expiry_date": "2024-12-31",
    "skytap_userdata": ""
}
```

### createJSON (API Submission)
```json
{
    "request_key": "MU*@e7y8y3umho8urh3788n@MH8eh82oeuMH28uemhuhmO8M!EY27MOHUE!2817EM712==",
    "request_type": "Deploy_ePOD_Template",
    "request_body": { ... }
}
```

## Error Handling

The app handles the following error scenarios:

- **Database Connection Failure**: Shows "Error loading templates" in dropdown
- **API Request Failure**: Sends "An error has occurred" message to user
- **Success**: Sends "Thank you for your submission, check your email shortly for more details."

## Development

### Project Structure
```
Slack-CATestDriveApp/
├── app.py              # Main application logic
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .env               # Your environment variables (not in git)
└── README.md          # This file
```

### Testing

Test the slash command in your Slack workspace:
1. Ensure the app is running (`python app.py`)
2. Type `/testdrive` in any channel
3. Fill out the form with test data
4. Verify the JSON output
5. Submit and check logs for API response

## Troubleshooting

### ODBC Driver Issues
If you get "Driver not found" errors:
- Verify ODBC Driver 17 is installed: `odbcinst -q -d`
- Check driver name in connection string matches installed version

### Database Connection Issues
- Verify network access to SQL Server
- Check credentials and database name
- Test connection with a SQL client first

### Slack Connection Issues
- Ensure Socket Mode is enabled
- Verify both tokens are correct (Bot and App-Level)
- Check that required scopes are granted

## Security Notes

- Keep your `.env` file secure and never commit it to git
- The SQL credentials and API keys are hardcoded for this specific deployment
- Consider implementing additional authentication for production use
- Rotate API keys regularly

## Support

For issues or questions:
- Check Slack app logs in the Slack API dashboard
- Review application logs (`python app.py` output)
- Verify all prerequisites are met

## License

Copyright © 2024 CyberArk. All rights reserved.
