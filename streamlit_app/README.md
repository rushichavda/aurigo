# EB-1A Agent System - Streamlit UI

Testing interface for the agent-based EB-1A letter generation system.

## Features

- **Folder Validation**: Validate case folder structure against strict requirements
- **Folder Selection**: Choose which criterion folders to process (1-2 for testing)
- **Real-time Processing**: Monitor agent progress and status
- **Letter Preview**: View generated attorney letter
- **Exhibit Index**: Review all exhibits with descriptions
- **Download Results**: Export letter and exhibit index

## Setup

1. **Install Dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure API Key**:
   - Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Or get a Claude API key from [Anthropic Console](https://console.anthropic.com/)

## Running the App

### Option 1: Using the run script
```bash
cd streamlit_app
python run.py
```

### Option 2: Direct streamlit command
```bash
cd streamlit_app
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Usage

### 1. Configure Settings (Sidebar)

- **LLM Provider**: Choose between Gemini (recommended) or Claude
- **API Key**: Enter your API key for the selected provider

### 2. Folder Selection Tab

1. Enter the path to your case folder (e.g., `C:/aurigo/Pranav_Case_Data`)
2. Click "Validate" to check folder structure
3. Select which criterion folders to process
   - Start with 1-2 folders for quick testing
   - Default selection: Critical Role + Original Contribution

### 3. Processing Tab

1. Enter beneficiary name
2. Enter field of expertise
3. Click "Start Processing"
4. Monitor progress in real-time

### 4. Results Tab

View:
- Summary metrics (criteria processed, exhibits, errors)
- Agent results with confidence scores
- Complete letter preview
- Exhibit index table
- Download buttons for letter and exhibit index

## Folder Structure Requirements

Your case folder must follow this exact structure:

```
YourCaseFolder/
├── Case_Overview.docx (optional)
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

**Important**: Folder names must match exactly (case-sensitive).

## Testing with Sample Data

Use the provided Pranav case data:

1. Path: `C:/aurigo/Pranav_Case_Data`
2. Select folders: `1_Critical_role`, `2_Original_contribution`
3. Beneficiary: "Pranav Kumar"
4. Field: "Artificial Intelligence"
5. Start processing

## Agent System

The system uses specialized AI agents:

### Implemented Agents
- **CriticalRoleAgent**: Analyzes leading/critical role evidence
- **OriginalContributionAgent**: Analyzes original contributions evidence
- **ExhibitManagerAgent**: Manages exhibit IDs and tracking

### Coming Soon
- HighSalaryAgent
- JudgingAgent
- MembershipAgent
- AwardsAgent
- AuthorshipAgent
- PressAgent
- FinalMeritsAgent
- PerformingArtsAgent

## Architecture

```
User Input
    ↓
StrictFolderValidator (validates structure)
    ↓
AgentOrchestrator (coordinates workflow)
    ↓
Criterion Agents (process in parallel)
    ↓  ↓  ↓
ExhibitManagerAgent (tracks exhibits)
    ↓
Letter Generation
    ↓
Results & Export
```

## Troubleshooting

### "Module not found" errors
```bash
cd backend
pip install -r requirements.txt
```

### "API key invalid"
- Check that your API key is correct
- Verify you're using the right provider (Gemini vs Claude)
- Ensure API key has proper permissions

### "Folder validation failed"
- Check folder names match exactly (case-sensitive)
- Ensure Evidence folder exists
- Verify at least 3 criterion folders have files

### "Agent processing failed"
- Check logs in terminal for detailed error
- Verify documents are in supported formats
- Ensure sufficient API quota/credits

## Performance

- Processing time depends on:
  - Number of folders selected
  - Number of documents per folder
  - LLM provider speed

- Typical processing times:
  - 1 folder (10 docs): ~30-60 seconds
  - 2 folders (20 docs): ~1-2 minutes
  - Full case (100+ docs): ~5-10 minutes

## Cost Estimation

### Gemini 2.5 Flash (Recommended)
- ~$0.05-0.10 per folder
- ~$0.40 for complete case

### Claude Sonnet 4
- ~$0.50-1.00 per folder
- ~$3-5 for complete case

## Next Steps

After testing with Streamlit:
1. Implement remaining criterion agents
2. Add BackgroundAgent for Personal folder
3. Add LetterOrchestratorAgent for final compilation
4. Integrate with Next.js frontend
5. Add DOCX export functionality
6. Implement agent status WebSocket updates

## Support

For issues or questions:
1. Check backend logs in terminal
2. Review agent_architecture_plan.md
3. Verify folder structure with validator
4. Test with sample data first

## Development

To modify agents:
- Agents: `backend/app/agents/criterion_agents/`
- Base class: `backend/app/agents/base_agent.py`
- Orchestrator: `backend/app/services/agent_orchestrator.py`
- Validator: `backend/app/services/strict_folder_validator.py`

## License

MIT License - See LICENSE file for details
