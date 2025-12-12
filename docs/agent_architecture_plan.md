# EB-1A Agent-Based Pipeline Architecture

## Overview
Redesigned pipeline using specialized AI agents for each EB-1A criterion, with strict folder structure validation and agent orchestration.

---

## 1. Strict Folder Structure

### Required Structure
```
uploaded.zip
└── [AnyFolderName]/
    ├── Case_Overview.docx (or .pdf)
    ├── Statement_of_Intent.docx (optional)
    └── Evidence/
        ├── 1_Critical_role/
        ├── 2_Original_contribution/
        ├── 3_High_salary/
        ├── 4_Judging/
        ├── 5_Membership/
        ├── 6_Awards/
        ├── 7_Authorship/
        ├── 8_Press/
        ├── 9_Final_merits/
        ├── 10_Performing_Arts/
        └── Personal/
```

### Validation Rules
- **Exact match required**: Folder names must match exactly (case-sensitive)
- **Minimum criteria**: At least 3 criterion folders must contain files
- **Allowed formats**: PDF, DOCX, JPG, PNG, TIFF, PPT, PPTX, HTML
- **No flexibility**: LLM-based folder mapping removed

---

## 2. Agent Architecture

### Agent Types

#### A. Criterion Agents (10 specialized agents)
Each agent specializes in one EB-1A criterion:

1. **CriticalRoleAgent** - `1_Critical_role/`
2. **OriginalContributionAgent** - `2_Original_contribution/`
3. **HighSalaryAgent** - `3_High_salary/`
4. **JudgingAgent** - `4_Judging/`
5. **MembershipAgent** - `5_Membership/`
6. **AwardsAgent** - `6_Awards/`
7. **AuthorshipAgent** - `7_Authorship/`
8. **PressAgent** - `8_Press/`
9. **FinalMeritsAgent** - `9_Final_merits/`
10. **PerformingArtsAgent** - `10_Performing_Arts/`

#### B. Support Agents

11. **BackgroundAgent** - `Personal/` folder + `Case_Overview.docx`
    - Extracts beneficiary background
    - Field of expertise
    - Career timeline
    - Key qualifications

12. **ExhibitManagerAgent**
    - Tracks all exhibits across agents
    - Assigns exhibit IDs (A-1, A-2, B-1, B-2...)
    - Maintains exhibit index
    - Generates exhibit list

13. **LetterOrchestratorAgent**
    - Coordinates all agents
    - Compiles final letter
    - Ensures proper citations
    - Maintains legal format

---

## 3. Agent Capabilities

### Each Criterion Agent Must:

1. **Document Processing**
   - Use Docling to parse all files in folder
   - Handle multi-format: PDF, images, PPT, DOCX
   - OCR for scanned documents
   - Extract text, tables, metadata

2. **Information Analysis**
   - Identify document types (certificate, letter, award, publication, etc.)
   - Extract key facts relevant to criterion
   - Identify entities (names, organizations, dates, amounts)
   - Determine document significance
   - Validate criterion compliance

3. **Exhibit Preparation**
   - Assign exhibit IDs through ExhibitManagerAgent
   - Create descriptive exhibit titles
   - Write exhibit descriptions
   - Order exhibits logically

4. **Letter Section Generation**
   - Write criterion introduction
   - Analyze evidence with specific examples
   - Cite exhibits properly: "As evidenced in Exhibit C-3..."
   - Provide legal argumentation
   - Connect to "extraordinary ability" standard

---

## 4. Criterion-Specific Agent Behavior

### 1. CriticalRoleAgent - Leading/Critical Role
**Focus**: Employment in critical capacity in distinguished organizations

**Key Analysis**:
- Job titles and seniority level
- Organization reputation/prestige
- Scope of responsibility
- Impact on organization
- Leadership evidence
- Organizational charts
- Recommendation letters from executives

**Expected Documents**: Offer letters, employment letters, org charts, job descriptions

---

### 2. OriginalContributionAgent - Original Scientific/Business Contributions
**Focus**: Contributions of major significance to the field

**Key Analysis**:
- Research publications and citations
- Patents and inventions
- Novel methodologies/techniques
- Industry adoption of contributions
- Expert testimonials about impact
- Awards for contributions
- Adoption by other researchers/companies

**Expected Documents**: Research papers, patents, citation reports, impact letters

---

### 3. HighSalaryAgent - High Remuneration
**Focus**: High salary/compensation relative to field

