# Adaptive Phase II/III Pick-a-Winner Design — Intern Brief

> Project: Adaptive seamless phase II/III designs for oncology trials using ORR/DOR for interim dose/arm selection, with OS as the final confirmatory endpoint

---

## 1. Problem Statement

Traditional oncology development runs Phase II and III as separate sequential trials. This wastes time and patients — Phase II patients cannot be pooled into the final analysis. The goal: a single seamless Phase II/III trial that starts with multiple doses/arms, picks the winner based on **ORR** (binary, weeks), then confirms with **OS** (time-to-event, months-years). The different data types and imperfect correlation create the core challenge — selecting the best ORR arm doesn't guarantee the best OS arm, and shared patient data between selection and testing creates statistical bias that must be addressed.

---

## 2. Key References

### 2.1 Core Papers (Full Text)

| # | Authors | Year | Journal | Key Contribution |
|---|---------|------|---------|-----------------|
| 1 | Stallard & Todd | 2003 | *Stat Med* | Foundational pick-the-winner: two-stage, K treatments → select best at interim via efficient score. Works for binary, normal, TTE. |
| 2 | Bauer & Posch | 2004 | *Stat Med* | Origin of Bauer-Posch bias: using same patients' short-term data for selection and long-term for testing inflates type I error. |
| 3 | Dunnett | 1955 | *JASA* | Classic multiple comparison: K treatments vs control with FWER control. Building block for all pick-a-winner multiplicity adjustments. |
| 4 | Magirr et al. | 2012 | *Biometrika* | Generalized Dunnett test for MAMS with normal endpoints; boundary computation via conditional independence. TTE extension in Zhang & Jin (2025). |
| 5 | Wu et al. | 2023 | *Stat Med* | SCPRT-based MAMS. Analytical futility/efficacy boundaries for arbitrary stages/arms. Continuous outcomes only. |
| 6 | Wang et al. | 2023 | *Contemp Clin Trials* | Rank-based Dunnett adjustment; accounts for biomarker rank + correlation ρ; more powerful than Šidák when selected dose is not best biomarker responder. |
| 7 | Hua et al. | 2026 | *Stat Biopharm Res* | Closed testing + group-sequential p-values after ORR-based selection; 8-hypothesis design (2 trt × 2 pop × 2 endpoints); independent increment argument for X[1]/X[2]. |
| 6 | Zhang & Jin | 2025 | *Stat Biopharm Res* | **Directly addresses your setting.** Multi-stage group sequential Phase 2/3 with dose selection via ORR/PFS, OS as final. Cohort-separation + inverse normal combination + closed testing. |

**Stallard & Todd (2003).** The foundational design: K experimental arms vs control, select the most promising at interim via efficient score statistic, continue with selected arm + control. All patients from both stages included in the final test with multiplicity adjustment. Handles binary, normal, or failure-time data uniformly. Start here — implement this two-stage design first.

**Bauer & Posch (2004).** Demonstrates that using the same patients' short-term endpoint for selection and long-term for final testing inflates type I error. The magnitude depends on ρ between endpoints, the selection rule, and patient overlap. Motivated cohort-separation designs (Jenkins 2011, Zhang & Jin 2025).

**Dunnett (1955).** Exact critical values for comparing multiple treatments vs a single control with FWER control. The multivariate normal distribution of Dunnett statistics is the foundation for multiplicity adjustment throughout this literature.

**Magirr et al. (2012).** Generalized Dunnett test for MAMS with a normally distributed endpoint. Derives efficacy and futility boundaries for arbitrary numbers of arms and stages by exploiting conditional independence of test statistics given the control mean. Theorem 1 proves strong FWER control. The conditional-independence trick (conditioning on the control arm path) is the computational foundation that later TTE extensions build on — see Zhang & Jin (2025) for the TTE adaptation of this covariance structure.

**Wu et al. (2023).** SCPRT-based group sequential MAMS yielding analytical boundaries for any number of stages and arms, avoiding the exponential complexity of Magirr et al.'s search. Continuous outcomes only; boundary structure can be adapted for TTE.

**Wang et al. (2023).** Rank-based Dunnett adjustment for seamless 2/3 designs where dose selection uses a biomarker with correlation ρ to the efficacy endpoint. If the selected dose's biomarker rank is r < m (not the best responder), multiplicity adjustment reduces dimension, improving power vs Šidák. The correlation matrix (Table 1) gives: corr(Eⱼ, Eₚ) = 1/2; corr(Eⱼ, Bⱼ) = ρ; corr(Eⱼ, Bₚ) = ρ/2 for j ≠ p. Uses inverse normal combination test with rank-adjusted p-values. Very practical for simulation—the correlation structure is directly implementable.

