# Viewed Listing + Document Review Workflow

Use this when you have already viewed a property or are preparing to review the
documents after a viewing.

## Folder convention

Put every document for one property in its own folder:

```text
viewing/<address-or-short-name>/
├── jaarverslag.pdf
├── balans.pdf
├── MJOP.pdf
├── notulen.pdf
├── vragenlijst.pdf
└── documents-summary.md        # generated after review
```

Use a stable folder name, for example `viewing/gooise-kant-374/` or
`viewing/Hoofdweg 854V Hoofddorp/`.

## Ask Codex

Paste the Funda link and tell Codex which viewing folder to inspect:

```text
Follow dutch-home-analyze and dutch-home-vve.

Funda link:
<paste Funda URL>

Viewing folder:
dutch-home-purchase/viewing/<folder-name>/

Tasks:
1. Extract useful listing information from the Funda page. If Funda blocks access,
   ask me only for the missing fields.
2. Add or update the listing in data/listings.json as a viewed listing.
3. Inspect every document in the viewing folder.
4. Write a per-document summary and risk review to
   viewing/<folder-name>/documents-summary.md.
5. Update the listing with vve_analysis and viewing_documents fields.
6. Run python3 scripts/regenerate_all.py.
7. Tell me the key risks, bid impact, and dashboard path.
```

## Dashboard fields

For a property to appear in the "已看房 · Documents Review" dashboard section,
the listing should contain at least one of these:

```json
{
  "status": "viewed",
  "viewing_completed": true,
  "viewing_date": "2026-07-04",
  "viewing_folder": "viewing/gooise-kant-374"
}
```

Document review details should use this shape:

```json
{
  "viewing_documents": {
    "folder": "viewing/gooise-kant-374",
    "summary_path": "viewing/gooise-kant-374/documents-summary.md",
    "overall_risk_level": "medium",
    "documents": [
      {
        "filename": "MJOP.pdf",
        "type": "MJOP",
        "summary": "Near-term facade maintenance appears in the plan.",
        "risks": ["planned_major_work"],
        "follow_up_questions": [
          "Is this work fully funded by the reservefonds?"
        ]
      }
    ]
  }
}
```

## What the review should inspect

For each document, summarize what matters for bidding:

- Annual report / jaarverslag: income, reservefonds, debts, arrears.
- Balance sheet / balans: cash, reserves, liabilities, owner arrears.
- MJOP: upcoming roof, facade, lift, painting, sustainability costs.
- Meeting minutes / notulen: voted special levies, disputes, delayed repairs.
- Splitsingsakte / regulations: ownership boundaries and restrictions.
- Questionnaire / vragenlijst: seller disclosures, moisture, defects, legal issues.
- Energy label / measurement report: energy risk and usable area mismatch.

Red flags should use consistent keys where possible:

```text
low_reservefonds
planned_major_work
special_assessment
achterstallig_onderhoud
active_dispute
split_vve_entities
high_vve_fee
erfpacht_trap
measurement_mismatch
seller_disclosure_issue
```

## Regenerate the dashboard

From the project folder:

```bash
cd dutch-home-purchase
python3 scripts/regenerate_all.py
```

Then open:

```text
dashboard/index.html
```

The new "已看房 · Documents Review" section shows viewed listings, risk level,
document count, summary link, and VvE/document risk notes.