**Key Analysis**:
- Salary amounts and currency
- Comparison to industry standards
- Compensation packages (equity, bonuses)
- Salary surveys and benchmarks
- Years of experience vs. compensation
- Geographic adjustments

**Expected Documents**: Pay stubs, offer letters, W2s, compensation statements, industry salary surveys

---

### 4. JudgingAgent - Judging Others' Work
**Focus**: Served as judge of work of others in field

**Key Analysis**:
- Conference program committees
- Journal peer review invitations
- Grant review panels
- Competition judging
- PhD thesis committees
- Frequency and prestige of judging

**Expected Documents**: Review invitations, program committee listings, thank you letters

---

### 5. MembershipAgent - Professional Memberships
**Focus**: Membership in associations requiring outstanding achievements

**Key Analysis**:
- Membership selectivity (acceptance rate)
- Nomination requirements
- Membership criteria rigor
- Association prestige
- Membership level (fellow, senior member, etc.)
- Invitation evidence

**Expected Documents**: Membership certificates, invitation letters, association criteria, acceptance letters

---

### 6. AwardsAgent - Awards and Prizes
**Focus**: Nationally/internationally recognized prizes

**Key Analysis**:
- Award prestige and recognition level
- Selection criteria and process
- Nomination requirements
- Award history and past recipients
- Geographic scope (national vs. international)
- Competitive nature

**Expected Documents**: Award certificates, nomination letters, award descriptions, news articles

---

### 7. AuthorshipAgent - Scholarly Authorship
**Focus**: Authored scholarly articles in professional journals

**Key Analysis**:
- Publication venues (journal quality, impact factor)
- Author position (first, corresponding, last)
- Citation counts
- Publication frequency
- Peer review status
- Journal selectivity
- Field relevance

**Expected Documents**: Published papers, journal covers, citation reports, impact metrics

---

### 8. PressAgent - Published Material About You
**Focus**: Media coverage about the applicant's work

**Key Analysis**:
- Publication reach and circulation
- Media prestige
- Content focus on applicant
- Frequency of coverage
- National vs. international media
- Expert commentary vs. profile

**Expected Documents**: News articles, magazine features, press releases, media mentions

---

### 9. FinalMeritsAgent - Final Merits Determination
**Focus**: Overall demonstration of being at top of field

**Key Analysis**:
- Synthesize all criteria evidence
- Demonstrate "sustained acclaim"
- Show "top of field" status
- Connect individual achievements to bigger picture
- Address Kazarian two-step analysis
- Provide holistic argument

**Expected Documents**: Comprehensive statements, expert opinion letters, comparative analysis

---

### 10. PerformingArtsAgent - Commercial Success in Performing Arts
**Focus**: Commercial success in performing arts (if applicable)

**Key Analysis**:
- Box office revenues
- Record sales / streaming numbers
- Concert ticket sales
- Awards and recognition
- Media coverage of performances
- Contract values
- Audience reach

**Expected Documents**: Sales reports, concert receipts, streaming analytics, contracts

---

## 5. Agent Orchestration Flow

### Phase 1: Upload & Validation (5%)
```
User uploads ZIP
  ↓
Extract and validate exact folder structure
  ↓
Verify folder names match hardcoded list
  ↓
Check minimum 3 criterion folders have files
  ↓
Create case record with status "validated"
```

### Phase 2: Background Processing (10%)
```
BackgroundAgent activates
  ↓
Parse Case_Overview.docx + Personal/ folder
  ↓
Extract: name, field, background, qualifications
  ↓
Store beneficiary_info
```

### Phase 3: Criterion Agents Parallel Processing (15-70%)
```
For each criterion folder with files:
  ↓
  Activate corresponding CriterionAgent
  ↓
  Agent processes ALL files:
    - Parse with Docling
    - Extract information
    - Analyze relevance
    - Identify key facts
  ↓
  Agent requests exhibit IDs from ExhibitManagerAgent
  ↓
  Agent generates exhibit metadata:
    - Title
    - Description
    - Key points
  ↓
  Agent drafts letter section:
    - Criterion introduction
    - Evidence analysis with citations
    - Legal argumentation
  ↓
  Return: {
    criterion: "Critical Role",
    documents_processed: 12,
    exhibits: [Exhibit objects],
    letter_section: "...",
    key_facts: [...],
    confidence_score: 0.85
  }
```

**All criterion agents run in parallel for efficiency**

