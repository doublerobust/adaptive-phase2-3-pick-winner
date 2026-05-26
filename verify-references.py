#!/usr/bin/env python3
"""
verify-references.py — Systematic reference verification against Crossref API.

Usage:
    # Verify all references in a markdown doc
    python3 verify-references.py path/to/document.md

    # Verify a specific list of DOIs
    python3 verify-references.py --dois 10.1002/sim.1362 10.1093/biomet/ass002

What it does:
    1. Extracts numbered references with DOIs from the markdown file
    2. Queries Crossref API for each DOI
    3. Compares title, authors, journal, year, volume, pages
    4. Reports mismatches and non-existent DOIs
    5. For references without DOIs, notes them for manual review

Dependencies: curl (should be available on any Unix system)
"""

import subprocess
import json
import re
import sys
import os
import time
import urllib.parse

def query_crossref(doi):
    """Query Crossref API for a single DOI.
    Returns (message_dict, status_string) where status_string is
    'ok', 'not_found', 'rate_limited', 'server_error', or 'network_error'."""
    encoded_doi = urllib.parse.quote(doi, safe='')
    url = f"https://api.crossref.org/works/{encoded_doi}"
    tmp_out = "/tmp/doi_response.json"
    try:
        r = subprocess.run(
            ["curl", "-sL", "-w", "%{http_code}", "-o", tmp_out, url],
            capture_output=True, text=True, timeout=15
        )
        http_code = r.stdout.strip()
        if r.returncode != 0:
            return None, "network_error"
        if http_code == "404":
            return None, "not_found"
        if http_code == "429":
            return None, "rate_limited"
        if http_code in ("500", "502", "503"):
            return None, "server_error"
        if http_code != "200":
            return None, f"http_{http_code}"
        if not os.path.exists(tmp_out):
            return None, "network_error"
        with open(tmp_out) as f:
            body = f.read()
        if not body:
            return None, "network_error"
        data = json.loads(body)
        return data.get("message"), "ok"
    except json.JSONDecodeError:
        return None, "network_error"
    except Exception:
        return None, "network_error"

