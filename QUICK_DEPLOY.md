# ⚡ Quick Deploy to Streamlit Cloud

## 🚀 5-Minute Deployment

### 1️⃣ Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2️⃣ Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Click **"New app"**
3. Enter:
   - **Repository:** Your GitHub repo
   - **Branch:** `main`
   - **Main file:** `biaslense/app/bamip_multipage.py`
4. Click **"Deploy!"**

### 3️⃣ Add API Key
1. Go to **App settings** ⚙️
2. Click **"Secrets"**
3. Add:
```toml
OPENAI_API_KEY = "sk-your-key-here"
openai_api_key = "sk-your-key-here"
```

### 4️⃣ Done! 🎉
Your app will be live at: `https://your-app-name.streamlit.app`

---

## 📋 Pre-Flight Checklist

- [ ] All changes committed to Git
- [ ] Data files (JSON) are in the repository
- [ ] `requirements.txt` is up to date
- [ ] OpenAI API key ready
- [ ] Tested locally: `streamlit run biaslense/app/bamip_multipage.py`

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | Check `requirements.txt` |
| "File not found" | Verify JSON files are committed |
| "API key error" | Add key to Streamlit secrets |
| App won't start | Check logs in dashboard |

## 📚 Full Guide
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
