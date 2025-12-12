# EB-1A Agent System - Quick Start Guide

Get up and running with the new agent-based architecture in 5 minutes.

## 🎯 What's New

The system has been redesigned with:
- **Strict folder structure** with exact name matching
- **Specialized AI agents** for each EB-1A criterion
- **LangChain/LangGraph** orchestration
- **Streamlit UI** for testing
- **Selective folder processing** (1-2 folders for quick tests)

## 📋 Prerequisites

1. **Python 3.11+** installed
2. **Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Tesseract OCR** for document parsing:
   - Windows: Download from [GitHub releases](https://github.com/tesseract-ocr/tesseract/releases)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

## 🚀 Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd C:\aurigo\backend
pip install -r requirements.txt
```

This will install:
- LangChain & LangGraph (agent framework)
- Streamlit (testing UI)
- Docling (document parser)
- Google Generative AI (Gemini)
- All existing dependencies

### Step 2: Configure Environment

Create `.env` file in backend folder:

```bash
cd C:\aurigo\backend
copy .env.example .env
```

Edit `.env` and add your API key:

```env
# LLM Provider
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp

# Optional Claude (for refinement)
CLAUDE_API_KEY=your-claude-api-key-optional
USE_CLAUDE_POLISH=false

# Database
DATABASE_URL=sqlite:///./aurigo.db
```

### Step 3: Verify Folder Structure

Check that Pranav case data follows the strict structure:

```
C:\aurigo\Pranav_Case_Data\
├── Case_Overview.docx (optional)
└── Evidence\
    ├── 1_Critical_role\
    ├── 2_Original_contribution\
    ├── 3_High_salary\
    ├── 4_Judging\
    ├── 5_Membership\
    ├── 6_Awards\
    ├── 7_Authorship\
    ├── 8_Press\
    ├── 9_Final_merits\
    ├── 10_Performing_Arts\
    └── Personal\
```

**Important**: Folder names must match EXACTLY (case-sensitive).

## 🧪 Testing with Streamlit UI

### Start the Streamlit App

```bash
cd C:\aurigo\streamlit_app
python run.py
```

Or:

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Test Workflow

1. **Configure (Sidebar)**
   - Provider: Gemini
   - API Key: Paste your Gemini API key

2. **Folder Selection Tab**
   - Path: `C:\aurigo\Pranav_Case_Data`
   - Click "Validate"
   - Select folders: ✅ 1_Critical_role, ✅ 2_Original_contribution
   - (Start with 2 folders for quick test)

3. **Processing Tab**
   - Beneficiary: "Pranav Kumar"
   - Field: "Artificial Intelligence"
   - Click "Start Processing"
   - Wait 1-2 minutes

4. **Results Tab**
   - View agent results
   - Check confidence scores
   - Preview generated letter
   - Download outputs

## 📊 What to Expect

### Processing Time
- 1 folder (10 docs): ~30-60 seconds
- 2 folders (20 docs): ~1-2 minutes

### Agent Results

Each agent will:
1. ✅ Parse all documents with Docling
2. ✅ Analyze evidence with Gemini
3. ✅ Extract key facts
4. ✅ Create exhibits (C-1, C-2, D-1, D-2...)
5. ✅ Generate letter section
6. ✅ Calculate confidence score

### Generated Outputs

1. **Attorney Letter**
   - Introduction
   - Executive summary
   - Criterion sections with inline citations
   - Conclusion
   - Complete exhibit index

2. **Exhibit Index**
   - Grouped by criterion (Groups C, D, E...)
   - Sequential numbering (C-1, C-2, D-1, D-2...)
   - Titles and descriptions

## 🔍 Verification Checklist

After processing, verify:

- [ ] All selected folders processed successfully
- [ ] Exhibits created with proper IDs (C-1, D-1, etc.)
- [ ] Letter sections generated for each criterion
- [ ] Inline citations present (e.g., "See Exhibit C-3")
- [ ] Exhibit index complete at end of letter
- [ ] Key facts extracted from documents
- [ ] Confidence scores calculated (>0.5 is good)

## 🐛 Troubleshooting

### Issue: "Module not found" errors
**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "API key invalid"
**Solution**:
- Verify API key is correct
- Check you're using Gemini key (not Claude)
- Test key at [Google AI Studio](https://makersuite.google.com/)

### Issue: "Folder validation failed"
**Solution**:
- Check folder names match EXACTLY (case-sensitive)
- Ensure `Evidence` folder exists
- Verify at least 3 folders have documents

### Issue: "Docling parsing failed"
**Solution**:
- Install Tesseract OCR
- Verify documents are in supported formats
- Check file permissions

### Issue: "Agent processing timeout"
**Solution**:
- Reduce number of selected folders
- Check API rate limits
- Verify network connection

## 📁 Project Structure

```
C:\aurigo\
├── backend/
│   ├── app/
│   │   ├── agents/                    # NEW
│   │   │   ├── base_agent.py         # Base agent class
│   │   │   ├── exhibit_manager_agent.py
│   │   │   └── criterion_agents/
│   │   │       ├── critical_role_agent.py
│   │   │       └── original_contribution_agent.py
│   │   ├── services/
│   │   │   ├── strict_folder_validator.py  # NEW
│   │   │   ├── agent_orchestrator.py       # NEW
│   │   │   └── ... (existing services)
│   │   └── ... (existing code)
│   └── requirements.txt               # UPDATED
│
├── streamlit_app/                     # NEW
│   ├── app.py                        # Streamlit UI
│   ├── run.py                        # Startup script
│   └── README.md
│
├── docs/
│   ├── agent_architecture_plan.md    # Architecture spec
│   └── QUICKSTART.md                 # This file
│
└── Pranav_Case_Data/                 # Sample data
    └── Evidence/
```

## 🎓 Understanding the Agent System

### Agent Flow

```
User selects folders
    ↓
StrictFolderValidator
  - Validates exact folder names
  - Checks minimum 3 folders with files
    ↓
AgentOrchestrator (LangGraph)
  - Initializes ExhibitManagerAgent
  - Creates CriterionAgents for selected folders
    ↓
Parallel Processing
  - CriticalRoleAgent → Group C exhibits
  - OriginalContributionAgent → Group D exhibits
    ↓
Each Agent:
  1. Parses docs with Docling
  2. Analyzes with Gemini
  3. Extracts facts
  4. Requests exhibit IDs
  5. Generates letter section
    ↓
LetterOrchestrator
  - Compiles all sections
  - Adds exhibit index
  - Formats final letter
    ↓
Results & Download
```

### Exhibit System

- **Group A**: Background
- **Group B**: Field description
- **Group C**: Critical Role (1_Critical_role)
- **Group D**: Original Contributions (2_Original_contribution)
- **Group E**: High Salary (3_High_salary)
- **Group F**: Judging (4_Judging)
- **Group G**: Membership (5_Membership)
- **Group H**: Awards (6_Awards)
- **Group I**: Authorship (7_Authorship)
- **Group J**: Press (8_Press)
- **Group K**: Final Merits (9_Final_merits)
- **Group L**: Performing Arts (10_Performing_Arts)

Format: `{GroupLetter}-{Number}` (e.g., C-1, C-2, D-1, D-2...)

## 🚧 Current Limitations

1. **Implemented Agents**: Only 2 criterion agents (Critical Role, Original Contribution)
2. **Remaining Agents**: 8 criterion agents + BackgroundAgent need implementation
3. **DOCX Export**: Not yet implemented (only Markdown output)
4. **Real-time Updates**: Agent status not streamed (batch results only)
5. **Database Integration**: Streamlit UI bypasses database (direct processing)

## 🔜 Next Steps

1. **Immediate Testing** (Now)
   - Test with 1_Critical_role + 2_Original_contribution
   - Verify exhibit creation and citations
   - Check letter quality

2. **Implement Remaining Agents** (Next)
   - HighSalaryAgent
   - JudgingAgent
   - MembershipAgent
   - AwardsAgent
   - AuthorshipAgent
   - PressAgent
   - FinalMeritsAgent
   - PerformingArtsAgent

3. **Add Support Agents**
   - BackgroundAgent (Personal folder)
   - LetterOrchestratorAgent (final compilation)

4. **Enhance UI**
   - Real-time agent status updates
   - WebSocket progress streaming
   - Agent-specific visualizations

5. **Integration**
   - Connect to Next.js frontend
   - Add database persistence
   - Implement DOCX export
   - Deploy to production

## 💡 Tips for Best Results

1. **Start Small**: Test with 1-2 folders first
2. **Good Documents**: Use high-quality PDFs (not scanned images)
3. **Organize Files**: Ensure documents are in correct criterion folders
4. **API Quota**: Monitor Gemini API usage (free tier limits)
5. **Review Results**: Check confidence scores and key facts extracted

## 📚 Additional Resources

- **Architecture Plan**: `docs/agent_architecture_plan.md`
- **Streamlit README**: `streamlit_app/README.md`
- **Base Agent Code**: `backend/app/agents/base_agent.py`
- **Orchestrator Code**: `backend/app/services/agent_orchestrator.py`

## ✅ Ready to Test!

You're all set! Run:

```bash
cd C:\aurigo\streamlit_app
python run.py
```

And start processing your first case with the new agent system! 🚀

## 💬 Feedback

After testing:
- Note what works well
- Identify issues or improvements
- Test with different folder combinations
- Verify exhibit citations in generated letter

---

**Happy Testing!** 🎉
