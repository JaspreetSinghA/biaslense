# BiasLens Project Roadmap

**Last Updated:** May 31, 2026  
**Current Phase:** Phase 3 Complete ✅ (Python SDK)  
**Next Phase:** Phase 1.5 + Phase 4 (Launch)

---

## Executive Summary

BiasLens has achieved **algorithm credibility** (Phase 2) and **multi-platform distribution** (Phase 3). The next 3-6 months focus on **launching to users and building a feedback loop** to guide future development.

### Core Goals
1. **Paper Resubmission** — Empirically validated algorithm ready for publication
2. **Accessible Tool** — Available via web app, REST API, Python SDK
3. **Real Users & Feedback** — Build based on actual user needs, not assumptions

---

## Completed Phases

### Phase 1: REST API ✅
- **Status:** Complete, deployed on Railway
- **Features:** `/health`, `/analyze`, `/analyze/batch` endpoints
- **Deployment:** https://web-production-59ba5.up.railway.app
- **Rate Limiting:** 10 req/min for /analyze, 5 req/min for /batch
- **Commit:** `f83dcd4` (feat: add rate limiting and MCP server)

### Phase 2: Algorithm Credibility ✅
- **Status:** Complete, empirically validated
- **Features:** 
  - Krippendorff's α analysis (inter-rater agreement)
  - Empirical baseline calibration (3.4-3.6 range vs hardcoded 5.0)
  - Evidence-based penalty multipliers (2-3× less severe than original)
- **Output:** `ALGORITHM.md` with full methodology
- **Ready for:** Paper resubmission
- **Commit:** `a99f9a2`, `6c7be1d` (Phase 2 implementation + security hardening)

### Phase 3: Python SDK ✅
- **Status:** Complete, production-ready
- **Features:**
  - `BamiPClient` class (local and remote endpoints)
  - `analyze()`, `analyze_batch()`, `get_health()`, `analyze_file()`, `export_results()`
  - Full type hints, docstrings, error handling
  - Smart batching with rate limit awareness
- **Examples:** 3 example scripts (basic, batch, file processing)
- **Documentation:** `biaslense/sdk/README.md`
- **Ready for:** `pip install biaslense`
- **Commit:** `2857492` (feat: Add Python SDK)

### Phase 3.5: Security & Portability ✅
- **Status:** Complete
- **Features:**
  - REST API key handling (os.environ with Streamlit fallback)
  - Portable paths (environment variables, no hardcoded /Users/...)
  - Data quality validation (detects silent NaN coercion)
  - Stable prompt ID hashing (eliminates collisions)
- **Commit:** `ac24ddd` (refactor: Security hardening)

---

## Upcoming Phases

### Phase 1.5: OpenAI Integration (DEFERRED) ⚠️
**Duration:** 30 min  
**Priority:** 🔴 CRITICAL (blocks improved response generation)

**What to do:**
1. Go to Railway dashboard
2. Set environment variable: `OPENAI_API_KEY=sk-...`
3. Restart API
4. Test: `/analyze` should now return `improved_response` field

**Impact:**
- Improved response generation will actually work in production
- Users see before/after bias comparison
- Completes the BAMIP pipeline

**Status:** Deferred from Phase 1, should do before launch

---

### Phase 4: Launch & Community (2-3 weeks)
**Duration:** ~15 days part-time  
**Priority:** 🟢 HIGH (readies for users)

#### Step 4a: Paper Submission (3 days)
- Write cover letter:
  - Mention empirical validation (ALGORITHM.md)
  - Reference Krippendorff's α results (276 evaluations, 6 raters, 3 models)
  - Note that algorithm is production-ready
  - Link to GitHub repo + REST API for reproducibility
- Target venues:
  - Same journal (if open to resubmission)
  - ACM FAccT (Fairness, Accountability, Transparency)
  - EMNLP (Empirical Methods in NLP)
  - EACL (European Association for Computational Linguistics)

#### Step 4b: Publish SDK to PyPI (2-3 days)
- Create `setup.py` with metadata:
  ```python
  setup(
      name="biaslense",
      version="1.0.0",
      description="Detect and mitigate sociocultural bias in AI-generated text",
      author="Jaspreet Singh Ahluwalia",
      packages=find_packages(),
      install_requires=["requests", "pydantic"],
  )
  ```
- Build and publish:
  ```bash
  python setup.py sdist bdist_wheel
  python -m twine upload dist/*
  ```
- Result: `pip install biaslense` works for anyone

#### Step 4c: Write Launch Blog Post (2 days)
- Target: Medium, Dev.to, academic blogs
- Content:
  - "We empirically validated bias detection in LLMs (here's how)"
  - Problem: Algorithm credibility (arbitrary penalties)
  - Solution: 276 rater evaluations + Krippendorff's α
  - Results: Penalties 2-3× more realistic, algorithm ready for production
  - Call-to-action: Try on Streamlit, use SDK, read ALGORITHM.md
