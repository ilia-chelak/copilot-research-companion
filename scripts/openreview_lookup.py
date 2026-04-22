#!/usr/bin/env python3
"""
OpenReview paper review lookup via direct API calls.

Usage:
    python scripts/openreview_lookup.py "Paper Title Here"
    python scripts/openreview_lookup.py "Paper Title Here" --venue ICLR --year 2026
    python scripts/openreview_lookup.py --forum-id aMs6FtNaY5

Exit codes:
    0  Success — reviews found and printed
    2  Paper not found on OpenReview
    3  Paper found but no public review artifacts
    5  API/network error

Requires: pip install requests
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(5)

API_BASE = "https://api2.openreview.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "application/json",
}

# Venues that use OpenReview, with submission invitation variants to try.
VENUE_CONFIGS = {
    "ICLR": {
        "id_template": "ICLR.cc/{year}/Conference",
        "years": range(2023, 2028),
        "submission_suffixes": ["/-/Submission", "/-/Blind_Submission"],
    },
    "NeurIPS": {
        "id_template": "NeurIPS.cc/{year}/Conference",
        "years": range(2023, 2028),
        "submission_suffixes": ["/-/Submission", "/-/Blind_Submission"],
    },
    "ICML": {
        "id_template": "ICML.cc/{year}/Conference",
        "years": range(2023, 2028),
        "submission_suffixes": ["/-/Submission", "/-/Blind_Submission"],
    },
    "AAAI": {
        "id_template": "AAAI.org/{year}/Conference",
        "years": range(2024, 2028),
        "submission_suffixes": ["/-/Submission", "/-/Blind_Submission"],
    },
    "COLM": {
        "id_template": "COLM.cc/{year}/Conference",
        "years": range(2024, 2028),
        "submission_suffixes": ["/-/Submission"],
    },
    "ARR": {
        "id_template": "aclweb.org/ACL/ARR/{year}/October",
        "years": range(2023, 2028),
        "submission_suffixes": ["/-/Submission"],
    },
}


def api_get(endpoint, params=None):
    """Make a GET request to the OpenReview API with proper headers."""
    url = f"{API_BASE}{endpoint}"
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 403:
        return None, "forbidden"
    if r.status_code == 404:
        return None, "not_found"
    if r.status_code != 200:
        return None, f"http_{r.status_code}"
    return r.json(), None


def search_by_title(title, venue_hint=None, year_hint=None):
    """Search for a paper by title across OpenReview.

    When a venue hint is given, uses the precise invitation-based search.
    Otherwise, uses the /notes/search full-text endpoint which covers ALL venues
    (conferences, workshops, journals like TMLR, etc.) in a single query.
    """
    # If venue hint provided, use targeted invitation-based search
    if venue_hint and venue_hint.upper() in VENUE_CONFIGS:
        return _search_by_invitation(title, venue_hint, year_hint)

    # Otherwise, use the full-text search endpoint (covers all venues)
    return _search_fulltext(title)


def _title_similarity(a, b):
    """Simple word-overlap similarity between two titles."""
    wa = set(a.strip().lower().split())
    wb = set(b.strip().lower().split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / max(len(wa), len(wb))


def _search_fulltext(title):
    """Search across ALL OpenReview venues using the /notes/search endpoint."""
    data, err = api_get("/notes/search", {"query": title, "limit": "10"})
    if err:
        return [], err == "forbidden"

    found = []
    for note in data.get("notes", []):
        note_title = _extract_title(note)
        if note_title and _title_similarity(title, note_title) > 0.4:
            found.append(note)

    # Deduplicate by forum ID
    seen = set()
    unique = []
    for n in found:
        fid = n.get("forum", n.get("id"))
        if fid not in seen:
            seen.add(fid)
            unique.append(n)

    return unique, False


def _extract_title(note):
    """Extract title string from a raw API note dict."""
    content = note.get("content", {})
    if not content:
        return ""
    title_field = content.get("title", {})
    if isinstance(title_field, dict):
        return title_field.get("value", "")
    return str(title_field)


def _search_by_invitation(title, venue_hint, year_hint):
    """Search using venue-specific invitation patterns (more precise, fewer results)."""
    invitations_to_try = []

    cfg = VENUE_CONFIGS[venue_hint.upper()]
    years = [year_hint] if year_hint else cfg["years"]
    for y in years:
        vid = cfg["id_template"].format(year=y)
        for suffix in cfg["submission_suffixes"]:
            invitations_to_try.append(vid + suffix)

    found = []
    api_errors = 0

    for invitation in invitations_to_try:
        data, err = api_get("/notes", {
            "invitation": invitation,
            "content.title": title,
            "limit": "5",
        })
        if err:
            if err == "forbidden":
                api_errors += 1
            continue
        for note in data.get("notes", []):
            found.append(note)

    # Deduplicate by forum ID
    seen = set()
    unique = []
    for n in found:
        fid = n.get("forum", n.get("id"))
        if fid not in seen:
            seen.add(fid)
            unique.append(n)

    all_failed = api_errors > 0 and len(unique) == 0
    return unique, all_failed


def search_by_forum(forum_id):
    """Get a paper by its forum ID."""
    data, err = api_get(f"/notes", {"id": forum_id})
    if err:
        return [], err == "forbidden"
    notes = data.get("notes", [])
    return notes, False


def get_all_forum_notes(forum_id):
    """Fetch all notes (reviews, meta-reviews, decisions) for a paper forum."""
    all_notes = []
    offset = 0
    limit = 1000
    while True:
        data, err = api_get("/notes", {
            "forum": forum_id,
            "limit": str(limit),
            "offset": str(offset),
        })
        if err or not data:
            break
        notes = data.get("notes", [])
        all_notes.extend(notes)
        if len(notes) < limit:
            break
        offset += limit
    return all_notes


def classify_notes(forum_id, all_notes):
    """Classify forum notes into reviews, meta-review, and decision."""
    reviews = []
    meta_review = None
    decision = None

    for note in all_notes:
        if note.get("id") == forum_id:
            continue

        invitations = note.get("invitations", [])
        inv_lower = " ".join(invitations).lower()

        if any(kw in inv_lower for kw in ["decision", "acceptance"]):
            decision = note
        elif any(kw in inv_lower for kw in ["meta_review", "metareview", "meta-review"]):
            meta_review = note
        elif any(kw in inv_lower for kw in ["official_review"]) or (
            "review" in inv_lower
            and "meta" not in inv_lower
            and "ethics" not in inv_lower
            and "decision" not in inv_lower
            and "withdrawal" not in inv_lower
            and "desk_reject" not in inv_lower
        ):
            if note.get("content"):
                reviews.append(note)

    return reviews, meta_review, decision


def extract_content(note):
    """Extract all content fields from a note dict."""
    content = note.get("content", {})
    if not content:
        return {}
    result = {}
    for key, val in content.items():
        if isinstance(val, dict) and "value" in val:
            result[key] = val["value"]
        else:
            result[key] = val
    return result


def _get_title(note):
    """Safely extract title string from a note dict."""
    return extract_content(note).get("title", "Unknown Title")


def _get_rating(rc):
    for key in ["rating", "recommendation", "overall_assessment", "score", "soundness"]:
        if key in rc and rc[key]:
            return str(rc[key])
    return "N/A"


def _get_confidence(rc):
    for key in ["confidence", "confidence_assessment", "reviewer_confidence"]:
        if key in rc and rc[key]:
            return str(rc[key])
    return "N/A"


def format_output(paper_note, reviews, meta_review, decision):
    """Format the results as structured markdown."""
    title = _get_title(paper_note)
    forum_id = paper_note.get("forum", paper_note.get("id", ""))
    forum_url = f"https://openreview.net/forum?id={forum_id}"

    lines = [
        f"# OpenReview Reviews: {title}",
        f"- **OpenReview URL**: {forum_url}",
        f"- **Forum ID**: {forum_id}",
    ]

    if decision:
        dc = extract_content(decision)
        dec_val = dc.get("decision", dc.get("recommendation", dc.get("value", "Unknown")))
        lines.append(f"- **Decision**: {dec_val}")

    if reviews:
        ratings = [_get_rating(extract_content(r)) for r in reviews]
        lines.append(f"- **Ratings**: {', '.join(ratings)} ({len(reviews)} reviewers)")

    lines.extend(["", "---"])

    field_aliases = {
        "Summary": ["summary", "summary_of_contributions", "main_review", "review"],
        "Strengths": ["strengths", "strengths_and_weaknesses"],
        "Weaknesses": ["weaknesses"],
        "Questions": ["questions"],
        "Limitations": ["limitations"],
        "Requested Changes": ["requested_changes"],
        "Soundness": ["soundness"],
        "Presentation": ["presentation"],
        "Contribution": ["contribution"],
        "Broader Impact": ["broader_impact_concerns"],
        "Ethics": ["flag_for_ethics_review", "ethics_review"],
        "Claims and Evidence": ["claims_and_evidence"],
        "Audience": ["audience"],
    }

    for i, rev in enumerate(reviews, 1):
        rc = extract_content(rev)
        lines.extend(["", f"## Reviewer {i}"])
        lines.append(f"- **Rating**: {_get_rating(rc)}")
        lines.append(f"- **Confidence**: {_get_confidence(rc)}")

        printed_keys = {"rating", "confidence", "title", "recommendation",
                        "overall_assessment", "score", "reviewer_confidence",
                        "confidence_assessment"}

        for display_name, aliases in field_aliases.items():
            for alias in aliases:
                if alias in rc and rc[alias] and str(rc[alias]).strip():
                    lines.extend([f"\n### {display_name}", str(rc[alias])])
                    printed_keys.add(alias)
                    break

        for key, val in rc.items():
            if key not in printed_keys and val and str(val).strip():
                display = key.replace("_", " ").title()
                lines.extend([f"\n### {display}", str(val)])

        lines.extend(["", "---"])

    if meta_review:
        lines.extend(["", "## Meta-Review"])
        mc = extract_content(meta_review)
        for key, val in mc.items():
            if val and str(val).strip():
                display = key.replace("_", " ").title()
                lines.extend([f"\n### {display}", str(val)])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Look up OpenReview reviews for a paper",
    )
    parser.add_argument("title", nargs="?", help="Paper title to search for")
    parser.add_argument("--venue", help="Venue hint (ICLR, NeurIPS, ICML, AAAI, COLM)")
    parser.add_argument("--year", type=int, help="Year hint (e.g., 2025)")
    parser.add_argument("--forum-id", help="Direct OpenReview forum ID")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    args = parser.parse_args()

    if not args.title and not args.forum_id:
        parser.error("Provide either a paper title or --forum-id")

    # Find the paper
    if args.forum_id:
        papers, api_failed = search_by_forum(args.forum_id)
    else:
        papers, api_failed = search_by_title(args.title, args.venue, args.year)

    if not papers:
        if api_failed:
            print("API_ERROR: OpenReview API returned 403. Check network access.", file=sys.stderr)
            sys.exit(5)
        print(f"NOT_FOUND: No paper matching '{args.title or args.forum_id}' on OpenReview", file=sys.stderr)
        sys.exit(2)

    if len(papers) > 1:
        print(f"Found {len(papers)} candidates, using first match.", file=sys.stderr)

    paper = papers[0]
    title = _get_title(paper)
    forum_id = paper.get("forum", paper.get("id", ""))
    print(f"Found: {title} (forum={forum_id})", file=sys.stderr)

    # Fetch all notes for this paper
    all_notes = get_all_forum_notes(forum_id)
    reviews, meta_review, decision = classify_notes(forum_id, all_notes)

    if not reviews and not meta_review and not decision:
        print("NO_REVIEWS: Paper found but no public review artifacts", file=sys.stderr)
        sys.exit(3)

    review_count = len(reviews)
    extra = []
    if meta_review:
        extra.append("meta-review")
    if decision:
        extra.append("decision")
    extra_str = f" + {', '.join(extra)}" if extra else ""
    print(f"Found {review_count} reviews{extra_str}", file=sys.stderr)

    output = format_output(paper, reviews, meta_review, decision)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