**Hua, Wang & Luo (2026).** Two-stage design where ORR at IA1 drives a 5-branch selection tree (Figure 1: stop, enrich BM+, select treatment, etc.). After selection, PFS/OS tested via group-sequential with 3 additional looks. Uses **closed testing + group-sequential p-values** rather than cohort-separation. Argues via the log-rank independent increment property that Stage-1 and Stage-2 test statistics are independent even with shared patients — a different justification than Zhang & Jin's cohort-separation. The 8-hypothesis structure (2 treatments × 2 populations × 2 endpoints) is more complex than our setting, but the multiplicity machinery is directly portable.

**Zhang & Jin (2025).** Your most important paper. Extends two-stage seamless to **multi-stage group sequential** with TTE endpoints and dose selection via ORR/PFS. Key innovations: (1) **cohort-separation** — Cohort 1 (pre-selection, all arms) and Cohort 2 (post-selection, selected arm + control) combined via inverse normal combination with weights proportional to expected events; (2) **explicit covariance formula** for combined test statistics across stages; (3) **closed testing + Dunnett** for FWER at one-sided 0.025. Simulation confirms type I error control and favorable operating characteristics vs traditional Phase 2 + Phase 3.

### 2.2 Further Reading (Abstract Only)

| Paper | One-Liner |
|-------|-----------|
| Jin & Zhang (2021), *Stat Methods Med Res* | Adaptive seamless Phase 2-3 with multiple endpoint closed testing |
| Jenkins et al. (2011), *Pharm Stat* | Original cohort-separation using correlated different TTE endpoints |
| Bretz et al. (2006), *Biom J* | Foundational framework for confirmatory seamless designs |
| Schmidli et al. (2006), *Biom J* | Applications of Bretz et al. — practical implementation |
| Friede & Stallard (2008), *Biom J* | Compares 4 methods: Dunnett, adaptive Dunnett, combination test, group sequential |
| Sun et al. (2020), *Stat Biopharm Res* | ORR/PFS for adaptive seamless decisions; 2-in-1 design |
| Dixit et al. (2021), *J Biopharm Stat* | MAMS for TTE with non-proportional hazards |
| Sydes et al. (2012), *Trials* | STAMPEDE — landmark MAMS implementation |
| Kelly et al. (2005), *Stat Med* | Practical MAMS implementation guide |
| Mehta & Tsiatis (2001), *Biometrics* | Information-based monitoring for interim timing with immature endpoints |
| Zhong et al. (2025), *Stat Med* | Derives ρ(ORR, OS) analytically; drop-the-losers |
| Broglio et al. (2024), *Ther Innov Regul Sci* | Systematic review of adaptive seamless designs |
| Friede et al. (2019), *arXiv / R asd* | R package `asd` for treatment/subgroup selection |

### 2.3 Bayesian Alternative (Brief)

Bayesian approaches (Berry et al. 2002; Lee & Liu 2008) use predictive probability: P(treatment beats control at final given interim data). Naturally handles ORR-OS correlation through the joint posterior. This project uses the frequentist framework because (1) regulators expect well-characterized frequentist type I error control, (2) cohort-separation cleanly solves the Bauer-Posch bias, (3) the literature you'll build on is almost entirely frequentist.

---

## 3. Design Options

**2-in-1 Design (Jin & Zhang 2021, Sun et al. 2020).** Operationally seamless: separate protocols with continuous recruitment. Phase II data used for selection only, not pooled into Phase III. Simpler but less efficient than inferentially seamless.

**MAMS with Group Sequential (Zhang & Jin 2025, Magirr et al. 2012).** † *Your primary candidate.* Inferentially seamless: one protocol, two cohorts. Cohort 1 randomized across K doses + control. After ORR-based selection, Cohort 2 enrolls selected dose + control. OS combined via inverse normal combination. Group sequential looks. Cohort-separation avoids Bauer-Posch bias.

**Drop-the-Losers (Zhong et al. 2025).** Uses ORR for selection. Derives ρ(ORR, OS) under PH; FWER inflation = f(ρ, Δ). When ρ = 0, no inflation. For solid tumors, ρ ∈ [0.3, 0.7].

