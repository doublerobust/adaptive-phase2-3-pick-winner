# Adaptive Phase II/III Pick-a-Winner Design

**Literature review, intern brief, and simulation framework for adaptive seamless Phase II/III designs in oncology.**

## Background

Traditional oncology drug development runs Phase II and III as separate sequential trials — time-consuming and inefficient, with Phase II patients excluded from the final analysis.

This project explores a **single seamless Phase II/III design** that:

1. **Starts** with multiple doses or arms
2. **Selects** the "winner" at an interim analysis based on a short-term endpoint (ORR, binary, weeks)
3. **Confirms** with a long-term endpoint (OS, time-to-event, months–years)

The core statistical challenge: the different data types and imperfect correlation between ORR and OS mean the best ORR arm isn't guaranteed to be the best OS arm, and shared patient data between selection and testing creates bias that must be controlled.

## Contents

| File | Description |
|------|-------------|
| `pick-a-winner-lit-review.md` | Comprehensive literature review covering key methods (Stallard & Todd, Bauer & Posch, Dunnett, Magirr et al., Wu et al., Zhang & Jin) |
| `pick-a-winner-lit-review-v3.pdf` | Compiled PDF of the literature review |
| `pick-a-winner-intern-brief.md` | Intern-facing project brief with problem statement, key references, and guidance |
| `audit/` | Independent peer reviews by Gemini and Claude |

## Key Methods Covered

- **Stallard & Todd (2003)** — Foundational pick-the-winner: two-stage, K treatments → select best at interim via efficient score
- **Bauer & Posch (2004)** — Bias from reusing short-term data for selection and long-term data for testing
- **Dunnett (1955)** — Multiple comparison procedure for K treatments vs control
- **Magirr et al. (2012)** — MAMS for time-to-event endpoints
- **Wu et al. (2023)** — SCPRT-based MAMS with analytical boundaries
- **Zhang & Jin (2025)** — Multi-stage group sequential Phase 2/3 with ORR/PFS selection, OS confirmation

## Status

Literature review phase — simulation framework incoming.