- Metrics to highlight:
  - 6 raters across 3 AI models
  - 276 evaluations total
  - Krippendorff's α computed per dimension
  - Empirical penalties replace researcher heuristics

#### Step 4d: Announce & Gather Feedback (1 week)
- Post on:
  - **Technical:** HackerNews, Reddit (r/MachineLearning, r/NLP, r/Python)
  - **Social:** Twitter/X, LinkedIn (tag fairness/ethics researchers)
  - **Academic:** Email fairness/NLP mailing lists
  - **Community:** United Sikhs Discord, relevant Slack communities
- Create feedback channels:
  - GitHub Issues (bug reports, feature requests)
  - GitHub Discussions (questions, ideas)
  - Google Form (quick feedback survey)
  - Email: bamiPipeline@jaspreetahluwalia.com
- Metrics to track:
  - GitHub stars
  - PyPI downloads
  - Blog views
  - Issues/feedback volume

---

### Phase 5: User Testing & Feedback Loop (4-6 weeks)
**Duration:** ~20 days (spread over 4-6 weeks)  
**Priority:** 🟢 HIGH (informs roadmap)

#### Goals
- Learn how users actually use BiasLens (web app vs SDK vs API?)
- Identify what's broken, what's missing
- Prioritize Phase 6 based on real needs

#### Actions
1. **Monitor Usage** (ongoing)
   - Check Streamlit analytics (daily active users)
   - Monitor Railway logs (API requests, error rates)
   - Track GitHub activity (issues, stars, discussions)
   - Monitor PyPI downloads

2. **Collect Feedback** (week 1-2)
   - Review all GitHub issues and discussions
   - Send feedback survey to early users
   - Interview 3-5 active users (30 min calls)
   - Monitor social media mentions

3. **Analyze Patterns** (week 3)
   - Aggregate feedback by category:
     - Bug reports → Fix immediately
     - Feature requests → Prioritize by frequency
     - Bias types → What groups are people analyzing?
     - Use cases → How are people actually using it?

4. **Document Learnings** (week 4)
   - Update GitHub roadmap with user priorities
   - Share findings in public update
   - Adjust Phase 6 based on what you learned

#### Key Questions to Answer
- Which interface do users prefer? (web app vs SDK vs API)
- What bias types beyond Sikh are most important?
- What's broken? (bugs, accuracy issues, speed)
- What's missing? (features, support, documentation)
- Who are your users? (researchers, developers, advocates, companies)

#### Expected Outcomes
- 10-50 GitHub stars
- 10-20 SDK PyPI downloads
- 5-10 documented bugs/feature requests
- 3-5 feedback interviews completed
- Clear picture of Phase 6 priorities

---

### Phase 6: Scale & Optimize (8-12 weeks)
**Duration:** Varies by sub-phase  
**Priority:** 🟡 MEDIUM (based on Phase 5 feedback)

#### Phase 6a: Bias Detection for Other Groups (2-3 weeks each)
**Why:** Current tool is Sikh-specific; users want to detect bias against other communities

**Process (per group):**
1. Get community input on what bias looks like
2. Collect ~200 AI-generated responses
3. Get 2-3 community members to rate them
4. Run same calibration as Phase 2
5. Add to SDK: `client.analyze(ai_response, model="muslim")` vs `model="sikh"` etc.

**Candidate Groups (in priority order):**
1. Muslim communities (most similar to Sikh case)
2. East Asian groups (common stereotypes in AI)
3. LGBTQ+ identities
4. Indigenous peoples
5. African diaspora communities

**Timeline:** 1 group every 1-2 months = 5-10 groups in 6-12 months

**Impact:** 10-100x expansion of use cases

#### Phase 6b: Performance & Scale (1-2 weeks)
**Why:** Handle more users without crashing

**Improvements:**
- Add response caching (same prompt → cached result)
- Optimize local pipeline (profile slow spots, optimize)
- Add async support to SDK (for high-throughput scenarios)
- Batch processing improvements (parallel processing where safe)

**Impact:** Handle 10x more requests; faster response times

#### Phase 6c: Advanced Features (2-4 weeks each, pick based on feedback)
**Why:** Integrate BiasLens into workflows users already have

**Options:**
- **CLI Tool**: `biaslense analyze --input file.csv --output results.csv`
- **Git Integration**: Pre-commit hook to check PR descriptions for bias
- **CI/CD Integration**: GitHub Actions to scan pull requests
- **Slack Bot**: Real-time bias detection in messages
- **Browser Extension**: Check text on any website
- **Google Sheets Add-on**: Analyze data directly in spreadsheets

