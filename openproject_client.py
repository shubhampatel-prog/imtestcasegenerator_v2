import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config import OPENPROJECT_BASE_URL, OPENPROJECT_API_KEY

# ─────────────────────────────────────────────
# Shared request helper — never raises, returns None on any failure
# ─────────────────────────────────────────────
def _get(url: str):
    try:
        response = requests.get(
            url,
            auth=("apikey", OPENPROJECT_API_KEY),
            headers={"Content-Type": "application/json"},
            verify=False,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️  OpenProject fetch failed [{url}]: {e}")
        return None


# ─────────────────────────────────────────────
# Attachments  (/api/v3/work_packages/{id}/attachments)
# Returns a list of dicts with file metadata only (no binary download)
# ─────────────────────────────────────────────
def _fetch_attachments(ticket_id: str) -> list:
    try:
        url  = f"{OPENPROJECT_BASE_URL}/api/v3/work_packages/{ticket_id}/attachments"
        data = _get(url)
        if not data:
            return []

        elements = data.get("_embedded", {}).get("elements", [])
        attachments = []

        for el in elements:
            if not isinstance(el, dict):
                continue
            attachments.append({
                "file_name":    el.get("fileName", ""),
                "content_type": el.get("contentType", ""),
                "file_size":    el.get("fileSize", ""),
                "description":  (el.get("description") or {}).get("raw", ""),
                "created_at":   el.get("createdAt", ""),
                "created_by":   el.get("_links", {}).get("author", {}).get("title", ""),
            })

        return attachments
    except Exception as e:
        print(f"⚠️  Attachments fetch failed: {e}")
        return []


# ─────────────────────────────────────────────
# Activities  (/api/v3/work_packages/{id}/activities)
# Returns comments + change-log entries
# ─────────────────────────────────────────────
def _fetch_activities(ticket_id: str) -> list:
    try:
        url  = f"{OPENPROJECT_BASE_URL}/api/v3/work_packages/{ticket_id}/activities"
        data = _get(url)
        if not data:
            return []

        elements = data.get("_embedded", {}).get("elements", [])
        activities = []

        for el in elements:
            if not isinstance(el, dict):
                continue

            comment_raw = (el.get("comment") or {}).get("raw", "")

            # details is a list of change entries [{raw: "...", format: "..."}]
            raw_details = el.get("details", [])
            detail_texts = []
            for d in raw_details:
                if isinstance(d, dict):
                    text = d.get("raw", "")
                    if text:
                        detail_texts.append(text)

            # Skip empty activities (no comment, no details)
            if not comment_raw and not detail_texts:
                continue

            activities.append({
                "type":       el.get("_type", ""),
                "created_at": el.get("createdAt", ""),
                "user":       el.get("_links", {}).get("user", {}).get("title", ""),
                "comment":    comment_raw,
                "changes":    detail_texts,
            })

        return activities
    except Exception as e:
        print(f"⚠️  Activities fetch failed: {e}")
        return []


# ─────────────────────────────────────────────
# Main entry point — fetch everything about a ticket
# ─────────────────────────────────────────────
def fetch_ticket(ticket_id: str) -> dict:
    url  = f"{OPENPROJECT_BASE_URL}/api/v3/work_packages/{ticket_id}"
    data = _get(url)

    if data is None:
        # Hard failure on the main ticket — re-raise so the caller sees it
        raise Exception(f"Failed to fetch work package {ticket_id} from OpenProject")

    links = data.get("_links", {})

    # ── Core fields ──────────────────────────────────────────────────────────
    subject     = data.get("subject", "")
    description = (data.get("description") or {}).get("raw", "")
    ticket_type = links.get("type",     {}).get("title", "")
    status      = links.get("status",   {}).get("title", "")
    priority    = links.get("priority", {}).get("title", "")
    project     = links.get("project",  {}).get("title", "")
    author      = links.get("author",   {}).get("title", "")
    assignee    = links.get("assignee", {}).get("title", "")
    version     = links.get("version",  {}).get("title", "")
    category    = links.get("category", {}).get("title", "")
    parent      = links.get("parent",   {}).get("title", "")

    start_date       = data.get("startDate", "")
    due_date         = data.get("dueDate", "")
    estimated_hours  = data.get("estimatedTime", "")
    remaining_hours  = data.get("remainingTime", "")
    percent_done     = data.get("percentageDone", "")
    story_points     = data.get("storyPoints", "")
    created_at       = data.get("createdAt", "")
    updated_at       = data.get("updatedAt", "")

    # ── Custom fields (any key starting with "customField") ──────────────────
    custom_fields = {}
    try:
        for key, value in data.items():
            if key.startswith("customField"):
                if isinstance(value, dict):
                    custom_fields[key] = value.get("raw", "") or value.get("title", "") or str(value)
                elif value is not None:
                    custom_fields[key] = str(value)
    except Exception as e:
        print(f"⚠️  Custom fields parse failed: {e}")

    # ── Attachments (separate API call, safe fallback to []) ─────────────────
    attachments = _fetch_attachments(ticket_id)

    # ── Activities  (separate API call, safe fallback to []) ─────────────────
    activities = _fetch_activities(ticket_id)

    # ── Assemble final requirement dict ──────────────────────────────────────
    requirement = {
        "id":              ticket_id,
        "subject":         subject,
        "type":            ticket_type,
        "status":          status,
        "priority":        priority,
        "project":         project,
        "author":          author,
        "assignee":        assignee,
        "version":         version,
        "category":        category,
        "parent_ticket":   parent,
        "start_date":      start_date,
        "due_date":        due_date,
        "estimated_hours": estimated_hours,
        "remaining_hours": remaining_hours,
        "percent_done":    percent_done,
        "story_points":    story_points,
        "created_at":      created_at,
        "updated_at":      updated_at,
        "description":     description,
        "custom_fields":   custom_fields,
        "attachments":     attachments,
        "activities":      activities,
    }

    # Drop keys with empty / None values to keep the prompt lean
    requirement = {k: v for k, v in requirement.items()
                   if v not in (None, "", [], {})}

    # Always keep these even if empty so downstream code can rely on them
    requirement.setdefault("id",          ticket_id)
    requirement.setdefault("subject",     "")
    requirement.setdefault("description", "")

    return requirement
