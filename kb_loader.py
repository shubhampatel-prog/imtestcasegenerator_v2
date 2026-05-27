def normalize_testcases(raw_cases):
    """
    Converts TestLink sanity cases into compact AI-friendly KB.
    Includes name, summary, preconditions, and steps+expected results.
    Limits size to avoid token overflow.
    """

    kb = []

    # 🔥 IMPORTANT: limit to prevent token explosion
    for tc in raw_cases[:25]:
        kb.append({
            "name":                  tc.get("name", ""),
            "summary":               tc.get("summary", ""),
            "preconditions":         tc.get("preconditions", ""),
            "steps":                 tc.get("steps", []),
            "step_expected_results": tc.get("step_expected_results", []),
        })

    return kb
