# 🚀 Streamlit Community Cloud Deployment Guide

## Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Streamlit Community Cloud Account** - Sign up at https://streamlit.io/cloud
3. **OpenAI API Key** - Required for the BAMIP pipeline

## 📋 Pre-Deployment Checklist

### ✅ Files Already Configured

- [x] `.streamlit/config.toml` - Server configuration
- [x] `biaslense/requirements.txt` - Python dependencies
- [x] `biaslense/packages.txt` - System dependencies
- [x] Main app file: `biaslense/app/bamip_multipage.py`

### ⚠️ Important: Data Files

Make sure your required JSON data files are committed to Git:
- `src/data/stereotype_lexicon.json` (or equivalent)
- Any other data files needed by the app

**Note:** The `.gitignore` has been updated to allow JSON files in `src/data/` and `biaslense/data/` directories.

## 🔑 Step 1: Prepare Your Repository

### 1.1 Commit All Changes

```bash
# Check git status
git status

# Add all changes
git add .

# Commit changes
git commit -m "Prepare for Streamlit Cloud deployment"

# Push to GitHub
git push origin main
```

### 1.2 Verify Required Files

Ensure these files are in your repository:
- `biaslense/requirements.txt`
- `biaslense/packages.txt`
- `.streamlit/config.toml`
- `biaslense/app/bamip_multipage.py`
- Required data files (JSON files)

## 🌐 Step 2: Deploy to Streamlit Community Cloud

### 2.1 Sign Up / Log In

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Authorize Streamlit to access your repositories

### 2.2 Create New App

1. Click **"New app"** button
2. Fill in the deployment form:

   **Repository:** `JaspreetSinghA/biaslense` (or your repo)
   
   **Branch:** `main` (or your default branch)
   
   **Main file path:** `biaslense/app/bamip_multipage.py`
   
   **App URL:** Choose a custom URL (e.g., `biaslense-app`)

### 2.3 Advanced Settings (Optional)

Click "Advanced settings" to configure:
- **Python version:** 3.9 or 3.10 (recommended)
- **Secrets:** Add your OpenAI API key (see Step 3)

## 🔐 Step 3: Configure Secrets (API Keys)

### Option A: Through Streamlit Cloud Dashboard (Recommended)

1. After creating the app, go to **App settings** (⚙️ icon)
2. Click on **"Secrets"** in the left sidebar
3. Add your secrets in TOML format:

```toml
# .streamlit/secrets.toml format
OPENAI_API_KEY = "sk-your-api-key-here"
openai_api_key = "sk-your-api-key-here"
```

**Important:** Add both keys (uppercase and lowercase) to ensure compatibility with all code paths.

### Option B: Create secrets.toml Locally (For Testing)

For local testing, create `.streamlit/secrets.toml`:

```bash
# Create secrets file (this file is gitignored)
cat > .streamlit/secrets.toml << EOF
OPENAI_API_KEY = "sk-your-api-key-here"
openai_api_key = "sk-your-api-key-here"
EOF
```

**Note:** Never commit `secrets.toml` to Git. It's already in your `.gitignore`.

## 🎯 Step 4: Deploy and Monitor

### 4.1 Initial Deployment

1. Click **"Deploy!"** button
2. Wait for the build process (usually 2-5 minutes)
3. Monitor the logs for any errors

### 4.2 Common Build Issues and Solutions

#### Issue: "Module not found"
**Solution:** Check that all imports are in `requirements.txt`

#### Issue: "File not found" (JSON data files)
**Solution:** 
- Verify JSON files are committed to Git
- Check file paths in your code
- Ensure `.gitignore` allows the files

#### Issue: "Memory limit exceeded"
**Solution:** 
- Streamlit Cloud has memory limits
- Consider using smaller models
- Optimize data loading with `@st.cache_resource`

#### Issue: "API key not found"
**Solution:**
- Add API key to Streamlit Cloud secrets
- Restart the app after adding secrets

## 📊 Step 5: Post-Deployment

### 5.1 Test Your App

1. Visit your app URL: `https://your-app-name.streamlit.app`
2. Test all features:
   - Home page loads correctly
   - Test BAMIP analysis works
   - History page functions properly
   - API calls to OpenAI succeed

### 5.2 Monitor Usage

- Check the Streamlit Cloud dashboard for:
  - App uptime
  - Resource usage
  - Error logs
  - Visitor analytics

### 5.3 Update Your App

To deploy updates:

```bash
# Make changes to your code
git add .
git commit -m "Update feature X"
git push origin main
```

Streamlit Cloud will automatically redeploy when you push to GitHub!

## 🔧 Troubleshooting

### App Won't Start

1. **Check logs** in Streamlit Cloud dashboard
2. **Verify file paths** - ensure main file path is correct
3. **Test locally** first: `streamlit run biaslense/app/bamip_multipage.py`

### Slow Performance

1. **Use caching** - Add `@st.cache_data` and `@st.cache_resource`
2. **Optimize imports** - Only import what you need
3. **Reduce model size** - Use smaller transformer models if possible

### API Errors

1. **Check API key** - Verify it's correctly set in secrets
2. **Check quotas** - Ensure you haven't exceeded OpenAI limits
3. **Add error handling** - Gracefully handle API failures

## 📝 Best Practices

### 1. Resource Management

```python
# Use caching for expensive operations
@st.cache_resource
def load_model():
    return SentenceTransformer('model-name')

@st.cache_data
def load_data():
    return pd.read_json('data.json')
```

### 2. Environment Detection

```python
import os

# Check if running on Streamlit Cloud
is_cloud = os.getenv('STREAMLIT_SHARING_MODE') is not None
```

### 3. Graceful Degradation

```python
# Provide fallback if API key missing
if not api_key:
    st.warning("⚠️ API key not configured. Using demo mode.")
    # Provide limited functionality
```

## 🎨 Custom Domain (Optional)

Streamlit Cloud provides a free subdomain: `your-app.streamlit.app`

For a custom domain:
1. Upgrade to a paid plan
2. Configure DNS settings
3. Follow Streamlit's custom domain guide

## 📚 Additional Resources

- **Streamlit Docs:** https://docs.streamlit.io/
- **Deployment Guide:** https://docs.streamlit.io/streamlit-community-cloud
- **Community Forum:** https://discuss.streamlit.io/
- **GitHub Issues:** Report issues in your repository

## 🆘 Getting Help

If you encounter issues:

1. **Check Streamlit Community Forum:** https://discuss.streamlit.io/
2. **Review app logs** in Streamlit Cloud dashboard
3. **Test locally** to isolate cloud-specific issues
4. **Check GitHub Issues** for similar problems

## ✅ Deployment Checklist Summary

- [ ] Code pushed to GitHub
- [ ] Required files present (requirements.txt, packages.txt, config.toml)
- [ ] Data files committed and accessible
- [ ] Streamlit Cloud account created
- [ ] App deployed with correct file path
- [ ] API keys added to secrets
- [ ] App tested and working
- [ ] README updated with live app URL

---

**Your app should be live at:** `https://your-app-name.streamlit.app`

Good luck with your deployment! 🚀
