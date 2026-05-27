import requests
import xml.etree.ElementTree as ET
import time
import xmlrpc.client
import html
import ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config import (
    TESTLINK_URL,
    TESTLINK_API_KEY,
    TESTLINK_AUTHOR_LOGIN,
)


# =========================================================
# SSL-bypassing transport for xmlrpc.client (corporate certs)
# =========================================================
class _SafeTransport(xmlrpc.client.SafeTransport):
    def make_connection(self, host):
        self._connection = host, None
        import http.client
        conn = http.client.HTTPSConnection(
            host,
            context=ssl.create_default_context(),
        )
        conn._context = ssl._create_unverified_context()
        return conn

def _rpc_client():
    return xmlrpc.client.ServerProxy(TESTLINK_URL, transport=_SafeTransport())


# =========================================================
# XML ESCAPE
# =========================================================
def escape_xml(text):
    if text is None:
        return ""
    return html.escape(str(text), quote=True)


# =========================================================
# 📚 KB LOADER
# Only change from original: accepts kb_suite_id param,
# and fetches preconditions + steps via xmlrpc for richer KB.
# =========================================================
def get_all_testcases(project_id, kb_suite_id=None):

    KB_SUITE_ID = kb_suite_id if kb_suite_id else 26691
    print(f"📚 Loading KB from suite {KB_SUITE_ID}...")

    try:
        rpc = _rpc_client()

        response = rpc.tl.getTestCasesForTestSuite({
            "devKey": TESTLINK_API_KEY,
            "testsuiteid": int(KB_SUITE_ID),
            "deep": True,
            "details": "full",
        })

        print(f"📦 Raw KB response type: {type(response)}, length: {len(response) if isinstance(response, (list, dict)) else 'N/A'}")

        if isinstance(response, dict):
            items = list(response.values())
        elif isinstance(response, list):
            items = response
        else:
            print(f"⚠️ Unexpected KB response type: {type(response)}")
            return []

        kb_cases = []

        for tc in items:
            if not isinstance(tc, dict):
                continue

            name    = tc.get("name", tc.get("testcase_name", ""))
            summary = tc.get("summary", "")
            precond = tc.get("preconditions", "")

            if not name:
                continue

            raw_steps = tc.get("steps", [])
            parsed_steps = []
            parsed_expected = []

            if isinstance(raw_steps, (list, tuple)):
                for s in raw_steps:
                    if isinstance(s, dict):
                        parsed_steps.append(s.get("actions", ""))
                        parsed_expected.append(s.get("expected_results", ""))

            kb_cases.append({
                "name":                  name,
                "summary":               summary,
                "preconditions":         precond,
                "steps":                 parsed_steps,
                "step_expected_results": parsed_expected,
            })

        print(f"✅ KB Loaded: {len(kb_cases)} testcases")
        return kb_cases[:200]

    except Exception as e:
        print(f"⚠️ KB load failed: {e}")
        return []


# =========================================================
# XML POST
# =========================================================
def _post_xml(body: str, retries: int = 3):

    for attempt in range(retries):
        try:
            response = requests.post(
                TESTLINK_URL,
                data=body.encode("utf-8"),
                headers={"Content-Type": "text/xml"},
                auth=("apikey", TESTLINK_API_KEY),
                timeout=60,
                verify=False,
            )

            response.raise_for_status()
            return response.text

        except Exception as e:
            if attempt == retries - 1:
                raise

            print(f"⚠️ Retry {attempt+1}/{retries} after error: {e}")
            time.sleep(2)


# =========================================================
# PROJECT ID
# =========================================================
def get_project_id(project_name: str):

    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<methodCall>
