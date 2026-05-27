# Adaptive Phase II/III Pick-a-Winner Design — Intern Brief

> Project: Adaptive seamless phase II/III designs for oncology trials using ORR/DOR for interim dose/arm selection, with OS as the final confirmatory endpoint

---

## 1. Problem Statement

Traditional oncology development runs Phase II and III as separate sequential trials. This wastes time and patients — Phase II patients cannot be pooled into the final analysis. The goal: a single seamless Phase II/III trial that starts with multiple doses/arms, picks the winner based on **ORR** (binary, weeks), then confirms with **OS** (time-to-event, months-years). The different data types and imperfect correlation create the core challenge — selecting the best ORR arm doesn't guarantee the best OS arm, and shared patient data between selection and testing creates statistical bias that must be addressed.

---

## 2. Key References

### 2.1 Core Papers (Full Text, Priority Order)

| # | Authors | Year | Journal | Key Contribution |
|---|---------|------|---------|-----------------|
| 1 | **Zhang EP, Jin M** ⭐ | 2025 | *Stat Biopharm Res* | **Primary method.** Multi-stage group sequential Phase 2/3; cohort-separation + inverse normal combination test + closed testing + Dunnett. Uses p-value combination (not MVN integration). |
| 2 | **Jenkins M, Stone A, Jennison C** | 2011 | *Pharm Stat* | **Cohort-separation origin.** Subpopulation selection with correlated TTE endpoints; Option A cleanly solves Bauer-Posch bias. Blueprint for unbiased TTE testing after interim selection. |
| 3 | Bauer P, Posch M | 2004 | *Stat Med* | Origin of Bauer-Posch bias: shared patients for short-term selection and long-term testing inflates type I error. Must-read before cohort-separation makes sense. |
| 4 | Stallard N, Todd S | 2003 | *Stat Med* | Foundational pick-the-winner via efficient score statistics (MVN approach). Supplementary — the logic informs the design structure, but Eric's p-value combination is the implementation path. |
| 5 | Sun LZ, Li W, Chen C, Zhao J | 2020 | *Stat Biopharm Res* | 2-in-1 design: benefit-cost criteria for when seamless designs are worth the complexity. Practical context. |
| 6 | Zhong W, Liu J, Wang C | 2025 | *Stat Med* | ρ(ORR, OS) formulas under PH + drop-the-losers design. Needed for correlation calibration. |
| 7 | Wang X, Chen M, Chu S, et al. | 2023 | *Contemp Clin Trials* | Rank-based Dunnett adjustment. Correlation matrix directly implementable for simulation. |
| 8 | Hua K, Wang X, Luo X | 2026 | *Stat Biopharm Res* | Closed testing + group-sequential for alternative approach (independent increment vs cohort-separation). Compare with Eric/Jenkins. |
| 9 | Magirr D, Jaki T, Whitehead J | 2012 | *Biometrika* | Generalized Dunnett for MAMS. Conditional-independence trick underpins Zhang & Jin covariance formulas. |
| 10 | Bretz F, Schmidli H, König F, et al. | 2006 | *Biom J* | Foundational framework for confirmatory seamless designs. |

**Reading order (revised, per mentor guidance):**

