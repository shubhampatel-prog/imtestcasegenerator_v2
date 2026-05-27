import json
import sys
import streamlit as st
import re

from openproject_client import fetch_ticket
from testlink_client import (
    get_project_id,
    get_all_testcases,
    create_testcase,
    create_child_suite,
)
from kb_loader import normalize_testcases
from testcase_generator import generate_testcases
from config import TESTLINK_PROJECT_NAME, TESTLINK_SUITE_ID

DEFAULT_SUITE_ID = TESTLINK_SUITE_ID

def main(ticket_id: str, project_id: int = None, suite_id: int = None, kb_suite_id: int = None, show_prompt: bool = False, platform: str = "IndiaMart Android App"):
    """
    Original pipeline logic — unchanged.
    Only additions:
      - suite_id    : overrides DEFAULT_SUITE_ID from config
      - kb_suite_id : passed through to get_all_testcases()
      - show_prompt : prints the LLM prompt to the terminal
    """

    effective_suite_id = suite_id if suite_id else DEFAULT_SUITE_ID

    st.info(f"🚀 AI Test Case Pipeline Started for ID: {ticket_id}")

    requirement = fetch_ticket(ticket_id)
    ticket_title = requirement.get("subject", "OpenProject Ticket")
    st.write(f"📌 **Ticket:** {ticket_title}")

    description = requirement.get("description", "") or ""
    word_count = len(description.split())
    if word_count < 50:
        st.error(
            "⚠️ Please enrich the story/task ticket to create test cases. "
            f"The description is too short ({word_count} word{'s' if word_count != 1 else ''}). "
            "A minimum of 50 words is required for meaningful test case generation."
        )
        return False, 0, 0, None

    project_id = project_id if project_id else get_project_id(TESTLINK_PROJECT_NAME)

    clean_title = re.sub(r"[^a-zA-Z0-9 _-]", "", ticket_title)
    clean_title = clean_title[:120]

    child_suite_name = f"{ticket_id} - {clean_title}"
    st.write(f"📁 Creating/Retrieving Suite...")

    suite_id_new = create_child_suite(
        effective_suite_id,
        project_id,
        child_suite_name,
    )

    if not suite_id_new:
        st.error("❌ Failed to create child suite.")
        return False, 0, 0, None

    raw_kb = get_all_testcases(project_id, kb_suite_id=kb_suite_id)
    kb = normalize_testcases(raw_kb)

    st.write("🧠 Generating AI testcases...")
    testcases_json, prompt_used = generate_testcases(requirement, kb, return_prompt=True, platform=platform)

    # Print prompt to terminal if requested
    if show_prompt:
        print("\n" + "=" * 70)
        print("  PROMPT SENT TO LLM")
        print("=" * 70)
        print(prompt_used)
        print("=" * 70 + "\n")


    try:
        testcases = json.loads(testcases_json)
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON parse failed: {e}")
        return False, 0, 0, None

    if not testcases:
        st.warning("⚠️ No test cases generated.")
        return False, 0, 0, None

    st.write(f"🚀 Creating **{len(testcases)}** test cases in TestLink...")

    created = 0
    failed = 0

    for tc in testcases:
        name = tc.get("testcase_name", "UNKNOWN_TC")
        success = create_testcase(project_id, suite_id_new, tc)

        if success:
            created += 1
        else:
            failed += 1
            st.error(f"Failed to create: {name}")

    return True, created, failed, prompt_used


if __name__ == "__main__":
    ticket_id = input("👉 Enter OpenProject Ticket ID: ").strip()
    if ticket_id:
        main(ticket_id)