### Phase 4: Final Merits Analysis (75%)
```
FinalMeritsAgent activates
  ↓
Analyze aggregate data from all agents
  ↓
Synthesize holistic argument
  ↓
Generate "Final Merits" section
```

### Phase 5: Letter Compilation (85%)
```
LetterOrchestratorAgent activates
  ↓
Collect outputs from all agents
  ↓
Generate letter structure:
  1. Introduction (attorney credentials)
  2. Executive Summary
  3. Background (from BackgroundAgent)
  4. Field Importance
  5. Criterion Sections (from each CriterionAgent)
  6. Final Merits Determination
  7. Conclusion
  ↓
Ensure all exhibit citations are valid
  ↓
Format with proper legal structure
```

### Phase 6: Export (95%)
```
ExhibitManagerAgent generates exhibit index
  ↓
DocumentExporter creates DOCX files:
  - Attorney_Letter.docx
  - Exhibit_Index.docx
  - Case_Metadata.json
  ↓
Status: "completed" (100%)
```

---

## 6. Agent Communication Protocol

### Agent State Management
Each agent maintains:
- `agent_id`: Unique identifier
- `status`: idle | active | completed | failed
- `progress`: 0-100
- `current_task`: Description of current work
- `outputs`: Results dictionary

### Inter-Agent Messaging
```python
# Agent requests exhibit ID
exhibit_id = await exhibit_manager_agent.request_exhibit_id(
    group_letter='C',
    title='Employment Letter from Google',
    description='Letter confirming critical role as AI Research Lead'
)

# Agent reports completion
await orchestrator.report_completion(
    agent_id='critical_role_agent',
    outputs={
        'exhibits': [...],
        'letter_section': '...',
        'confidence': 0.9
    }
)
```

---

## 7. Exhibit Management System

### Exhibit Grouping
- **Group A**: Background exhibits (Case Overview, Personal docs)
- **Group B**: Field exhibits (Statement of Intent, field descriptions)
- **Groups C-L**: One group per criterion (if evidence present)
  - C: Critical Role
  - D: Original Contribution
  - E: High Salary
  - F: Judging
  - G: Membership
  - H: Awards
  - I: Authorship
  - J: Press
  - K: Final Merits
  - L: Performing Arts

### Exhibit ID Format
`{GroupLetter}-{SequentialNumber}`
Examples: A-1, A-2, C-1, C-2, D-1

### Exhibit Metadata
```python
{
    "exhibit_id": "C-3",
    "group_letter": "C",
    "number": 3,
    "title": "Employment Verification Letter - Google Inc.",
    "description": "Official letter confirming role as Senior AI Research Lead...",
    "file_path": "1_Critical_role/google_employment_letter.pdf",
    "criterion": "Critical Role",
    "document_type": "Employment Letter",
    "key_points": [
        "Confirms leadership of 20-person team",
        "Developed core ML algorithms",
        "Impact on 1B+ users"
    ]
}
```

---

## 8. Letter Format & Citations

### Citation Examples
- "As demonstrated in Exhibit C-3, [Beneficiary] served as Senior AI Research Lead at Google Inc., leading a team of 20 researchers..."
- "Exhibit D-5 shows [Beneficiary]'s patent has been cited over 500 times, indicating major significance..."
- "The membership certificate (Exhibit G-1) confirms [Beneficiary] was elected as Fellow of the ACM, with only 1% acceptance rate..."

### Section Structure
```
III. Critical Role in Distinguished Organizations

[Beneficiary] has consistently held leading and critical roles in distinguished
organizations, demonstrating extraordinary ability through positions of significant
responsibility and impact.

A. Leadership at Google Inc.

As evidenced in Exhibit C-3, [Beneficiary] served as Senior AI Research Lead at
Google Inc. from 2020 to 2024. This position placed [Beneficiary] in a critical
role overseeing the development of core machine learning algorithms affecting over
1 billion users globally (Exhibit C-4). The scope of this responsibility is further
demonstrated by the organizational chart (Exhibit C-5) showing [Beneficiary]'s
direct reports and cross-functional leadership.

[Continue with more evidence...]
```

---

## 9. Streamlit UI Features

### Dashboard Components

1. **Upload Section**
   - Drag-and-drop ZIP upload
   - Instant folder structure validation
   - Visual checklist of required folders
   - File count per folder

2. **Processing Visualization**
   - Overall progress bar (0-100%)
   - Agent status grid:
     ```
     [BackgroundAgent: ✅ Completed]
     [CriticalRoleAgent: 🔄 Processing (8/12 files)]
     [AwardsAgent: 🔄 Processing (3/7 files)]
     [MembershipAgent: ⏳ Waiting]
     ```
   - Real-time log stream
   - Estimated time remaining