1. ⭐ **Zhang & Jin (2025)** — Eric's paper. Your primary method. Read first.
2. **Jenkins et al. (2011)** — Cohort-separation blueprint that Eric builds on.
3. **Bauer & Posch (2004)** — Understand *why* cohort-separation is necessary.
4. **Stallard & Todd (2003)** — Design logic and MVN background (read after you understand Eric's approach).
5. **Sun et al. (2020)** — Practical context for when seamless designs help.
6. **Zhong et al. (2025)** — ρ(ORR, OS) formulas for correlation calibration.
7. **Wang et al. (2023)** — Rank-based Dunnett for simulation.
8. **Hua et al. (2026)** — Alternative approach for comparison.
9. **Magirr et al. (2012)** — Conditional independence machinery.
10. **Bretz et al. (2006)** — Broader framework.

### 2.2 Further Reading (Abstract or Select Sections)

| Paper | One-Liner |
|-------|-----------|
| Jin & Zhang (2021), *Stat Methods Med Res* | Adaptive seamless Phase 2-3 with multiple endpoint closed testing |
| Schmidli et al. (2006), *Biom J* | Applications of Bretz et al. — practical implementation |
| Friede & Stallard (2008), *Biom J* | Compares 4 methods: Dunnett, adaptive Dunnett, combination test, group sequential |
| Dixit et al. (2021), *J Biopharm Stat* | MAMS for TTE with non-proportional hazards |
| Sydes et al. (2012), *Trials* | STAMPEDE — landmark MAMS implementation |
| Kelly et al. (2005), *Stat Med* | Practical MAMS implementation guide |
| Mehta & Tsiatis (2001), *Biometrics* | Information-based monitoring for interim timing with immature endpoints |
| Broglio et al. (2024), *Ther Innov Regul Sci* | Systematic review of adaptive seamless designs |
| Friede et al. (2019), *arXiv / R asd* | R package `asd` for treatment/subgroup selection |
| Wu et al. (2023), *Stat Med* | SCPRT-based MAMS with analytical futility/efficacy boundaries |

### 2.3 Bayesian Alternative (Brief)

Bayesian approaches (Berry et al. 2002; Lee & Liu 2008) use predictive probability: P(treatment beats control at final given interim data). Naturally handles ORR-OS correlation through the joint posterior. This project uses the frequentist framework because (1) regulators expect well-characterized frequentist type I error control, (2) cohort-separation cleanly solves the Bauer-Posch bias, (3) the literature you'll build on is almost entirely frequentist.

---

## 3. Design Options

**MAMS with Group Sequential (Zhang & Jin 2025, Jenkins et al. 2011).** ⭐ *Your primary candidate.* Inferentially seamless: one protocol, two cohorts. Cohort 1 randomized across K doses + control. After ORR-based selection, Cohort 2 enrolls selected dose + control. OS data from both cohorts combined via **inverse normal combination test** (p-value combination, not MVN integration). Group sequential looks. Cohort-separation avoids Bauer-Posch bias.

**2-in-1 Design (Jin & Zhang 2021, Sun et al. 2020).** Operationally seamless: separate protocols with continuous recruitment. Phase II data used for selection only, not pooled into Phase III. Simpler but less efficient than inferentially seamless.

**Drop-the-Losers (Zhong et al. 2025).** Uses ORR for selection. Derives ρ(ORR, OS) under PH; FWER inflation = f(ρ, Δ). When ρ = 0, no inflation. For solid tumors, ρ ∈ [0.3, 0.7].

**Rank-Based Dunnett (Wang et al. 2023).** Uses biomarker rank of selected dose to reduce multiplicity dimension. When ρ between biomarker and efficacy is known, exact 2m-dimensional MVN p-value. Correlation matrix directly implementable for simulation: corr(Eⱼ, Eₚ) = 1/2; corr(Eⱼ, Bⱼ) = ρ; corr(Eⱼ, Bₚ) = ρ/2.

**Subpopulation Selection (Jenkins et al. 2011).** Cohort-separation idea extended to patient subpopulations. Continue in all patients, subgroup, or both.

**Closed Testing + Group Sequential (Hua, Wang & Luo 2026).** Uses independent increment argument rather than cohort-separation. 8-hypothesis design (2 trt × 2 pop × 2 endpoints). Alternative justification to compare against.

---

## 4. Statistical Challenges

**FWER Control.** Must control across (1) selection among K doses and (2) multiple group sequential OS looks. Zhang & Jin uses closed testing + Dunnett + alpha spending via inverse normal combination. Any deviation from pre-specified selection rule (e.g., safety override) must preserve control.

**ρ(ORR, OS).** The central parameter. High ρ (≥ 0.7) → ORR selection nearly optimal for OS. Low ρ (≤ 0.3) → power loss. FWER ↑ monotonically with ρ. Calibrate from meta-analyses (Prasad et al. 2015).

**Bauer-Posch Bias.** Shared patients for selection and testing inflates type I error. Solved by cohort-separation (Jenkins 2011, Zhang & Jin 2025): only Cohort 1's ORR used for selection; OS from both cohorts combined via inverse normal combination test.

**Inverse Normal Combination Test (INCT).** The core p-value combination mechanism in Eric's paper. p-values from Cohort 1 and Cohort 2 are combined as C = w₁Φ⁻¹(1-p₁) + w₂Φ⁻¹(1-p₂), where w₁² + w₂² = 1. Under H₀, C ~ N(0,1). This is computationally simpler than Stallard & Todd's MVN integration and naturally extends to group sequential monitoring.

**Non-Proportional Hazards.** IO agents often show delayed separation (curves overlap 3-6 months). Violates PH assumptions in Zhang & Jin covariance formulas. Use weighted log-rank or RMST in sensitivity. Include delayed-separation scenarios (HR 1.0 → 0.75 over 6 months).

---

## 5. Simulation Roadmap (8 Weeks)

### Week 1 (in progress) — Deep Reading + First Implementation

**Reading:**
- ⭐ **Zhang & Jin (2025)** — full paper, multiple passes. Focus on:
  - Section 2: notation, dose selection rules, combination test
  - Section 3: closed testing procedure, Dunnett multiplicity adjustment
  - Section 4: simulation setup and results (Table 1-2)
  - Appendix: covariance derivation, R/\`rpact\` code patterns
- **Jenkins et al. (2011)** — focus on Option A (p.350): the cohort-separation mechanism
- **Bauer & Posch (2004)** — the bias problem that motivates everything

**Implementation:**
- Set up R project structure (`R/`, `inst/sims/`, `vignettes/`) from day one
- Implement the **two-arm two-stage INCT** — the simplest case in Zhang & Jin:
  1. Generate cohort 1: n₁ patients per arm, binary endpoint (ORR). Select winner.
  2. Generate cohort 2: n₂ patients in selected arm + control, binary endpoint.
  3. Compute p-values for each cohort (e.g., chi-square or Fisher exact for binary).
     For survival, use log-rank test.
  4. Combine via INCT: C = w₁Φ⁻¹(1-p₁) + w₂Φ⁻¹(1-p₂), weights w₁ = √(e₁/(e₁+e₂)).
  5. Reject H₀ if C ≥ z_α (one-sided α = 0.025).
- For binary→binary, validate: type I error ≈ 0.025 under H₀ across weight allocations

**Reading questions to answer:**
- Why does cohort-separation solve Bauer-Posch bias?
- How does INCT differ from Stallard & Todd's efficient score approach?
- What is the role of the closed testing procedure when K > 2?
- Why are weights w₁, w₂ proportional to √(expected events)?

**Deliverable:** Reading notes + working two-arm two-stage INCT in R. Type I error ≈ 0.025.

### Week 2 — Complete Two-Arm Validation + Dunnett Extension

- Extend to **TTE endpoints** within the INCT + cohort-separation framework:
  - Cohort 1: generate OS data (exponential or Weibull under PH)
  - Select arm with best OS at interim (since this is a simulation study, the "interim ORR" is emulated as a short follow-up OS assessment)
  - Cohort 2: generate additional OS data for selected arm + control
  - Combine log-rank p-values from each cohort via INCT
- Validate against Zhang & Jin Table 1 (type I error) and Table 2 (power) — target agreement within MC error (±0.003 for 10k reps)
- Add **Dunnett multiplicity adjustment** for K=3 arms: closed testing with 3 elementary hypotheses + intersection hypotheses
- **R package structure:** `R/inct_test.R`, `R/dunnett_closed.R`, `R/data_gen.R`
- **Deliverable:** Two-arm binary and TTE INCT validated. Three-arm Dunnett+INCT pilot working.

### Week 3 — Multi-Arm Binary→Binary Simulation

- Full binary→binary simulation (ORR both stages) to isolate the selection + combination methodology from TTE complexity
- **Design grid:**
  - K = 3 arms (2 experimental + control)
  - Stage 1 n₁ ∈ {30, 40, 60}/arm
  - Stage 2 n₂ ∈ {100, 150, 200} total (selected + control)
  - ORR control = 0.15, ORR exp ∈ {0.20, 0.30, 0.45}
  - Selection rule: pick arm with highest ORR (or safety override option)
  - Weights: w₁² = n₁ / (n₁ + n₂) | w₂² = n₂ / (n₁ + n₂)
- **Pilot phase (fast iteration):** 2-3 scenarios × 1k reps first to catch bugs
- **Compare selection rules:** pick-the-winner (best ORR) vs drop-the-losers (keep all with ORR > threshold)
- **Deliverable:** Binary→binary simulation results with MC standard errors. Selection rule comparison table.

### Week 4 — Multi-Arm TTE Simulation (Pilot + Validation)

- Implement **multi-state DGP** with Weibull transitions:
  - Alive without event → response (+ORR) → progression → death
  - ρ(ORR, OS) controlled via transition rate parameters
  - Calibrate ρ ∈ {0.3, 0.5, 0.7} using formulas from Zhong et al. (2025) and Prasad et al. (2015)
- **Full ORR→OS simulation:**
  - Interim at 40% of total expected events — use ORR for selection
  - Final analysis with OS, OS data from both cohorts combined via INCT
  - Closed testing for FWER control across K arms
- **Pilot grid (1k reps per cell, fast):**
  - ρ ∈ {0.3, 0.5, 0.7}
  - OS HR = {0.70, 0.80, 1.0 (null)}
  - K = 3 arms
- **Deliverable:** Working multi-state DGP + pilot ORR→OS results. Identify any bugs in correlation structure before scaling.

### Week 5 — Full-Scale ORR→OS Simulation

- **Full grid (5k-10k reps per scenario):**
  - K ∈ {2, 3, 4} arms
  - ρ ∈ {0.3, 0.5, 0.7}
  - OS HR ∈ {0.65, 0.70, 0.75, 0.80, 1.0}
  - Stage 1 sample sizes: n₁/arm ∈ {30, 50, 75}
  - Interim timing: info fraction ∈ {0.3, 0.5, 0.7}
- **Collect:**
  - Type I error (HR = 1.0) → should be ≤ 0.025 + MC error
  - Power curves by ρ and sample size
  - Probability of correct selection (PCS) — did the right arm win?
  - Probability of incorrect selection leading to OS failure
- **Deliverable:** Full simulation results with MC standard errors. Power × ρ × n₁ surfaces.

### Week 6 — Design Comparisons

- **Cohort-separation (Jenkins/Zhang) vs Independent-increment (Hua et al. 2026):**
  - Implement Hua's approach: no cohort separation, use independent increment argument for log-rank statistics
  - Compare type I error, power, and bias under same simulation scenarios
  - When does each approach dominate?
- **Pick-a-winner vs Drop-the-losers vs Traditional Phase 2+3:**
  - Implement standalone Phase II (select) + Phase III (confirm) with no pooling
  - Compare expected total sample size, duration, power
- **Carry-one vs carry-two arms forward:**
  - Carry-one: only selected arm continues to Cohort 2
  - Carry-two: top two arms continue (Dunnett adjustment increases)
- **Deliverable:** Design comparison results with clear takeaway table.

### Week 7 — Sensitivity Analysis

- **ρ calibration:** Vary ρ ∈ {0.1, 0.3, 0.5, 0.7, 0.9}. At what ρ does power drop below 80%?
- **Non-proportional hazards:**
  - Delayed separation: HR 1.0 → 0.75 over 6 months (weaning)
  - Early separation: HR 0.75 → 1.0 after 12 months (waning effect)
  - Compare log-rank vs weighted log-rank (Fleming-Harrington G^{1,0}) vs RMST
- **Safety-driven selection override:** 20% probability of selecting a non-optimal arm due to safety concerns. Does this meaningfully affect power?
- **Sample size misspecification:** ±20% from target. How robust are the operating characteristics?
- **Deliverable:** Complete sensitivity results with interpretation.

### Week 8 — Publication Prep

- **R package finalization:**
  - `R/` — documented functions for data generation, INCT, closed testing, Dunnett
  - `inst/sims/` — all simulation scripts with saved seeds
  - `vignettes/` — reproducible tutorial: simulate a pick-a-winner trial from start to finish
  - `README.md` — project overview with results summary
- **Figures:** power curves, PCS curves, FWER contours, design comparison plots
- **15-minute presentation:** problem → method → simulation results → conclusions
- **Written summary:** methodology draft with key findings and recommendations
- **Deliverable:** Complete R package + vignette + slides + written summary.

---

## 6. Implementation Notes

### Why INCT over Stallard & Todd's MVN Approach

Eric's paper uses the inverse normal combination test (p-value combination), not Stallard & Todd's multivariate normal integration. Key differences:

| Aspect | Stallard & Todd (MVN) | Zhang & Jin (INCT + cohort) |
|--------|----------------------|---------------------------|
| Computation | K-dimensional MVN integration | One-dimensional standard normal quantile |
| P-value source | Efficient score statistic at final analysis | Log-rank/score p-value per cohort |
| Bias control | Independent increments (ITT-based) | Cohort-separation (physical patient separation) |
| Flexibility | Harder to extend to group sequential | Natural fit — each cohort's p-value is independent |
| Software | Custom MVN integration or mvtnorm | `rpact` package or plain R |

**Start with INCT. It's simpler, more flexible, and directly matches Eric's framework.** Add MVN comparison only if operating characteristics differ meaningfully.

### Software Stack

| Tool | Use | Notes |
|------|-----|-------|
| **R 4.3+** | Primary simulation engine | |
| **`rpact`** | Group sequential boundaries, INCT | Actively maintained, regulatory-grade |
| **`survival`** | Log-rank test, Cox PH | |
| **`mvtnorm`** | Dunnett critical values, MVN probabilities | Needed for closed testing |
| **`copula`** | ORR-OS correlation | For multi-state DGP with specified ρ |
| **`parallel`** | Multi-core simulation | Use `mclapply` |
| **`data.table`** | Result aggregation | |
| **`ggplot2`** | Power curves, PCS plots, FWER contours | |
| **`targets`** | Workflow management for large sims | Optional but recommended for 10k-rep grids |

### Simulation Hygiene

- **Validate null first.** Type I error ≈ 0.025 before running any alternative.
- **Save RNG state.** `set.seed()` per scenario; save seed for every run.
- **Fix design parameters early.** N, n₁, α spending. Don't change mid-stream.
- **Report MC standard errors.** For 10k reps at α=0.025, SE ≈ 0.0016. At 5k reps, SE ≈ 0.0022.
- **Log everything.** Scenario parameters → file names with parameter values encoded.
- **Pilot before scale.** 2-3 scenarios × 1k reps identifies the bugs. Then 10k.
- **Build the R package from day one.** Not an afterthought in Week 8.

### Starting Parameters (Suggested Defaults)

| Parameter | Default | Range for Sensitivity |
|-----------|---------|----------------------|
| K (doses) | 3 | 2, 4 |
| Stage 1 n/arm | 50 | 30, 75 |
| Total N | 400 | 300, 600 |
| ORR control | 0.15 | — |
| ORR exp | 0.30 | 0.20, 0.45 |
| OS HR | 0.75 | 0.65, 0.70, 0.80, 1.0 |
| ρ(ORR, OS) | 0.5 | 0.3, 0.7 |
| α (one-sided) | 0.025 | — |
| Interim info fraction | 0.4 | 0.3, 0.5, 0.7 |
| Reps per scenario | 5,000 | 1,000 (pilot), 10,000 (final) |

---

## 7. Quick Reference: Zhang & Jin (2025) Core Elements

### Notation
- K: number of experimental doses
- nᵢⱼ: patients in Cohort j for arm i
- Sⱼ: test statistic for Cohort j (log-rank score or z-score)
- pⱼ: one-sided p-value from Cohort j
- INCT: C = w₁Φ⁻¹(1-p₁) + w₂Φ⁻¹(1-p₂), where w₁² + w₂² = 1
- Under H₀: C ~ N(0,1) → reject if C ≥ z_α

### Closed Testing Procedure (K = 3 arms)
- Elementary hypotheses: H_A, H_B (2 experimental vs control)
- Intersection hypotheses: H_A ∩ H_B
- Test H_A at level α only if both H_A and H_A ∩ H_B are rejected
- Dunnett critical value for H_A ∩ H_B: 2D MVN with correlation ρ̂
- Final decision: reject H_A only if INCT p_{A,1} ≤ adjusted threshold

### Cohort-Separation Key Idea
```
Cohort 1 (pre-selection):     A1, A2, B, Control   → ORR measured → pick winner
                                    ↓
Cohort 2 (post-selection):    Winner + Control      → OS measured
                                    ↓
Final analysis:               OS(Cohort1) + OS(Cohort2) via INCT
                              p₁ from Cohort 1 OS (log-rank, all arms)
                              p₂ from Cohort 2 OS (log-rank, winner vs control)
                              C = w₁Φ⁻¹(1-p₁) + w₂Φ⁻¹(1-p₂)
```

The key: **p₁ and p₂ are independent** because they come from disjoint patient cohorts. The selection rule only affects which arms contribute to p₂ (winner vs control), not the Cohort 1 p-value computation (which includes all originally randomized patients in their assigned arms according to ITT).

---

## 8. Reference List

**Core Papers**

1. Zhang EP, Jin M. A Multi-Arm Multi-Stage Group Sequential Phase 2/3 Design with Dose Selection for Oncology Trials. *Statistics in Biopharmaceutical Research*. 2025. DOI: 10.1080/19466315.2025.2539831.
2. Jenkins M, Stone A, Jennison C. An adaptive seamless phase II/III design for oncology trials with subpopulation selection using correlated survival endpoints. *Pharmaceutical Statistics*. 2011;10(4):347-356. DOI: 10.1002/pst.472.
3. Bauer P, Posch M. Letter to the Editor: Modification of the sample size and the schedule of interim analyses in survival trials based on data inspections. *Stat Med*. 2004;23(8):1333-1335. DOI: 10.1002/sim.1759.
4. Stallard N, Todd S. Sequential designs for phase III clinical trials incorporating treatment selection. *Stat Med*. 2003;22(5):689-703. DOI: 10.1002/sim.1362.
5. Sun LZ, Li W, Chen C, Zhao J. Advanced utilization of intermediate endpoints for making optimized cost-effective decisions in seamless phase II/III oncology trials. *Statistics in Biopharmaceutical Research*. 2020;12(2):224-233. DOI: 10.1080/19466315.2019.1665578.
6. Zhong W, Liu J, Wang C. Multiplicity control in oncology clinical trials with a binary surrogate endpoint-based drop-the-losers design. *Statistics in Medicine*. 2025;44:e70209. DOI: 10.1002/sim.70209.
7. Wang X, Chen M, Chu S, Fan R, Chan ISF. A rank-based approach to improve the efficiency of inferential seamless phase 2/3 clinical trials with dose optimization. *Contemporary Clinical Trials*. 2023;132:107300. DOI: 10.1016/j.cct.2023.107300.
8. Hua K, Wang X, Luo X. Multiplicity control in clinical trials with adaptive selection followed by group-sequential testing. *Statistics in Biopharmaceutical Research*. 2026. DOI: 10.1080/19466315.2026.2634636.
9. Magirr D, Jaki T, Whitehead J. A generalized Dunnett test for multi-arm multi-stage clinical studies with treatment selection. *Biometrika*. 2012;99(2):494-501. DOI: 10.1093/biomet/ass002.
10. Bretz F, Schmidli H, König F, Racine A, Maurer W. Confirmatory seamless phase II/III clinical trials with hypotheses selection at interim: general concepts. *Biometrical Journal*. 2006;48(4):623-634. DOI: 10.1002/bimj.200510232.

**Further Reading**

11. Prasad V, Kim C, Burotto M, Vandross A. The strength of association between surrogate end points and survival in oncology: a systematic review of trial-level meta-analyses. *JAMA Internal Medicine*. 2015;175(8):1389-1398.
12. Jin M, Zhang P. An adaptive seamless phase 2-3 design with multiple endpoints. *Statistical Methods in Medical Research*. 2021;30(4):1143-1151. DOI: 10.1177/0962280220986935.
13. Dixit V, Mitra S, Simonsen KL. Multi-arm multi-stage clinical trials for time-to-event outcomes. *Journal of Biopharmaceutical Statistics*. 2021;31(6):838-851. DOI: 10.1080/10543406.2021.1979575.
14. Sydes MR, Parmar MKB, Mason MD, et al. Flexible trial design in practice — stopping arms for lack-of-benefit and adding research arms mid-trial in STAMPEDE: a multi-arm multi-stage randomized controlled trial. *Trials*. 2012;13:168. DOI: 10.1186/1745-6215-13-168.
15. Kelly PJ, Stallard N, Todd S. An adaptive group sequential design for phase II/III clinical trials that select a single treatment from several. *Journal of Biopharmaceutical Statistics*. 2005;15(4):641-658. DOI: 10.1081/BIP-200062857.
16. Friede T, Stallard N, Parsons N. Seamless phase II/III clinical trials using early outcomes for treatment or subgroup selection: methods and aspects of their implementation. *arXiv:1901.08365*. 2019. [R package `asd`]
17. Mehta CR, Tsiatis AA. Flexible sample size considerations using information-based interim monitoring. *Drug Information Journal*. 2001;35(4):1095-1112. DOI: 10.1177/009286150103500407.
18. Stallard N, Todd S. A group-sequential design for clinical trials with treatment selection. *Statistics in Medicine*. 2008;27(29):6209-6227. DOI: 10.1002/sim.3436.
19. Broglio K, Cooner F, Wu Y, et al. A systematic review of adaptive seamless clinical trials for late-phase oncology development. *Therapeutic Innovation & Regulatory Science*. 2024;58:917-929. DOI: 10.1007/s43441-024-00670-1.
20. Schmidli H, Bretz F, Racine A, Maurer W. Confirmatory seamless phase II/III clinical trials with hypotheses selection at interim: applications and practical considerations. *Biometrical Journal*. 2006;48(4):635-643. DOI: 10.1002/bimj.200510233.
