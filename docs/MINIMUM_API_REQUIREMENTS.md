# Minimum API Requirements for Aurigo Baby Version

## TL;DR - You Need Just **1 API Key** 🎉

**For the basic pipeline to work, you need:**
- ✅ **Gemini API Key** (FREE tier available) - 2M tokens/month free
- ❌ ~~Claude API~~ - Optional (only for letter polishing)
- ❌ ~~OpenRouter API~~ - Legacy (not used in main pipeline)

---

## Current Pipeline Architecture

### **Full Processing Pipeline**

```
┌─────────────────────────────────────────────────────────┐
│  STEP 1: Folder Validation (NEW!)                      │
│  ────────────────────────────────────────────────────── │
│  - Detect Evidence folder       → Gemini 2.0 Flash     │
│  - Detect Case Overview          → Gemini 2.0 Flash     │
│  - Map criteria                  → Gemini 2.0 Flash     │
│  Cost: ~$0.00004 per case                               │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 2: Document Parsing                               │
│  ────────────────────────────────────────────────────── │
│  - Extract text from PDFs        → Docling (Local!)    │
│  - OCR scanned documents         → Docling (Local!)    │
│  - Parse DOCX, images, etc.      → Docling (Local!)    │
│  Cost: $0 (runs locally)                                │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 3: Information Extraction                         │
│  ────────────────────────────────────────────────────── │
│  - Extract key facts             → Gemini 2.5 Flash    │
│  - Identify entities             → Gemini 2.5 Flash    │
│  - Classify documents            → Gemini 2.5 Flash    │
│  Cost: ~$0.40 per case (143 docs)                       │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 4: Letter Generation                              │
│  ────────────────────────────────────────────────────── │
│  - Generate attorney letter      → Gemini 2.5 Flash    │
│  - Create exhibit index          → Gemini 2.5 Flash    │
│  Cost: ~$0.05 per case                                  │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 5: Polishing (OPTIONAL)                           │
│  ────────────────────────────────────────────────────── │
│  - Polish letter language        → Claude Sonnet 4     │
│  Cost: ~$3-5 per case (if enabled)                      │
│  ⚠️ DISABLED by default!                                │
└─────────────────────────────────────────────────────────┘
```

---

## API Usage Breakdown

### **Where Each LLM is Used**

| Service | LLM Used | Required? | Purpose |
|---------|----------|-----------|---------|
| **folder_validator.py** | Gemini 2.0 Flash | ✅ **YES** | Detect Evidence folder, Case Overview |
| **criteria_mapper.py** | Gemini 2.5 Flash | ✅ **YES** | Map folders to EB-1A criteria |
| **information_extractor.py** | Gemini 2.5 Flash | ✅ **YES** | Extract facts from documents |
| **letter_generator.py** | Gemini 2.5 Flash | ✅ **YES** | Generate attorney letter |
| **letter_generator.py** (polish) | Claude Sonnet 4 | ❌ **NO** | Optional polishing (disabled by default) |
| **document_parser.py** | None (Docling) | N/A | Local parsing, no API |

### **Summary**

- **Gemini**: Used in 4/5 pipeline steps → **REQUIRED**
- **Claude**: Used in 1/5 steps (optional polish) → **OPTIONAL**
- **OpenRouter**: Not used in pipeline → **LEGACY**

---

## How to Configure (Minimum Setup)

### **1. Get Free Gemini API Key**

**Steps**:
1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy your key (looks like: `AIzaSy...`)

**Free Tier**:
- ✅ 2 million tokens per month FREE
- ✅ Gemini 2.0 Flash: Fast and free
- ✅ Gemini 2.5 Flash: Highest quality, still free
- ✅ No credit card required

**Cost Estimate**:
- ~$0.45 per case with free tier
- Can process ~4,400 cases/month FREE (2M tokens / 450 tokens per case)

### **2. Configure `.env` File**

**Minimum Configuration**:
```bash
# LLM Provider - MUST BE GEMINI
llm_provider=gemini

# Gemini API Key (REQUIRED)
gemini_api_key=AIzaSy...YOUR_KEY_HERE...

# Gemini Model (RECOMMENDED)
gemini_model=gemini-2.0-flash-exp

# Claude Polishing (OPTIONAL - disable for baby version)
use_claude_polish=false

# Claude API (NOT NEEDED for baby version)
# claude_api_key=

# OpenRouter (LEGACY - not used)
# openrouter_api_key=
```

