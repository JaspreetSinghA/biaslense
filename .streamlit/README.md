# Streamlit Configuration

This directory contains configuration files for Streamlit deployment.

## Files

### `config.toml`
Server configuration for production deployment. Already configured for Streamlit Community Cloud.

### `secrets.toml` (Not in Git)
Contains sensitive API keys and credentials. Create this file locally for testing:

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
openai_api_key = "sk-your-api-key-here"
```

**Important:** 
- This file is gitignored for security
- For Streamlit Cloud deployment, add secrets through the dashboard
- Both uppercase and lowercase keys are included for compatibility

## Adding Secrets to Streamlit Cloud

1. Deploy your app on Streamlit Community Cloud
2. Go to App Settings (⚙️ icon)
3. Click "Secrets" in the sidebar
4. Paste your secrets in TOML format
5. Save and restart the app

## Local Testing

To test locally with secrets:

```bash
# Create secrets file
echo 'OPENAI_API_KEY = "sk-your-key"' > .streamlit/secrets.toml

# Run the app
streamlit run biaslense/app/bamip_multipage.py
```

## Security Notes

- Never commit `secrets.toml` to version control
- Rotate API keys if accidentally exposed
- Use environment variables as an alternative to secrets.toml