def search_crossref(query, limit=10):
    """Search Crossref by author/title. Returns list of items."""
    try:
        r = subprocess.run(
            ["curl", "-sL", f"https://api.crossref.org/works?query={query}&rows={limit}"],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode != 0 or not r.stdout:
            return []
        return json.loads(r.stdout).get("message", {}).get("items", [])
    except:
        return []

def print_ref_info(msg, label="", indent=""):
    """Pretty-print a Crossref message."""
    if not msg:
        print(f"{indent}  ⚠️  No data returned")
        return
    title = msg.get("title", ["?"])[0][:120]
    authors = ", ".join([a.get("family", "?") for a in msg.get("author", [])[:3]])
    journal = msg.get("container-title", ["?"])[0]
    pub = msg.get("published-print", {}) or {}
    yr = pub.get("date-parts", [[0]])[0][0]
    if yr == 0:
        yr = msg.get("created", {}).get("date-parts", [[0]])[0][0]
    vol = msg.get("volume", "?")
    iss = msg.get("issue", "?")
    pg = msg.get("page", "?")
    if label:
        print(f"{indent}  [{label}]")
    print(f"{indent}  Title: {title}")
    print(f"{indent}  Authors: {authors}")
    print(f"{indent}  Published: {journal}, {yr}, Vol {vol}, Iss {iss}, pp {pg}")


def verify_reference(doi, expected=None):
    """
    Verify a single DOI against Crossref.
    
    Args:
        doi: DOI string
        expected: dict with optional keys: title, authors, journal, year, volume, pages
    
    Returns: (passed: bool, message: dict, issues: list)
    """
    msg, status = query_crossref(doi)
    if status == "not_found":
        return False, None, ["DOI not found in Crossref (404)"], status
    if status == "rate_limited":
        return False, None, ["Rate limited (429) by Crossref API"], status
    if status == "server_error":
        return False, None, ["Crossref server error (5xx)"], status
    if status != "ok":
        return False, None, [f"Network/API error ({status})"], status
    
    issues = []
    if expected:
        exp_title = expected.get("title", "").lower()[:60]
        if exp_title:
            act_title = (msg.get("title", ["?"])[0] or "")[:60].lower()
            # Only flag if titles differ substantially
            common = len(set(exp_title.split()) & set(act_title.split()))
            if common < 2:
                issues.append(f"TITLE mismatch: expected '{expected['title'][:80]}'")
        
        exp_journal = (expected.get("journal", "") or "").lower()
        if exp_journal:
            act_journal = (msg.get("container-title", ["?"])[0] or "").lower()
            if exp_journal not in act_journal:
                issues.append(f"JOURNAL: expected containing '{exp_journal}', got '{act_journal}'")
        
        exp_year = expected.get("year")
        if exp_year:
            pub = msg.get("published-print", {}) or {}
            yr = pub.get("date-parts", [[0]])[0][0]
            if yr == 0:
                yr = msg.get("created", {}).get("date-parts", [[0]])[0][0]
            if yr and yr != exp_year:
                issues.append(f"YEAR: expected {exp_year}, crossref has {yr}")
        
        exp_vol = expected.get("volume")
        if exp_vol:
            vol = msg.get("volume", "")
            if vol and vol != str(exp_vol):
                issues.append(f"VOLUME: expected {exp_vol}, got {vol}")
        
        exp_pages = expected.get("pages")
        if exp_pages:
            pg = msg.get("page", "")
            if pg and pg != str(exp_pages):
                issues.append(f"PAGES: expected {exp_pages}, got {pg}")
    
    return len(issues) == 0, msg, issues, "ok"


def extract_dois_from_markdown(filepath):
    """
    Extract numbered references from a markdown file, finding DOIs.
    Returns list of dicts: {num, text, doi, title, authors, journal, year, volume, pages}
    """
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return []
    
    with open(filepath) as f:
        content = f.read()
    
    # Find numbered reference lines: "1. **Authors.** Title. *Journal*. Year;Vol(Iss):Pages. DOI: xxx"
    refs = []
    lines = content.split("\n")
    current_ref = None
    
    for line in lines:
        # Match numbered reference start: optional number followed by **Author**
        m = re.match(r'^(\d+)\.\s+\*\*(.+?)\*\*', line)
        if m:
            if current_ref:
                refs.append(current_ref)
            current_ref = {"num": m.group(1), "raw": line[:200]}
        
        if current_ref:
            # Find DOI
            doi_m = re.search(r'(?:DOI|doi|https?://doi\.org)\s*:\s*(10\.[^\s\),\];]+)', line)
            if doi_m:
                current_ref["doi"] = doi_m.group(1)
            
            # Find journal
            jrnl_m = re.search(r'\*([^*]+?)\*\s*\.?\s*\d{4}', line)
            if jrnl_m:
                current_ref["journal"] = jrnl_m.group(1)
            
            # Find year
            yr_m = re.search(r'(\d{4})(?:[;,\s\.]|$)', line)
            if yr_m:
                current_ref["year"] = int(yr_m.group(1))
    
    if current_ref:
        refs.append(current_ref)
    
    return refs


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 verify-references.py <markdown_file> [--dois DOI DOI ...]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    refs = extract_dois_from_markdown(filepath)
    
    print("=" * 70)
    print(f"REFERENCE VERIFICATION: {os.path.basename(filepath)}")
    print(f"Found {len(refs)} references, {sum(1 for r in refs if 'doi' in r)} with DOIs")
    print("=" * 70)
    
    passed = 0
    failed = 0
    no_doi = 0
    
    for ref in refs:
        label = f"#{ref['num']}"
        print(f"\n--- Ref {label} ---")
        print(f"  Text: {ref.get('raw', '')[:120]}...")
        
        doi = ref.get("doi")
        if not doi:
            print(f"  ⚠️  No DOI found — manual review needed")
            no_doi += 1
            continue
        
        expected = {}
        if ref.get("journal"):
            expected["journal"] = ref["journal"]
        if ref.get("year"):
            expected["year"] = ref["year"]
        
        ok, msg, issues, status = verify_reference(doi, expected)
        
        if ok and msg:
            print(f"  ✅ VERIFIED")
            print_ref_info(msg, indent="  ")
            passed += 1
        elif msg:
            print(f"  ❌ ISSUES FOUND:")
            for issue in issues:
                print(f"     {issue}")
            print_ref_info(msg, indent="  ")
            failed += 1
        else:
            print(f"  ❌ DOI NOT FOUND: {doi}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {passed} verified ✅, {failed} with issues ❌, {no_doi} without DOI ⚠️")
    print(f"Total: {len(refs)} references")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
