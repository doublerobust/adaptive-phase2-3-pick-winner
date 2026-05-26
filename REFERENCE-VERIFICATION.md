# Reference Verification Protocol

> How to ensure every citation in this project is real.
> Never trust untemplated reference text without independent verification.

---

## The Problem

This project's literature review contained **5 fake/wrong references** before systematic verification caught them. The root cause: I assumed existing reference text was correct instead of independently verifying each one against an authoritative source.

## The Protocol

### Step 1: Automated Crossref Check

Run the verification script against any markdown document:

```bash
python3 verify-references.py pick-a-winner-lit-review.md
```

This extracts all numbered references with DOIs, queries [Crossref API](https://api.crossref.org), and reports mismatches in title, authors, journal, year, volume, and pages.

### Step 2: Independent AI Review (Mandatory)

Never rely on the same model that wrote the references to verify them. Instead:

**Option A — Gemini API (preferred):**

```bash
source ~/.openclaw/.env
python3 verify-references.py document.md > /tmp/verify-report.txt

# Write the verification prompt
python3 -c "
import json
with open('/tmp/verify-report.txt') as f:
    report = f.read()
d = {'contents': [{'parts': [{'text': 'Independently verify these references...' + report}]}]}
json.dump(d, open('/tmp/payload.json','w'))
"

curl -s "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=${GOOGLE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @/tmp/payload.json
```

**Option B — Local Qwen (no API key needed):**

```bash
python3 verify-references.py document.md > /tmp/verify-report.txt

ollama run openclaw-qwen "Review this Crossref verification output for errors:
$(cat /tmp/verify-report.txt)

Flag any reference where the Crossref data doesn't match the document."
```

### Step 3: Fix and Re-Verify

1. Fix all issues the independent reviewer flagged
2. Re-run `verify-references.py` to confirm the fixes
3. No reference should be left with a mismatched DOI

## What the Script Checks

| Field | Source | What can go wrong |
|-------|--------|-------------------|
| DOI | Crossref API | Wrong DOI points to different paper |
| Title | Crossref API | Title doesn't match claimed content |
| Journal | Crossref API | Wrong journal name |
| Year | Crossref API | Year mismatch |
| Volume/Pages | Crossref API | Volume/pages don't match |

## When Verification Isn't Needed

- **Templated output** from a structure you control (e.g., auto-generated reference lists from `bibtex`)
- **Regulatory guidance** (ICH, FDA) — verify by URL/existence, not DOI
- **Book chapters** (Berry et al. 2002) — verify by publisher, not Crossref

## When Verification IS Needed

- **Any hand-written reference** in a markdown document
- **DOI copied from a PDF or citation** — these can be incorrect
- **References inherited from a previous version** of the document

## History

| Date | What was found | Impact |
|------|---------------|--------|
| 2026-05-26 | Bauer & Posch "main paper" — doesn't exist | Removed, corrected to letter |
| 2026-05-26 | Magirr "Stat Med TTE" paper — doesn't exist | Corrected to Biometrika paper |
| 2026-05-26 | Schmidli DOI was Bretz's DOI | Fixed |
| 2026-05-26 | Kelly/wrong DOI pointed to Hilliam | Replaced with real paper |
| 2026-05-26 | Mehta & Tsiatis wrong journal | Fixed |
| 2026-05-26 | Royston/Parmar wrong journal | Fixed |
| 2026-05-26 | Brannath wrong title, journal, volume | Fixed |
