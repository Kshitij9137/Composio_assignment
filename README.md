# App Research Agent – Composio Take-home

An automated research agent that analyzes 100 SaaS apps to extract authentication methods, self-serve status, API surface, and buildability for AI agent toolkits. Built for the Composio AI Product Ops Intern assignment.

---

## 📊 Live Case Study

**[View the interactive dashboard →](https://<your-username>.github.io/<repo-name>/)**

The dashboard presents:
- 5 headline findings
- 78.8% → 100% accuracy improvement through human verification
- Searchable, sortable table of all 100 apps

---

## 🏗️ Architecture

The agent works in **two tiers**:

1. **Tier 1 – Composio Catalog Check**  
   Checks if Composio already ships a toolkit for the app. If found, we get ground-truth auth schemes (OAuth2, API Key, etc.) – no LLM call needed.

2. **Tier 2 – Gemini Research**  
   For apps not in the catalog, Gemini researches:
   - Auth methods (OAuth2, API Key, Basic, Token)
   - Self-serve vs gated (can a developer get credentials freely?)
   - API surface (REST, GraphQL, both, or none)
   - Buildability (can we build an agent toolkit today?)
   - Evidence URLs (documentation links)

**Verification Loop** (Phase 4):  
20 apps hand-checked against real documentation. Accuracy improved from **78.8% → 100%**.

---

## 📈 Key Findings

| Metric | Value |
|--------|-------|
| **Self-serve apps** | 81/100 (81%) |
| **Buildable today** | 84/100 (84%) |
| **Composio toolkits already exist** | 60/100 (60%) |
| **MCP servers exist** | 14/100 (14%) |
| **Dominant auth** | OAuth2 (61%) |

### Category Breakdown

| Category | Self-Serve | Buildable |
|----------|------------|-----------|
| Communications & Messaging | 100% | 100% |
| Marketing, Ads, Email & Social | 100% | 100% |
| Developer, Infra & Data | 100% | 100% |
| Productivity & Project Mgmt | 100% | 100% |
| CRM & Sales | 90% | 90% |
| Support & Helpdesk | 90% | 90% |
| Data, SEO & Scraping | 80% | 90% |
| Ecommerce | 60% | 80% |
| Finance & Fintech | 50% | 50% |
| AI, Research & Media-native | 40% | 40% |

---

## 🔧 How to Run the Agent

### Prerequisites
- Python 3.10+
- Composio account ([composio.dev](https://composio.dev))
- Gemini API key ([Google AI Studio](https://makersuite.google.com/app/apikey))

### Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd <repo-name>

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your COMPOSIO_API_KEY and GEMINI_API_KEY