### **3. Verify Configuration**

**Test if Gemini is working**:
```bash
cd backend
python -c "
from app.llm.gemini import GeminiLLM
import asyncio

async def test():
    llm = GeminiLLM()
    result = await llm.generate('Say hello!')
    print(result)

asyncio.run(test())
"
```

**Expected output**: `Hello! How can I help you today?`

---

## What Happens Without Claude?

### **With Gemini Only (Baby Version)**

✅ **Works completely**:
- ✅ Folder validation with confidence scoring
- ✅ Criteria mapping
- ✅ Document parsing (local)
- ✅ Information extraction
- ✅ Attorney letter generation
- ✅ Exhibit index generation
- ✅ Full pipeline end-to-end

**Output Quality**:
- **Good**: Professional attorney letter
- **Functional**: All required sections included
- **Usable**: Ready for review and minor edits

### **With Claude Added (Premium Version)**

✅ **Additional polish**:
- ✅ More sophisticated language
- ✅ Better flow and transitions
- ✅ Legal tone refinement
- ✅ Professional formatting improvements

**Output Quality**:
- **Excellent**: Publication-ready letter
- **Polished**: Minimal edits needed
- **Professional**: Attorney-level writing

**Cost Difference**:
- Baby version (Gemini only): ~$0.45/case
- Premium version (Gemini + Claude): ~$3.50-5.50/case

---

## Feature Availability Matrix

| Feature | Gemini Only | Gemini + Claude |
|---------|-------------|-----------------|
| **Folder Validation** | ✅ Full | ✅ Full |
| **Flexible Folder Detection** | ✅ Yes | ✅ Yes |
| **Criteria Mapping** | ✅ Yes | ✅ Yes |
| **Confidence Scoring** | ✅ Yes | ✅ Yes |
| **Document Parsing** | ✅ Yes | ✅ Yes |
| **OCR Support** | ✅ Yes | ✅ Yes |
| **Information Extraction** | ✅ Yes | ✅ Yes |
| **Letter Generation** | ✅ Yes | ✅ Yes |
| **Exhibit Management** | ✅ Yes | ✅ Yes |
| **DOCX Export** | ✅ Yes | ✅ Yes |
| **Letter Polishing** | ❌ No | ✅ Yes |
| **Cost per Case** | ~$0.45 | ~$3.50-5.50 |

---

## How to Enable Claude (Optional)

If you want the premium polishing feature:

### **1. Get Claude API Key**

**Steps**:
1. Go to: https://console.anthropic.com/
2. Sign up and add payment method (paid only)
3. Create API key
4. Copy key (looks like: `sk-ant-...`)

**Pricing**:
- Claude Sonnet 4: $3 per million input tokens
- ~$3-5 per case for polishing

### **2. Update `.env`**

```bash
# Enable Claude polishing
use_claude_polish=true

# Add Claude API key
claude_api_key=sk-ant-...YOUR_KEY_HERE...
claude_model=claude-sonnet-4-20250514
```

### **3. Test**

```bash
cd backend
python -c "
from app.llm.claude import ClaudeLLM
import asyncio

async def test():
    llm = ClaudeLLM()
    result = await llm.generate('Say hello!')
    print(result)

asyncio.run(test())
"
```

---

## OpenRouter Status (Legacy)

**OpenRouter is NOT used in the current pipeline**:
- ❌ Not in folder validation
- ❌ Not in criteria mapping
- ❌ Not in information extraction
- ❌ Not in letter generation

**You can safely ignore OpenRouter** for the baby version.

**Why it exists**:
- Legacy code from earlier prototype
- May be used for experimental features
- Can be re-enabled via `llm_provider=openrouter` (not recommended)

---

## Recommended Setup for Testing

### **Option 1: Free Baby Version (Recommended)**

**APIs Needed**: Just Gemini (FREE)

**Configuration**:
```bash
llm_provider=gemini
gemini_api_key=YOUR_GEMINI_KEY
gemini_model=gemini-2.0-flash-exp
use_claude_polish=false
```

