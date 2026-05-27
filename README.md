# Adaptive Phase II/III Pick-a-Winner Design

> **Literature review, intern brief, and simulation framework for adaptive seamless Phase II/III designs in oncology.**
>
> *Project at Merck — Statistical Methodology*

[![Status: Literature Review Complete](https://img.shields.io/badge/status-literature%20review%20complete-blueviolet)]()
[![Next: Simulation Framework](https://img.shields.io/badge/next-simulation%20framework-yellow)]()

## Background

Traditional oncology drug development runs Phase II and III as **separate sequential trials** — time-consuming and inefficient, with Phase II patients excluded from the final analysis.

This project explores a **single seamless Phase II/III design** that:

1. **Starts** with multiple doses or arms
2. **Selects** the "winner" at an interim analysis based on a **short-term endpoint** (ORR, binary, weeks)
3. **Confirms** with a **long-term endpoint** (OS, time-to-event, months–years)

The core statistical challenge: different data types and imperfect correlation between ORR and OS mean the best ORR arm isn't guaranteed to be the best OS arm, and shared patient data between selection and testing creates bias that must be controlled.

## Contents

| File | Description |
|------|-------------|
| `pick-a-winner-lit-review.md` | Comprehensive literature review — Stallard & Todd, Bauer & Posch, Dunnett, Magirr et al., Wu et al., Wang et al. (rank-based), Zhang & Jin, Zhong et al. (DTL), Hua et al. (closed testing + GS), Sun et al. (2-in-1), Jenkins et al. (cohort-separation), Broglio et al. (survey) |
| `pick-a-winner-lit-review-v3.pdf` | Compiled PDF of the literature review |
| `pick-a-winner-intern-brief.md` | Intern-facing project brief with 8-week implementation plan |
| `audit/` | Independent peer reviews by [Gemini 2.5 Pro](./audit/gemini-review-lit-v2.md) and [Claude Opus 4](./audit/claude-review-lit-v2.md) |

## Key Methods Covered

| Method | Key Reference | Role |
|--------|--------------|------|
| Pick-the-winner | Stallard & Todd (2003) | Two-stage, K treatments → select best at interim via efficient score |
| Bias from endpoint reuse | Bauer & Posch (2004) | Why shared patient data between ORR interim and OS final inflates type I error |
| Multiple comparison | Dunnett (1955) | K treatments vs control adjustment |
| Generalized Dunnett for MAMS | Magirr et al. (2012) | Multi-arm multi-stage boundary computation via conditional independence (normal endpoints) |
| SCPRT-based MAMS | Wu et al. (2023) | Analytical boundaries for multi-stage selection |
| Rank-based Dunnett | Wang et al. (2023) | Shortcut adjustment using biomarker rank; more powerful than Šidák when r < m |
| Cohort separation + INCT | Zhang & Jin (2025) | Multi-stage group sequential Phase 2/3 with short-term selection, long-term confirmation |
| ρ(ORR, OS) formulas | Zhong et al. (2025) | Analytic correlation derivation under PH + DTL design with software |
| Closed testing + group-sequential | Hua, Wang & Luo (2026) | 8-hypothesis framework with independent increment argument |
| Cohort separation | Jenkins et al. (2011) | Clean framework for unbiased final testing after interim selection |
| 2-in-1 benefit-cost | Sun et al. (2020) | Benefit-cost ratio criteria for when seamless is worth the complexity |
| Seamless survey | Broglio et al. (2024) | Systematic review of adaptive seamless designs in late-phase oncology |

## Project Phases

The intern implementation spans **8 weeks** (Summer 2026):

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | Read Zhang & Jin (2025) [Eric's paper] + Jenkins (2011) + Bauer & Posch (2004). Implement two-arm INCT + cohort-separation from scratch. | Working INCT reproduction; type I ≈ 0.025 |
| 2 | Validate TTE INCT against published tables. Add Dunnett for K=3 arms. Start R package. | K=3 Dunnett+INCT validated |
| 3 | Multi-arm binary→binary simulation. Compare selection rules (pick-winner vs DTL). Pilot 1k reps. | Binary→binary pilot + selection comparison |
| 4 | Multi-state DGP (ORR→OS). Pilot ORR→OS with ρ ∈ {0.3, 0.5, 0.7}. | Multi-state DGP + pilot results |
| 5 | Full-scale ORR→OS simulation grid (5k-10k reps). | Full grid with MC standard errors |
| 6 | Design comparisons: cohort-sep vs independent-increment, pick-winner vs DTL vs traditional, carry-one vs carry-two. | Design comparison results |
| 7 | Sensitivity: ρ calibration, non-PH, safety override, sample size misspecification. | Sensitivity results |
| 8 | R package, vignette, figures, 15-min presentation, written summary. | Complete R package + slides |

```mermaid
gantt
title Project Roadmap
    dateFormat  YYYY-MM
    section Phase 1
    Literature Review         :done, 2026-04, 2026-05
    Expert Peer Review        :done, 2026-05-20, 2026-05-21
    Intern Onboarding         :done, 2026-05, 2026-06
    section Phase 2 (Intern — 8 weeks)
    Week 1-2: INCT Foundation   :2026-06-01, 14d
    Week 3-4: Pilot & DGP       :2026-06-15, 14d
    Week 5-6: Full Sim & Design :2026-06-29, 14d
    Week 7-8: Sens & Pkg        :2026-07-13, 14d
```

## Peer Review Summary

Both **Gemini 2.5 Pro** and **Claude Opus 4** reviewed the literature review independently. Key findings:

| Area | Verdict |
|------|---------|
| Gemini | **Major Revision** — missing MAMS TTE references (Magirr 2012, Bauer & Posch 2004), structural fragmentation from v1→v2 merge |
| Claude | **Minor Revision** — add Bayesian methods section, estimand alignment discussion, fix multi-state model spec |
| Consensus | Strong foundation. Intern team revised starting point: begin with Zhang & Jin (2025) INCT + cohort-separation (p-value combination, simpler), not Stallard & Todd (2003) MVN integration. Stallard & Todd is supplementary background. |

Full reviews:
- 📄 [Claude Opus 4 Review](./audit/claude-review-lit-v2.md)
- 📄 [Gemini 2.5 Pro Review](./audit/gemini-review-lit-v2.md)

## For the Intern

See the [intern brief](./pick-a-winner-intern-brief.md) for the **8-week timeline**.

1. **Read the [intern brief](./pick-a-winner-intern-brief.md) first** — it frames the problem and your task
2. **Read the [literature review](./pick-a-winner-lit-review.md)** for the full picture
3. **Read the peer reviews** in `audit/` — they contain practical simulation advice and critical caveats
4. **Prioritized reading order** (per mentor team):
   1. ⭐ Zhang & Jin (2025) — Eric's paper, p-value combination, primary method
   2. Jenkins et al. (2011) — cohort-separation blueprint
   3. Bauer & Posch (2004) — understand why cohort-separation is necessary
   4. Stallard & Todd (2003) — design logic (MVN background)
   5. Sun et al. (2020) — most directly applicable setting

### Key Simulation Tips

- **Start with INCT + cohort-separation** (Zhang & Jin 2025) — p-value combination is simpler than MVN integration. Stallard & Todd's MVN approach is supplementary.
- **Binary→binary first** (ORR both stages) before adding TTE complexity
- **Pilot phase early** — run 2–3 scenarios × 1k reps after binary→binary to catch bugs
- **Validate null first** — confirm exact 0.025 type I error before running alternatives
- **Use `rpact`** — actively maintained, supports INCT, group sequential, and alpha spending natively
- **Build the R package from day one** — `R/`, `inst/sims/`, `vignettes/`
- **Save full state** (RNG seed, parameters, full results) on every run — you'll need it for debugging down the line
- **Expect 3–4 slow weeks** at the start — bugs in correlation structure, selection rules, and combination tests take time to track down
- **Calibrate ρ(ORR, OS) from published meta-analyses** (Prasad et al. 2015), not raw historical data
- **Include sensitivity for non-PH** (delayed separation typical in immuno-oncology) and safety-driven selection

## Status

✅ Literature review complete
✅ Expert peer reviews complete (Gemini + Claude)
✅ Intern onboarding complete
✅ Intern brief aligned with 8-week plan
⬜ Simulation framework — Phase 2 (intern, Summer 2026)

## Related Repos

- [Small Strata Pooling](https://github.com/doublerobust/small-strata-pooling) — How to handle sparse stratification with standard analysis methods
- [Ridge-Cal](https://github.com/doublerobust/ridge-cal) — Regularized calibration of external prognostic scores using blinded trial data

---

*Merck & Co., Inc., Rahway, NJ, USA*
