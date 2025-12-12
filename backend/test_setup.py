"""
Quick diagnostic script to test Aurigo setup (Windows compatible)
"""
import asyncio
import sys

async def test_all():
    print("=" * 60)
    print("AURIGO SETUP DIAGNOSTIC")
    print("=" * 60)

    # Test 1: Config
    print("\n[1/5] Testing Configuration...")
    try:
        from app.config import get_settings
        settings = get_settings()
        print(f"  [OK] LLM Provider: {settings.llm_provider}")
        gemini_key_status = 'SET (' + settings.gemini_api_key[:20] + '...)' if settings.gemini_api_key else '[MISSING]'
        print(f"  [OK] Gemini Key: {gemini_key_status}")
        print(f"  [OK] Database: {settings.database_url}")
    except Exception as e:
        print(f"  [ERROR] Config Error: {e}")
        return

    # Test 2: Imports
    print("\n[2/5] Testing Imports...")
    try:
        from app.services.folder_validator import FolderValidator
        print("  [OK] FolderValidator")
        from app.services.criteria_mapper import CriteriaMapper
        print("  [OK] CriteriaMapper")
        from app.llm.gemini import GeminiLLM
        print("  [OK] GeminiLLM")
    except Exception as e:
        print(f"  [ERROR] Import Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 3: Gemini API
    print("\n[3/5] Testing Gemini API...")
    try:
        from app.llm.gemini import GeminiLLM
        llm = GeminiLLM()
        result = await llm.generate("Say 'OK'", temperature=0.1)
        if result:
            print(f"  [OK] Gemini API working: {result[:50]}")
        else:
            print("  [ERROR] Gemini API returned empty response")
    except Exception as e:
        print(f"  [ERROR] Gemini API Error: {e}")
        if "GEMINI_API_KEY not configured" in str(e):
            print("  [FIX] Add GEMINI_API_KEY to .env file")
        import traceback
        traceback.print_exc()
        return

    # Test 4: Folder Detection
    print("\n[4/5] Testing Folder Detection...")
    try:
        result = await llm.identify_evidence_folder([
            "Evidence", "Personal", "Random"
        ])
        print(f"  [OK] Evidence detection: {result['evidence_folder']} (confidence: {result['confidence']})")
    except Exception as e:
        print(f"  [ERROR] Folder Detection Error: {e}")
        import traceback
        traceback.print_exc()

    # Test 5: Validation
    print("\n[5/5] Testing Validation...")
    try:
        from pathlib import Path
        test_path = Path("C:/aurigo/Pranav_Case_Data")
        if test_path.exists():
            validator = FolderValidator()
            validation = await validator.validate_structure(str(test_path))
            print(f"  [OK] Validation: {validation['valid']}")
            if validation.get('errors'):
                print(f"  [WARNING] Errors: {validation['errors']}")
            if validation.get('warnings'):
                print(f"  [WARNING] Warnings: {validation['warnings']}")
        else:
            print(f"  [WARNING] Test case not found at {test_path}")
    except Exception as e:
        print(f"  [ERROR] Validation Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_all())