<methodName>tl.getProjects</methodName>
<params>
<param>
<value>
<struct>
<member>
<name>devKey</name>
<value><string>{TESTLINK_API_KEY}</string></value>
</member>
</struct>
</value>
</param>
</params>
</methodCall>
"""

    xml_response = _post_xml(body)
    root = ET.fromstring(xml_response)

    print("\n===== ACTUAL TESTLINK PROJECTS =====")

    for proj in root.findall(".//struct"):

        pid = None
        pname = None

        for member in proj.findall("member"):

            key_el = member.find("name")
            val_el = member.find("value/string")

            if key_el is None or val_el is None:
                continue

            key = key_el.text
            val = val_el.text

            if key == "id":
                pid = val

            elif key in ("testprojectname", "name"):
                pname = val

        print(f"ID: {pid} | NAME: {pname}")

        if pname == project_name:
            print("===================================\n")
            return int(pid)

    print("===================================\n")
    raise Exception(f"Project not found in TestLink: {project_name}")


# =========================================================
# CREATE CHILD SUITE
# =========================================================
def create_child_suite(parent_suite_id: int, project_id: int, suite_name: str):

    print(f"📁 Creating child suite: {suite_name}")

    client = _rpc_client()

    data = {
        "devKey": TESTLINK_API_KEY,
        "testprojectid": int(project_id),
        "testsuitename": suite_name,
        "details": "Auto-created by AI pipeline",
        "parentid": int(parent_suite_id),
        "checkduplicatedname": True,
        "actiononduplicatedname": "generate_new",
    }

    response = client.tl.createTestSuite(data)

    if isinstance(response, list) and response:
        first = response[0]

        if isinstance(first, dict) and first.get("id"):
            suite_id = int(first["id"])
            print(f"✅ Child suite created: {suite_id}")
            return suite_id

    print("🔴 Raw suite response:", response)
    raise Exception("❌ Failed to create child suite")


# =========================================================
# IMPORTANCE MAP
# =========================================================
def _map_importance(priority: str):

    p = (priority or "").lower()

    if p == "high":
        return 3

    if p == "medium":
        return 2

    if p == "low":
        return 1

    return 2


# =========================================================
# CREATE TEST CASE
# =========================================================
def create_testcase(project_id, suite_id, testcase):

    importance = _map_importance(testcase.get("priority"))

    testcase_name = escape_xml(f"[AI] {testcase['testcase_name']}")

    summary = escape_xml(testcase.get("expected_result", ""))

    preconditions = escape_xml(testcase.get("preconditions", ""))

    steps_xml = ""

    steps = testcase.get("steps", [])
    step_expected = testcase.get("step_expected_results", [])

    for i, step in enumerate(steps, start=1):

        if i-1 < len(step_expected):
            expected = step_expected[i-1]
        else:
            expected = testcase.get("expected_result", "")

        step = escape_xml(step)
        expected = escape_xml(expected)

        steps_xml += f"""
        <value>
          <struct>
            <member>
              <name>step_number</name>
              <value><int>{i}</int></value>
            </member>
            <member>
              <name>actions</name>
              <value><string>{step}</string></value>
            </member>
            <member>
              <name>expected_results</name>
              <value><string>{expected}</string></value>
            </member>
          </struct>
        </value>
        """

    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<methodCall>
  <methodName>tl.createTestCase</methodName>
  <params>
    <param>
      <value>
        <struct>

          <member>
            <name>devKey</name>
            <value><string>{TESTLINK_API_KEY}</string></value>
          </member>

          <member>
            <name>testcasename</name>
            <value><string>{testcase_name}</string></value>
          </member>

          <member>
            <name>testsuiteid</name>
            <value><int>{suite_id}</int></value>
          </member>

          <member>
            <name>testprojectid</name>
            <value><int>{project_id}</int></value>
          </member>

          <member>
            <name>authorlogin</name>
            <value><string>{TESTLINK_AUTHOR_LOGIN}</string></value>
          </member>

          <member>
            <name>summary</name>
            <value><string>{summary}</string></value>
          </member>

          <member>
            <name>preconditions</name>
            <value><string>{preconditions}</string></value>
          </member>

          <member>
            <name>steps</name>
            <value>
              <array>
                <data>
                  {steps_xml}
                </data>
              </array>
            </value>
          </member>

          <member>
            <name>importance</name>
            <value><int>{importance}</int></value>
          </member>

          <member>
            <name>executiontype</name>
            <value><int>1</int></value>
          </member>

        </struct>
      </value>
    </param>
  </params>
</methodCall>
"""

    xml_response = _post_xml(body)

    print("   🔍 Raw TestLink response:", xml_response[:250])

    return "<name>id</name>" in xml_response