**Pros**:
- ✅ Completely free (2M tokens/month)
- ✅ Full pipeline works
- ✅ Fast processing
- ✅ Good quality output
- ✅ No credit card needed

**Cons**:
- ❌ No letter polishing
- ❌ Basic language (still professional)

**Use Case**: Perfect for testing, development, and basic production

---

### **Option 2: Premium Version**

**APIs Needed**: Gemini (FREE) + Claude (PAID)

**Configuration**:
```bash
llm_provider=gemini
gemini_api_key=YOUR_GEMINI_KEY
gemini_model=gemini-2.5-flash-exp
use_claude_polish=true
claude_api_key=YOUR_CLAUDE_KEY
claude_model=claude-sonnet-4-20250514
```

**Pros**:
- ✅ Best quality output
- ✅ Professional polish
- ✅ Attorney-level writing
- ✅ Minimal editing needed

**Cons**:
- ❌ Costs $3-5 per case (Claude)
- ❌ Requires payment method

**Use Case**: Production use for high-quality deliverables

---

## Cost Comparison

### **Per Case Cost Breakdown**

| Step | Gemini Only | Gemini + Claude |
|------|-------------|-----------------|
| Folder validation | $0.00004 | $0.00004 |
| Document parsing | $0 (local) | $0 (local) |
| Information extraction | $0.40 | $0.40 |
| Letter generation | $0.05 | $0.05 |
| Letter polishing | $0 (skipped) | $3-5 |
| **TOTAL** | **~$0.45** | **~$3.50-5.50** |

### **Monthly Cost (100 cases)**

| Version | Cost per Case | 100 Cases | Notes |
|---------|---------------|-----------|-------|
| **Baby (Gemini only)** | $0.45 | $45 | Can be FREE if within 2M tokens |
| **Premium (+ Claude)** | $4.00 | $400 | Claude costs dominate |

---

## Quick Start Commands

### **1. Install Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

### **2. Create `.env` File**

```bash
cat > .env << EOF
# Minimum configuration for baby version
llm_provider=gemini
gemini_api_key=YOUR_GEMINI_KEY_HERE
gemini_model=gemini-2.0-flash-exp
use_claude_polish=false
database_url=sqlite:///./aurigo.db
secret_key=your-secret-key-change-in-production
frontend_url=http://localhost:3000
EOF
```

### **3. Start Backend**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### **4. Upload Test Case**

```bash
# Via frontend at http://localhost:3000
# Or via API:
curl -X POST http://localhost:8000/api/cases/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "beneficiary_name=Test User" \
  -F "uploaded_folder=@test_case.zip"
```

---

## Troubleshooting

### **Error: "GEMINI_API_KEY not configured"**

**Solution**: Add Gemini API key to `.env`:
```bash
gemini_api_key=AIzaSy...YOUR_KEY...
```

### **Error: "LLM API error: 429 Rate Limit"**

**Solution**: You've hit Gemini's free tier limit (2M tokens/month)
- Wait for next month
- Or upgrade to paid tier
- Or reduce processing (fewer cases)

### **Warning: "Claude API key not found"**

**Solution**: This is OK if `use_claude_polish=false`
- Baby version doesn't need Claude
- Just ignore the warning

### **Error: "ModuleNotFoundError: docling"**

**Solution**: Install Docling:
```bash
pip install docling
```

---

## Summary

### **Minimum Required**

✅ **1 API Key**: Gemini (FREE)

### **What Works**

✅ **Full pipeline**: Validation → Parsing → Extraction → Generation
✅ **New features**: Flexible folder detection, confidence scoring
✅ **Output**: Professional attorney letter + exhibit index

### **Cost**

✅ **FREE** for testing (2M tokens/month)
✅ **~$0.45/case** after free tier

### **Optional Upgrade**

❌ Claude API (~$3-5/case) for premium letter polishing

---

## Next Steps

1. **Get Gemini API key** (FREE): https://aistudio.google.com/app/apikey
2. **Configure `.env`** with Gemini key only
3. **Test with Pranav case** in `Pranav_Case_Data/`
4. **Review output** quality
5. **Decide** if Claude polishing is worth the cost

You're ready to run the baby version with just Gemini! 🎉
