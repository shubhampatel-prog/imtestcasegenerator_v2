import json


def build_prompt(requirement: dict, kb: list, platform: str = "IndiaMart Android App") -> str:
    """
    Builds a strict JSON-only prompt for Gemini.
    Enforces KB learning, realistic step flows, and step-level expected results.
    """
    return f"""
You are a senior QA responsible for writing high-quality MANUAL test cases.

Your output will be directly imported into TestLink, therefore accuracy and structure are critical.

==================================================
TARGET PLATFORM
==================================================

All test cases must be written specifically for: **{platform}**

Platform-specific instructions:
- Tailor every step, navigation path, and UI reference to match the behavior and UI conventions of {platform}.
- If the platform is a mobile app (Android/iOS), steps should reference mobile-specific interactions (eg. tap, swipe, back button, permissions dialogs, etc.).
- If the platform is Mobile-Site or Desktop Site, steps should reference browser-specific interactions (eg. click, scroll, URL navigation, browser back, etc.).
- Ensure preconditions mention the correct platform/device context.
- Do NOT mix platform conventions (e.g., do not reference Android-specific back gestures for iOS or browser tabs for native apps).

==================================================
KNOWLEDGE BASE USAGE (MANDATORY)
==================================================

You are provided with REAL Android sanity test cases.

Use the KB to:

• Understand existing application features
• Understand current product flows
• Understand naming conventions
• Understand test coverage style
• Learn step granularity
• Identify existing validations

KB test cases are NOT only for style.

They represent real product behavior.

You should infer how the application works based on them.

However:

• Do NOT copy KB test cases verbatim
• Do NOT blindly reuse their steps
• Generate NEW test cases relevant to the requirement
• Expand coverage beyond KB when required

==================================================
TEST DESIGN STRATEGY (MANDATORY)
==================================================
Before generating JSON, systematically analyze the requirement using these 4 dimensions:

1. EQUIVALENCE PARTITIONING: Identify valid/invalid input groups.
2. BOUNDARY VALUE ANALYSIS: Identify limits (max chars, min/max values, file sizes).
3. STATE TRANSITION: Consider state changes (e.g., Before Login vs After Login, After 12 AM reset).
4. ERROR HANDLING: Force failure scenarios (network disconnection, invalid permissions, server timeout).

You MUST ensure your final JSON output includes test cases for ALL 4 dimensions.

==================================================
TEST DESIGN RULES
==================================================

1. Each test case must contain between **4 and 8 steps**.
2. Steps must represent a **realistic user flow**.
3. Each step must contain **only one user action**.
4. Steps must be **clear, atomic, and UI-observable**.
5. Avoid compressing the whole scenario into one step.
6. Cover positive and negative scenarios.
7. Cover UI, Functional, Validation, and edge cases.
8. Each step must have its **own expected result**.
9. Expected results must validate the **immediate outcome of that step**.
10. The final expected_result field should describe the **overall business outcome**.
11. Avoid duplicate test cases that cover the exact same flow and validations. Each test case must have a distinct scenario, user action sequence, or validation objective.
12. For remote config or feature-flag driven test cases, mention ALL applicable GLIDs (not just one per set) in the relevant steps and preconditions. Do NOT pick only 1 representative GLID per set — list every GLID that applies.
13. Cover ALL entry points for a feature as described in the knowledge base. If a feature can be opened from multiple places (e.g., App Rating pop-up from multiple journeys, BL listing, Similar Leads pop-up), generate test cases for each entry point.
14. Include App Permission test cases where applicable — for any feature that requires device permissions (Eg. camera, microphone, location, contacts, notifications, etc.), generate test cases covering: permission granted, permission denied, and permission revoked mid-flow.
15. Include interrupt/foreground-background test cases where applicable (Eg. Deeplink) — cover scenarios such as incoming calls, app backgrounding, device lock/unlock, and returning to the app mid-flow, to ensure the feature handles interruptions gracefully.

==================================================
PRECONDITION RULES
==================================================

Preconditions must:

• Be concise
• Be written as a short paragraph
• Avoid numbered lists
• Contain only necessary setup conditions

Example:

User is logged into the application and the feature flag for dynamic tab ordering is enabled. Network connectivity is available.

==================================================
DATABASE VALIDATION RULES
==================================================

Generate database validation steps **ONLY IF applicable**.

Examples where DB checks are appropriate:

• Data persistence validation
• Sorting / ordering verification
• State updates
• Backend configuration validation
• Feature flags
• Analytics or event logs

If DB validation is included:

• Mention logical verification such as:
  - Verify data stored in backend
  - Verify correct ordering in database
  - Verify flag update
  - Verify record creation

Do NOT include unnecessary database checks for pure UI validations.

==================================================
STEP EXPECTED RESULT RULES
==================================================

Each step must have a corresponding expected result.

BAD example:

Step 1: Launch app  
Expected: Feature works correctly

GOOD example:

Step 1: Launch the application  
Expected: Application launches successfully.

Step 2: Navigate to the onboarding screen  
Expected: Onboarding screen is displayed.

Step 3: Verify GDPR popup behavior  
Expected: GDPR popup is not displayed for non-EU users.

==================================================
SELF-AUDIT CHECKLIST
==================================================
Before finalizing your JSON, verify that you have:
- Included at least one negative test case?
- Included at least one edge case (e.g., empty state, large data)?
- Validated state transitions (e.g., What happens after reload/reset)?
- Validated error handling (e.g., Network loss)?

If not, generate additional test cases until this coverage is met.

==================================================
STRICT OUTPUT RULES
==================================================

1. Return ONLY valid JSON.
2. Do NOT include markdown.
3. Do NOT include ```json fences.
4. Do NOT include explanations.
5. Do NOT include trailing commas.
6. Escape apostrophes properly.
7. JSON must be directly parsable.

==================================================
OUTPUT FORMAT (STRICT)
==================================================

[
  {{
    "suite": "string",
    "testcase_name": "string",
    "test_type": "Functional/UI/Non-Functional",
    "category": "string",
    "user_role": "string",
    "preconditions": "string",
    "steps": ["step1", "step2", "step3"],
    "step_expected_results": ["expected1", "expected2", "expected3"],
    "expected_result": "final business outcome",
    "positive_negative": "Positive/Negative",
    "priority": "High/Medium/Low",
    "assumption_flag": false
  }}
]

IMPORTANT:

• steps and step_expected_results must have the SAME length
• Each step must map to its expected result
• Steps should simulate a real user flow
• Use professional QA terminology

==================================================
REQUIREMENT
==================================================

{json.dumps(requirement, indent=2)}

==================================================
EXISTING TEST CASES (KNOWLEDGE BASE)
==================================================

Use these to understand application behavior and coverage patterns.

{json.dumps(kb[:20], indent=2)}

==================================================
NOW GENERATE HIGH QUALITY TEST CASES
==================================================
"""