**Rank-Based Dunnett (Wang et al. 2023).** Uses biomarker rank of selected dose to reduce multiplicity dimension. When ρ between biomarker and efficacy is known, exact 2m-dimensional MVN p-value. When ρ is unknown, rank-based Dunnett shortcut (r-th order statistic of m-dim t-distribution). More powerful than Šidák when selected dose is not the best biomarker responder. Correlation matrix directly implementable for simulation: corr(Eⱼ, Eₚ) = 1/2; corr(Eⱼ, Bⱼ) = ρ; corr(Eⱼ, Bₚ) = ρ/2.

**Subpopulation Selection (Jenkins et al. 2011).** *Abstract only.* Continue in all patients, subgroup, or both. Cohort-separation idea inspired Zhang & Jin.

**SCPRT Boundaries (Wu et al. 2023).** Analytical futility/efficacy boundaries for any stages×arms. Continuous outcomes; adaptable.

---

## 4. Statistical Challenges

**FWER Control.** Must control across (1) selection among K doses and (2) multiple group sequential OS looks. Zhang & Jin uses closed testing + Dunnett + alpha spending. Any deviation from pre-specified selection rule (e.g., safety override) must preserve control.

**ρ(ORR, OS).** The central parameter. High ρ (≥ 0.7) → ORR selection nearly optimal for OS. Low ρ (≤ 0.3) → power loss. FWER ↑ monotonically with ρ. Calibrate from meta-analyses (Prasad et al. 2015).

**Bauer-Posch Bias.** Shared patients for selection and testing inflates type I error. Solved by cohort-separation: only Cohort 1's ORR used for selection; OS from both cohorts combined via combination tests.

**Non-Proportional Hazards.** IO agents often show delayed separation (curves overlap 3-6 months). Violates PH assumptions in Zhang & Jin covariance formulas. Use weighted log-rank or RMST in sensitivity. Include delayed-separation scenarios (HR 1.0 → 0.75 over 6 months).

---

## 5. Simulation Roadmap (8 Weeks)

| Week | Focus | Deliverable |
|------|-------|-------------|
| **1–2** | **Read (full PDFs in `refs/`):** Stallard & Todd (2003) [pick-winner foundation], Bauer & Posch (2004) [bias warning], Jenkins et al. (2011) [cohort-separation], Sun et al. (2020) [2-in-1], Zhang & Jin (2025) [primary method], Zhong et al. (2025) [ρ formula], Wang et al. (2023) [rank-based Dunnett], Hua et al. (2026) [closed testing + GS]. Implement Stallard & Todd two-arm two-stage in R. Validate against published tables. Use `gsDesign`/`rpact` for group sequential guts. | Paper notes + working Stallard & Todd reproduction; type I error ≈ 0.025 ± MC error. |
| **3–4** | Implement binary→binary simulation (ORR both stages) to validate methodology without TTE complexity. **Pilot phase:** small grid (2–3 scenarios × 1k reps) to catch bugs and bottlenecks. Debug null first. Add multi-state DGP with Weibull transitions. | Working binary→binary sim + pilot results. |
| **5–6** | Full ORR→OS simulation with multi-state DGP and copula correlation. Run null + alternatives. Include safety-driven selection and non-PH (delayed separation). **Compare cohort-separation (Jenkins/Zhang) vs independent-increment (Hua).** 5k–10k reps per scenario. | Full simulation grid with MC standard errors. |
| **7** | Sensitivity: ρ ∈ {0.3, 0.5, 0.7} calibrated from Prasad et al. (2015). Compare pick-a-winner vs drop-the-losers vs traditional Phase 2+3. Compare carry-one vs carry-two arms. | Sensitivity results. |
| **8** | Draft methodology + figures (power curves, PCS curves, FWER contours). Reproducible vignette. Build as R package (`R/`, `inst/sims/`, `vignettes/`). | R package + vignette + 15-min presentation. |

**Starting parameters:** K=2-3 arms, Stage 1 n=30-40/arm, total N=300-600, ORR_control=0.15, ORR_exp=0.25-0.45, OS HR=0.70-0.85, ρ ∈ {0.3, 0.5, 0.7}, interim at N=120. Save RNG seed + full parameters + full results for every run.

---

## 6. References

**Core Papers**

