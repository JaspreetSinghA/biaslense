# PyPI Upload Guide for BiasLens SDK v1.0.0

## Status
✅ Package building: Complete  
✅ Local testing: Complete (wheel + source installations work)  
✅ Package validation: Complete (twine check passed)  
⏳ PyPI account: Needs setup (manual step)  

## What's Ready
- `dist/biaslense-1.0.0-py3-none-any.whl` (wheel)
- `dist/biaslense-1.0.0.tar.gz` (source)
- Both distributions are validated and ready for upload

---

## Step 6: Create PyPI Account (5 min - Manual)

### Option A: First Time on PyPI
1. Visit: https://pypi.org/account/register/
2. Register with:
   - Email: `jaspreetahluwalia007@gmail.com`
   - Username: Create your preferred username (e.g., `JaspreetSinghA`)
   - Password: Use a strong password
3. Verify email (check inbox for verification link)

### Option B: Already Have PyPI Account
Skip to "Generate API Token" below

### Generate API Token (Required)
1. Visit: https://pypi.org/manage/account/
2. Login with your PyPI credentials
3. Left sidebar → "API tokens"
4. Click "Add API token"
5. **Name:** `biaslense-publish`
6. **Scope:** "Entire account"
7. **Copy the token** (starts with `pypi-AgEI...`)
   - ⚠️ **Important:** You'll only see this token once!
   - Store it in a password manager or secure location

### Create ~/.pypirc Configuration
```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEI...YOUR_TOKEN_HERE...
EOF

chmod 600 ~/.pypirc
```

---

## Step 7: Upload to PyPI (5 min)

### Option A: Upload to TestPyPI First (Recommended)
Test on PyPI's staging environment before production:

```bash
cd /Users/jaspreetsingh/biaslense

# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install -i https://test.pypi.org/simple/ biaslense
```

### Option B: Upload to Production PyPI
```bash
cd /Users/jaspreetsingh/biaslense

# Upload to PyPI (production)
python3 -m twine upload dist/*

# Verify installation
pip install --upgrade biaslense

# Test it works
python3 -c "from biaslense.sdk import BamiPClient; print('✓ Installed from PyPI')"
```

### Check PyPI Page
After successful upload, your package will appear at:
- **PyPI:** https://pypi.org/project/biaslense/
- **Package name:** `biaslense`
- **Version:** `1.0.0`

---

## Step 8: Create GitHub Release

### Create git tag and push
```bash
cd /Users/jaspreetsingh/biaslense

# Commit packaging files
git add setup.py MANIFEST.in
git commit -m "chore: prepare SDK for PyPI publication"

# Create git tag
git tag -a v1.0.0 -m "Release v1.0.0: Python SDK on PyPI"

# Push tag to GitHub
git push origin v1.0.0
```

### Create GitHub Release Page
1. Go to: https://github.com/JaspreetSinghA/biaslense/releases
2. Click "Draft a new release"
3. Fill in:
   - **Tag version:** `v1.0.0`
   - **Release title:** `v1.0.0: BiasLens Python SDK on PyPI`
   - **Description:**
     ```markdown
     # BiasLens SDK v1.0.0 - Now on PyPI! 🎉

     Install with: `pip install biaslense`

     ## What's New
     - BiasLens SDK is now publicly available on PyPI
     - Easy installation for Python developers
     - Full support for local and remote bias analysis

     ## Features
     - ✓ Unified interface for local and remote bias analysis
     - ✓ Client-side rate limiting (DDoS protection)
     - ✓ Batch processing with automatic retry logic
     - ✓ Full type hints and comprehensive documentation
     - ✓ Minimal dependencies (requests + pydantic)

     ## Installation
     ```bash
     pip install biaslense
     ```

     ## Quick Start
     ```python
     from biaslense.sdk import BamiPClient

     client = BamiPClient()  # Local or remote
     result = client.analyze(
         prompt="Tell me about Sikhism",
         ai_response="Sikhs are Muslims who wear turbans...",
         ai_model="gpt-4"
     )
     print(f"Risk Level: {result.risk_level}")
     ```

     ## Documentation
     - [SDK README](https://github.com/JaspreetSinghA/biaslense/blob/main/biaslense/sdk/README.md)
     - [Quick Start Guide](https://github.com/JaspreetSinghA/biaslense#quick-start)
     - [Examples](https://github.com/JaspreetSinghA/biaslense/tree/main/examples)
     - [Full API Documentation](https://github.com/JaspreetSinghA/biaslense/blob/main/README.md)

     ## Links
     - 📦 **PyPI:** https://pypi.org/project/biaslense/
     - 🐙 **GitHub:** https://github.com/JaspreetSinghA/biaslense
     - 📖 **Algorithm:** See ALGORITHM.md for methodology

     ## What's Next
     - Phase 4a: Paper resubmission with empirical validation
     - Phase 4c: Launch blog post highlighting methodology
     - Phase 4d: Community announcement and feedback collection
     ```

4. Click "Publish release"

---

## Verification Checklist

### After PyPI Upload:
- [ ] Package appears on https://pypi.org/project/biaslense/
- [ ] Version shows as `1.0.0`
- [ ] Description displays correctly
- [ ] Installation instructions work: `pip install biaslense`
- [ ] Can import: `from biaslense.sdk import BamiPClient`
- [ ] PyPI page links back to GitHub repo

### After GitHub Release:
- [ ] Release appears at https://github.com/JaspreetSinghA/biaslense/releases
- [ ] Tag v1.0.0 is created in git
- [ ] Release notes are clear and informative
- [ ] Links to PyPI, docs, and examples work

---

## Troubleshooting

### "401 Unauthorized" on upload
- Check ~/.pypirc has correct token
- Verify token is still valid (tokens don't expire unless you revoke)
- Make sure `username = __token__` (exactly)

### "Package already exists"
- Version already uploaded (can't re-upload same version)
- Solution: Increment version (1.0.1, 1.0.2, etc.)
- Create new release

### Installation fails with "No module named 'requests'"
- Dependencies not installed
- Run: `pip install -e .` with dependencies
- Or manually: `pip install requests pydantic`

### GitHub tag push fails
- Make sure commits are pushed first: `git push origin main`
- Then push tag: `git push origin v1.0.0`

---

## Timeline

| Step | Task | Time | Status |
|------|------|------|--------|
| 1 | Create setup.py | 15 min | ✅ Done |
| 2 | Create MANIFEST.in | 5 min | ✅ Done |
| 3 | Verify structure | 10 min | ✅ Done |
| 4 | Build distribution | 5 min | ✅ Done |
| 5 | Test locally | 10 min | ✅ Done |
| 6 | PyPI account setup | 5 min | ⏳ Next |
| 7 | Upload to PyPI | 5 min | ⏳ After Step 6 |
| 8 | GitHub release | 5 min | ⏳ After Step 7 |
| **Total** | | **~60 min** | **On track** |

---

## Questions?

If you need help with any step:
1. Check the troubleshooting section above
2. See [ROADMAP.md](ROADMAP.md) for context
3. Open an issue on GitHub: https://github.com/JaspreetSinghA/biaslense/issues
