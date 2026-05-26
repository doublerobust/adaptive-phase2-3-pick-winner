#!/usr/bin/env python3
"""
verify-claims.py — Grounded claim verification: extract PDF text, compare against manuscript.

PRINCIPLE:
    LLM never "remembers" what a paper says. Instead:
    1. Parse manuscript for citation anchors (§, Theorem, eq., Table, p.)
    2. Extract the relevant PDF text around each anchor (deterministic)
    3. Feed BOTH the manuscript claim AND the extracted PDF text to LLM
    4. LLM only compares: "does claim match extracted text?" — no memory required

Usage:
    # Verify claims in manuscript against PDFs in refs/
    python3 verify-claims.py manuscript.md --refs-dir refs/

    # Verify a single claim manually
    python3 verify-claims.py --claim "Struthers & Kalbfleisch (1986) Theorem 3.1: 0 < β* < α₁"
                            --pdf refs/struthers1986-misspecified-cox.pdf

Dependencies: pdftotext (poppler-utils), curl
"""

import subprocess, json, sys, os, re, argparse, textwrap
from pathlib import Path


# ─── PDF text extraction (deterministic) ──────────────────────────────────────

def pdf_to_text(pdf_path):
    """Extract all text from a PDF using pdftotext. Returns text or None."""
    try:
        r = subprocess.run(["pdftotext", pdf_path, "-"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return r.stdout
    except Exception as e:
        print(f"  ⚠️  pdftotext failed: {e}", file=sys.stderr)
    return None


def extract_around(text, query, context_lines=5):
    """
    Extract a window of text around the first occurrence of query.
    Returns (before, match_line, after) or None.
    """
    lines = text.split("\n")
    query_lower = query.lower()
    for i, line in enumerate(lines):
        if query_lower in line.lower():
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            return {
                "query": query,
                "line": i + 1,
                "before": "\n".join(lines[start:i]),
                "match": lines[i],
                "after": "\n".join(lines[i+1:end])
            }
    return None


def extract_all_around(text, queries, context_lines=5):
    """Extract windows for multiple queries. Returns list of results."""
    results = []
    for q in queries:
        r = extract_around(text, q, context_lines)
        if r:
            results.append(r)
    return results


# ─── Citation anchor parsing ──────────────────────────────────────────────────

# Patterns for citation anchors in manuscript text
ANCHOR_PATTERNS = [
    # "Struthers & Kalbfleisch (1986, §3-2; Theorem 3.1)"
    r'(?:§|Sec(?:tion)?\.?\s*)([\d\.\-]+)',
    # "Theorem 3.1", "Lemma 2", "Proposition 1"
    r'(?:Theorem|Lemma|Proposition|Corollary|Property)\s+([\d\.]+)',
    # "eq. (3.2)", "equation (3-2)"
    r'(?:eq|equation)\.?\s*[\(]?([\d\.\-]+)[\)]?',
    # "Table 1", "Figure 2"
    r'(?:Table|Figure)\s+([\d\.]+)',
    # "p. 431", "pp. 1047-1056"
    r'(?:pp?\.)\s*(\d+(?:[–\-]\d+)?)',
]

def parse_anchors(text, ref_label="(Author, Year)"):
    """
    Extract citation anchors from a text passage.
    Returns list of anchor dicts: {type, value, full_match}
    """
    anchors = []
    for pattern in ANCHOR_PATTERNS:
        for m in re.finditer(pattern, text):
            anchors.append({
                "type": pattern.__repr__(),
                "value": m.group(0),
                "ref": ref_label
            })
    return anchors


# ─── LLM comparison (constrained, no memory) ─────────────────────────────────

def ollama_compare(claim, pdf_context, model="openclaw-qwen:latest"):
    """
    Ask LLM to compare a manuscript claim against extracted PDF text.
    The LLM is told ONLY to compare the two texts — no training memory.
    """
    prompt = f"""You are a text comparison tool, not a research assistant. 
Your ONLY job is to determine whether CLAIM is consistent with EXTRACTED_TEXT.

Rules:
- Answer only: CONSISTENT / INCONSISTENT / INSUFFICIENT_EVIDENCE
- If EXTRACTED_TEXT is empty, answer INSUFFICIENT_EVIDENCE
- Do NOT use any knowledge from your training — only the two texts provided
- CONSISTENT = the claim accurately reflects what EXTRACTED_TEXT says
- INCONSISTENT = the claim contradicts what EXTRACTED_TEXT says
- INSUFFICIENT_EVIDENCE = EXTRACTED_TEXT doesn't contain enough info to verify

CLAIM:
{claim}

EXTRACTED_TEXT:
{pdf_context}

Answer (CONSISTENT / INCONSISTENT / INSUFFICIENT_EVIDENCE):"""

    try:
        r = subprocess.run(
            ["curl", "-s", "--connect-timeout", "30",
             "http://localhost:12345/api/generate",
             "-d", json.dumps({"model": model, "prompt": prompt, "stream": False})],
            capture_output=True, text=True, timeout=120
        )
        if r.returncode == 0:
            resp = json.loads(r.stdout).get("response", "")
            # Normalize
            for verdict in ["CONSISTENT", "INCONSISTENT", "INSUFFICIENT_EVIDENCE"]:
                if verdict in resp.upper():
                    return verdict
            return f"PARSE_ERROR: {resp[:100]}"
    except Exception as e:
        return f"LLM_ERROR: {e}"
    return "LLM_ERROR: No response"


# ─── Manuscript parsing ──────────────────────────────────────────────────────

def parse_manuscript_claims(filepath):
    """
    Parse a markdown manuscript and extract sentences containing citation anchors.
    
    Returns list of dicts: 
        {sentence, ref_label, anchors: [{type, value}], section}
    """
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return []
    
    with open(filepath) as f:
        content = f.read()
    
    # Split into sections (## headers)
    sections = re.split(r'\n(##\s+.+?)\n', content)
    
    # Map citation labels to PDF paths (from reference list)
    ref_map = {}
    # Parse reference list at end of document
    ref_lines = re.findall(r'^(\d+)\.\s+.+?\((\d{4})\)', content, re.MULTILINE)
    
    claims = []
    current_section = "Preamble"
    
    for i, part in enumerate(sections):
        if re.match(r'^##\s+', part):
            current_section = part.strip("# ").strip()
            continue
        if not current_section:
            continue
        
        # Extract sentences with citation anchors
        sentences = re.split(r'(?<=[.!])\s+', part)
        for sent in sentences:
            # Find citations like (Author, Year) or Author et al. (Year)
            citations = re.findall(r'(?:([A-Z][a-z]+(?:\s+(?:et\s+al\.|&\s+[A-Z][a-z]+))?)\s*\((\d{4})\)|\(([^)]+),\s*(\d{4})\))', sent)
            
            anchors = parse_anchors(sent)
            
            for cite in citations:
                author = cite[0] or cite[2][:40]
                year = cite[1] or cite[3]
                ref_label = f"{author.strip()} ({year})"
                
                if anchors or any(cite):
                    claims.append({
                        "sentence": sent.strip()[:300],
                        "ref_label": ref_label,
                        "section": current_section,
                        "anchors": anchors
                    })
    
    return claims


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Grounded claim verification against PDFs")
    parser.add_argument("manuscript", nargs="?", help="Path to markdown manuscript")
    parser.add_argument("--refs-dir", default="refs", help="Directory with reference PDFs")
    parser.add_argument("--claim", help="Single claim to check (for manual verification)")
    parser.add_argument("--pdf", help="Single PDF to check against (for manual verification)")
    parser.add_argument("--ollama-url", default="http://localhost:12345",
                       help="Ollama URL")
    parser.add_argument("--model", default="openclaw-qwen:latest")
    parser.add_argument("--context-lines", type=int, default=5,
                       help="Lines of context around each anchor")
    args = parser.parse_args()
    
    if args.claim and args.pdf:
        # Single claim mode
        pdf_text = pdf_to_text(args.pdf)
        if not pdf_text:
            print("❌ Could not extract text from PDF")
            sys.exit(1)
        
        anchors = parse_anchors(args.claim)
        
        # Normalize PDF text
        pdf_norm = re.sub(r'(THEOREM|LEMMA|SECTION|TABLE)\s+(\d+)\s+(\d+)',
                          r'\1 \2.\3', pdf_text, flags=re.IGNORECASE)
        pdf_norm = re.sub(r'(\d+)\s*[\-–]\s*(\d+)', r'\1-\2', pdf_norm)
        
        # Build queries: all anchor values + key numbers from claim
        queries = [a["value"] for a in anchors]
        # Also extract meaningful numbers (skip years like 1986, years > 1900)
        for num in re.findall(r'([\d\.\-]+)', args.claim):
            try:
                n = float(num.replace('-', '.').split('.')[0])
                if n < 1900:  # skip years
                    queries.append(num)
            except:
                queries.append(num)
        
        # Try normalized text first, then original
        results = extract_all_around(pdf_norm, queries, args.context_lines)
        if not results:
            results = extract_all_around(pdf_text, queries, args.context_lines)
        
        if results:
            context = "\n---\n".join(
                f"[Before {r['query']}]:\n{r['before']}\n"
                f">>> {r['match']}\n"
                f"[After]:\n{r['after']}"
                for r in results
            )
        else:
            # Fall back: search last pages for keywords
            context = "[Anchor not found in PDF]"
            for kw in ['result', 'theorem', 'conclusion', 'summary', 'discussion']:
                if kw in pdf_text.lower():
                    lines = pdf_text.split("\n")
                    for i, line in enumerate(lines):
                        if kw in line.lower():
                            context = "\n".join(lines[max(0,i-3):min(len(lines),i+50)])
                            break
                    break
            if context == "[Anchor not found in PDF]":
                context = pdf_text[:3000]
        
        print("=" * 70)
        print("CLAIM VERIFICATION (single claim)")
        print("=" * 70)
        print(f"\n📝 Claim:\n{textwrap.fill(args.claim, 70)}\n")
        print(f"📄 Extracted context ({len(context)} chars):\n{context[:1500]}...\n")
        
        verdict = ollama_compare(args.claim, context, args.model)
        print(f"\n🔍 Verdict: {verdict}")
        return
    
    if args.manuscript:
        print("=" * 70)
        print("CLAIM VERIFICATION: Batch Mode")
        print("=" * 70)
        print(f"Manuscript: {args.manuscript}")
        print(f"Refs dir:   {args.refs_dir}")
        print()
        
        claims = parse_manuscript_claims(args.manuscript)
        if not claims:
            print("❌ No claims with citation anchors found.")
            sys.exit(1)
        
        print(f"Found {len(claims)} claims with citation anchors.\n")
        
        results = []
        for i, c in enumerate(claims):
            print(f"[{i+1}/{len(claims)}] {c['section']} — {c['ref_label']}")
            print(f"  📝 {c['sentence'][:120]}...")
            
            if not c['anchors']:
                print(f"  ⚠️  No anchors (eq/theorem/table refs) — PDF needed for full check")
                results.append((c, "NO_ANCHORS", "No anchors found"))
                continue
            
            # Find matching PDF
            pdf_files = list(Path(args.refs_dir).glob("*.pdf"))
            # Try to match by author/year from ref label
            ref_lower = c['ref_label'].lower().replace(" et al.", "")
            matched_pdf = None
            for pf in pdf_files:
                pf_name = pf.stem.lower()
                for word in ref_lower.replace("(", "").replace(")", "").split()[:3]:
                    if word in pf_name:
                        matched_pdf = pf
                        break
                if matched_pdf:
                    break
            
            if not matched_pdf:
                print(f"  ⚠️  No PDF for {c['ref_label']} in {args.refs_dir}")
                results.append((c, "NO_PDF", "PDF not found"))
                continue
            
            # Extract text from PDF
            pdf_text = pdf_to_text(str(matched_pdf))
            if not pdf_text:
                print(f"  ⚠️  Could not extract PDF text")
                results.append((c, "PDF_ERROR", "Text extraction failed"))
                continue
            
            # Search for anchors in PDF
            queries = [a["value"] for a in c['anchors']]
            # Also extract bare numbers from anchor values
            for a in c['anchors']:
                nums = re.findall(r'([\d\.]+)', a["value"])
                queries.append(nums[0])
            
            # Normalize PDF text: collapse spaces in special sequences
            # e.g. "THEOREM 3 1" → "THEOREM 3.1", "3 - 2" → "3-2"
            pdf_norm = re.sub(r'(THEOREM|LEMMA|SECTION|TABLE)\s+(\d+)\s+(\d+)',
                              r'\1 \2.\3', pdf_text, flags=re.IGNORECASE)
            pdf_norm = re.sub(r'(\d+)\s*[\-–]\s*(\d+)', r'\1-\2', pdf_norm)
            
            # Do normalized search first
            contexts = extract_all_around(pdf_norm, queries, args.context_lines)
            if not contexts:
                # Fall back to original text
                contexts = extract_all_around(pdf_text, queries, args.context_lines)
            
            if not contexts:
                print(f"  ⚠️  Anchor '{queries[0]}' not found in PDF — trying last page")
                lines = pdf_text.split("\n")
                fallback = "\n".join(lines[-100:])
                verdict = ollama_compare(c['sentence'], fallback, args.model)
                print(f"  🔍 {verdict} (fallback — anchor not located)")
                results.append((c, verdict, "Fallback to last page"))
                continue
            
            context_str = "\n---\n".join(
                f"[Before {r['query']}]:\n{r['before']}\n"
                f">>> {r['match']}\n"
                f"[After]:\n{r['after']}"
                for r in contexts
            )
            
            verdict = ollama_compare(c['sentence'], context_str, args.model)
            print(f"  🔍 {verdict}")
            results.append((c, verdict, context_str[:200]))
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        counts = {"CONSISTENT": 0, "INCONSISTENT": 0, "INSUFFICIENT_EVIDENCE": 0,
                  "NO_ANCHORS": 0, "NO_PDF": 0, "PDF_ERROR": 0}
        for c, verdict, _ in results:
            if verdict in counts:
                counts[verdict] += 1
            else:
                counts[verdict] = 1
        
        print(f"  ✅ Consistent:            {counts['CONSISTENT']}")
        print(f"  ❌ Inconsistent:          {counts['INCONSISTENT']}")
        print(f"  ⚠️  Insufficient evidence: {counts['INSUFFICIENT_EVIDENCE']}")
        print(f"  📄 No anchors:            {counts['NO_ANCHORS']}")
        print(f"  📄 PDF needed:            {counts['NO_PDF']}")
        print(f"  ⚠️  PDF error:             {counts['PDF_ERROR']}")
        print(f"  Total:                    {sum(counts.values())}")
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()