3. **Agent Details Panel**
   - Selected agent deep-dive
   - Files being processed
   - Extracted key facts (live)
   - Exhibits being created
   - Confidence scores

4. **Results Preview**
   - Generated letter preview (markdown)
   - Exhibit index table
   - Statistics:
     - Criteria matched: 7/10
     - Total exhibits: 43
     - Total documents: 67
     - Processing time: 4m 32s

5. **Export Section**
   - Download DOCX files
   - View metadata JSON
   - Export logs

---

## 10. Implementation Plan

### New Backend Files

```
backend/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py              # Base agent class
│   │   ├── background_agent.py         # Personal + Case Overview
│   │   ├── criterion_agents/
│   │   │   ├── critical_role_agent.py
│   │   │   ├── original_contribution_agent.py
│   │   │   ├── high_salary_agent.py
│   │   │   ├── judging_agent.py
│   │   │   ├── membership_agent.py
│   │   │   ├── awards_agent.py
│   │   │   ├── authorship_agent.py
│   │   │   ├── press_agent.py
│   │   │   ├── final_merits_agent.py
│   │   │   └── performing_arts_agent.py
│   │   ├── exhibit_manager_agent.py    # Exhibit coordination
│   │   └── letter_orchestrator_agent.py # Letter compilation
│   ├── services/
│   │   ├── strict_folder_validator.py  # Hardcoded validation
│   │   ├── agent_orchestrator.py       # Manages all agents
│   │   └── document_parser.py          # (existing, Docling)
│   └── routers/
│       └── agents.py                   # Agent status endpoints
├── streamlit_app/
│   ├── app.py                          # Main Streamlit UI
│   ├── components/
│   │   ├── upload_section.py
│   │   ├── progress_visualization.py
│   │   ├── agent_monitor.py
│   │   └── results_preview.py
│   └── utils/
│       └── api_client.py               # Backend API calls
└── requirements_streamlit.txt
```

---

## 11. Development Phases

### Phase 1: Foundation ✅ (Ready to Start)
- [x] Research EB-1A criteria
- [x] Design agent architecture
- [ ] Create strict folder validator
- [ ] Implement base agent class

### Phase 2: Agent Implementation
- [ ] Implement all 10 criterion agents
- [ ] Implement support agents (Background, ExhibitManager, LetterOrchestrator)
- [ ] Create agent orchestrator
- [ ] Add agent status endpoints

### Phase 3: Streamlit UI
- [ ] Build upload & validation UI
- [ ] Create progress visualization
- [ ] Implement agent monitoring
- [ ] Add results preview
- [ ] Enable DOCX download

### Phase 4: Testing & Refinement
- [ ] Test with Pranav case data
- [ ] Refine agent prompts
- [ ] Optimize parallel processing
- [ ] Validate letter quality
- [ ] Performance tuning

### Phase 5: Integration (Later)
- [ ] Integrate with Next.js UI
- [ ] Update API endpoints
- [ ] Deploy to production

---

## 12. Key Improvements Over Previous Design

1. **Strict Structure**: No ambiguity, user must follow exact format
2. **Specialized Agents**: Each agent deeply understands its criterion
3. **Parallel Processing**: All agents run simultaneously
4. **Better Citations**: Agents explicitly cite exhibits in text
5. **Visual Testing**: Streamlit UI shows everything in real-time
6. **Modular**: Easy to improve individual agents
7. **Confidence Scoring**: Agents report confidence in evidence quality
8. **Extensible**: Easy to add new agent capabilities

---

## Questions & Decisions

1. **LLM Provider**: Use Gemini 2.5 Flash for agents? Or Claude Code SDK agents?
2. **Parallel vs Sequential**: Should criterion agents run in parallel or sequentially?
3. **Agent Communication**: Direct calls or message queue?
4. **Caching**: Cache parsed documents between agent accesses?
5. **Error Handling**: How should agents handle insufficient evidence?

---

## Success Metrics

- **Accuracy**: Letter properly cites all exhibits
- **Completeness**: All documents processed and referenced
- **Quality**: Letter reads naturally with proper legal tone
- **Speed**: Complete processing in < 10 minutes for 100+ documents
- **Reliability**: 99%+ success rate on valid folder structures

---

**Status**: Architecture design complete, ready for implementation ✅
