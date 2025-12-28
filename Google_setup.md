# Google Docs Integration Setup

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the following APIs:
   - Google Docs API
   - Google Drive API

## Step 2: Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop app"
4. Download the JSON file
5. Rename it to `credentials.json`
6. Place it in the `config/` folder

## Step 3: First Run

On first export to Google Docs:
- Browser will open for authentication
- Sign in with your Google account
- Grant permissions
- Token will be saved for future use

## Done!

Your reports will now export to Google Docs automatically.