1. Stallard N, Todd S. Sequential designs for phase III clinical trials incorporating treatment selection. *Stat Med*. 2003;22(5):689-703.
2. Bauer P, Posch M. Letter to the Editor: Modification of the sample size and the schedule of interim analyses in survival trials based on data inspections. *Stat Med*. 2004;23(8):1333-1335. DOI: 10.1002/sim.1759.
3. Dunnett CW. A multiple comparison procedure for comparing several treatments with a control. *JASA*. 1955;50(272):1096-1121.
4. Magirr D, Jaki T, Whitehead J. A generalized Dunnett test for multi-arm multi-stage clinical studies with treatment selection. *Biometrika*. 2012;99(2):494-501. DOI: 10.1093/biomet/ass002.
5. Wu J, Li Y, Zhu L. Group sequential multi-arm multi-stage trial design with treatment selection. *Statistics in Medicine*. 2023;42(10):1480-1491. DOI: 10.1002/sim.9682.
6. Zhang EP, Jin M. A Multi-Arm Multi-Stage Group Sequential Phase 2/3 Design with Dose Selection for Oncology Trials. *Stat Biopharm Res*. 2025.

7. Wang X, Chen M, Chu S, Fan R, Chan ISF. A rank-based approach to improve the efficiency of inferential seamless phase 2/3 clinical trials with dose optimization. *Contemporary Clinical Trials*. 2023;132:107300. DOI: 10.1016/j.cct.2023.107300.

8. Hua K, Wang X, Luo X. Multiplicity control in clinical trials with adaptive selection followed by group-sequential testing. *Statistics in Biopharmaceutical Research*. 2026. DOI: 10.1080/19466315.2026.2634636.

**Further Reading**

9. Prasad V, Kim C, Burotto M, Vandross A. The strength of association between surrogate end points and survival in oncology: a systematic review of trial-level meta-analyses. *JAMA Internal Medicine*. 2015;175(8):1389-1398.
10. Jin M, Zhang P. An adaptive seamless phase 2-3 design with multiple endpoints. *Statistical Methods in Medical Research*. 2021;30(4):1143-1151. DOI: 10.1177/0962280220986935.
11. Jenkins M, Stone A, Jennison C. An adaptive seamless phase II/III design for oncology trials with subpopulation selection using correlated survival endpoints. *Pharmaceutical Statistics*. 2011;10(4):347-356. DOI: 10.1002/pst.472.
12. Bretz F, Schmidli H, König F, Racine A, Maurer W. Confirmatory seamless phase II/III clinical trials with hypotheses selection at interim: general concepts. *Biometrical Journal*. 2006;48(4):623-634. DOI: 10.1002/bimj.200510232.
13. Sun LZ, Li W, Chen C, Zhao J. Advanced utilization of intermediate endpoints for making optimized cost-effective decisions in seamless phase II/III oncology trials. *Statistics in Biopharmaceutical Research*. 2020;12(2):224-233. DOI: 10.1080/19466315.2019.1665578.
14. Dixit V, Mitra S, Simonsen KL. Multi-arm multi-stage clinical trials for time-to-event outcomes. *Journal of Biopharmaceutical Statistics*. 2021;31(6):838-851. DOI: 10.1080/10543406.2021.1979575.
15. Sydes MR, Parmar MKB, Mason MD, et al. Flexible trial design in practice — stopping arms for lack-of-benefit and adding research arms mid-trial in STAMPEDE: a multi-arm multi-stage randomized controlled trial. *Trials*. 2012;13:168. DOI: 10.1186/1745-6215-13-168.
16. Kelly PJ, Stallard N, Todd S. An adaptive group sequential design for phase II/III clinical trials that select a single treatment from several. *Journal of Biopharmaceutical Statistics*. 2005;15(4):641-658. DOI: 10.1081/BIP-200062857.
17. Friede T, Stallard N, Parsons N. Seamless phase II/III clinical trials using early outcomes for treatment or subgroup selection: methods and aspects of their implementation. *arXiv:1901.08365*. 2019. [R package `asd`]
18. Mehta CR, Tsiatis AA. Flexible sample size considerations using information-based interim monitoring. *Drug Information Journal*. 2001;35(4):1095-1112. DOI: 10.1177/009286150103500407.
19. Zhong W, Liu J, Wang C. Multiplicity control in oncology clinical trials with a binary surrogate endpoint-based drop-the-losers design. *Statistics in Medicine*. 2025;44:e70209. DOI: 10.1002/sim.70209.
20. Stallard N, Todd S. A group-sequential design for clinical trials with treatment selection. *Statistics in Medicine*. 2008;27(29):6209-6227. DOI: 10.1002/sim.3436.
21. Broglio K, Cooner F, Wu Y, et al. A systematic review of adaptive seamless clinical trials for late-phase oncology development. *Therapeutic Innovation & Regulatory Science*. 2024;58:917-929. DOI: 10.1007/s43441-024-00670-1.