**Impact:** 2-5x increase in accessibility

---

### Phase 7: Ecosystem & Community (3-6 months, ongoing)
**Duration:** Long-term, 5-10 hours/month  
**Priority:** 🟡 MEDIUM (strengthens impact)

#### Actions
1. **Academic Publication**
   - Publish methodology paper on SDK + tool design
   - Target: ACM Transactions on Computing for Social Good, AI Ethics journals

2. **Partnerships**
   - Universities: Integrate into CS ethics courses
   - Nonprofits: Collaborate with United Sikhs, CAIR, other advocacy groups
   - Companies: Bias detection for content moderation, hiring tools

3. **Community**
   - Create contributor guide for adding new bias models
   - Host quarterly workshops/webinars
   - Build public roadmap (GitHub Project board)

4. **Sustainability**
   - Explore grants (NSF, Mozilla, etc.)
   - Engage corporate sponsors (AI companies interested in fairness)
   - Build community fund for ongoing development

---

## Timeline Summary

| Phase | Duration | Start | End | Effort | Status |
|-------|----------|-------|-----|--------|--------|
| **1** | — | ✅ | ✅ | — | Complete |
| **2** | — | ✅ | ✅ | — | Complete |
| **3** | — | ✅ | ✅ | — | Complete |
| **3.5** | — | ✅ | ✅ | — | Complete |
| **1.5** | 30 min | NOW | Week 1 | 🟢 Trivial | Deferred |
| **4** | 2 weeks | Week 1 | Week 3 | 🟢 Low | Next |
| **5** | 4 weeks | Week 3 | Week 7 | 🟡 Medium | Planned |
| **6a** | 2-3 weeks | Week 7 | Ongoing | 🟡 Medium | Feedback-driven |
| **6b** | 1-2 weeks | Week 8 | Planned | 🟡 Medium | Feedback-driven |
| **6c** | 2-4 weeks | Week 10 | Planned | 🟠 High | Feedback-driven |
| **7** | 3-6 months | Week 8 | Ongoing | 🟡 Medium | Long-term |

**Total to "sustainable, user-driven product": 3-6 months part-time**

---

## Success Metrics

### By End of Month 1 (Phase 4)
- ✅ Paper resubmitted to journal/conference
- ✅ SDK published to PyPI
- ✅ Blog post published (100+ views)
- ✅ Announced on social/academic channels
- ✅ 5-20 GitHub stars
- ✅ First issues/feedback coming in

### By End of Month 3 (Phase 5)
- ✅ 50+ GitHub stars
- ✅ 20-50 PyPI downloads
- ✅ 5-10 documented bugs/features
- ✅ 3+ user interviews completed
- ✅ Phase 6 priorities identified
- ✅ Usage patterns understood (web vs SDK vs API)

### By End of Month 6+ (Phase 6)
- ✅ 1-2 additional bias models (Muslim, East Asian)
- ✅ 100+ GitHub stars
- ✅ 100+ monthly PyPI downloads
- ✅ Real users in production (researchers, nonprofits, companies)
- ✅ Sustainable development cycle
- ✅ Community contributions happening

---

## Decision Framework

### I should work on Phase X if:

**Phase 1.5 (OpenAI):** You want improved responses to work in production. Do this first (30 min).

**Phase 4a (Paper):** You care about academic credibility. Do immediately after 1.5.

**Phase 4b (PyPI):** You want more users. Do after 4a.

**Phase 5 (Feedback):** You want to know what to build next. Do continuously.

**Phase 6a (Other groups):** Users are asking for it. Prioritize based on Phase 5 feedback.

**Phase 6b (Performance):** Hitting scale problems (slow API, timeouts). Do when needed.

**Phase 6c (Features):** Users asking for specific integrations. Do based on feedback.

**Phase 7 (Ecosystem):** Long-term sustainability matters. Start planning in Month 3.

---

## How to Use This Roadmap

1. **This week:** Do Phase 1.5 (30 min) + Phase 4a (3 days)
2. **Next week:** Do Phase 4b-4d (all simultaneously, 1 week total)
3. **Month 2:** Run Phase 5 feedback loop continuously
4. **Month 3+:** Pick Phase 6 based on what Phase 5 taught you

**Share this roadmap** with:
- Collaborators (if any)
- Community members (on GitHub)
- Grant reviewers (if pursuing funding)
- Potential partners (universities, nonprofits)

---

## Questions to Revisit Monthly

1. Are we getting the users we expected?
2. What are the top 3 feature requests?
3. Are there bugs we should prioritize?
4. Does Phase 5 feedback change our Phase 6 priorities?
5. Should we pursue partnerships/funding?

---

**Last Updated:** May 31, 2026  
**Next Review:** June 30, 2026  
**Maintained By:** Jaspreet Singh Ahluwalia
