Official Review of Submission15729 by Reviewer CzYN
Official Reviewby Reviewer CzYN02 Jul 2026, 13:26 (modified: 09 Jul 2026, 07:02)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Reviewer CzYN, AuthorsRevisions
Paper Summary:
This paper introduces EvoClawBench, a benchmark designed to evaluate whether LLM agents can distill reusable procedural skills from their own prior execution evidence. Experiments across three modes (baseline, pre-skill, and post-skill) reveal that this closed-loop skill learning is highly selective and non-monotonic.

Summary Of Strengths:
The paper addresses an important yet under-explored question in the agent evaluation landscape.

The experimental results reveal a non-monotonic, highly selective pattern of skill-learning success across models and runtimes, offering counterintuitive insights that effectively challenge the prevailing assumption that self-authored skills are uniformly beneficial to agent performance.

Summary Of Weaknesses:
The benchmark relies on a single execution run per configuration without reporting confidence intervals or significance tests. Given the well-known stochasticity and non-determinism of LLM agent behaviors, this single-run protocol fails to account for run-to-run variance, severely undermining the statistical reliability of the reported performance differences and rankings.

The benchmark contains only 100 tasks in total, and critically, the hybrid-graded subset comprises a mere 12 tasks. This small sample size raises concerns about the generalizability of the paper's most impactful quantitative claims.

Table 2 presents the results without any formatting emphasis such as boldface or highlighting, which prevents readers from immediately identifying the most significant performance differences at first glance.

The main text frequently adopts code-style phrasing and inline code formatting (e.g., in Section 3.4) that are more fitting for Appendix than for the narrative exposition of a scholarly paper.

Why is there such a huge performance gap between OpenClaw and nanobot? Can the authors provide a detailed case-by-case analysis of typical tasks to rule out issues in task design and metric definition?

Comments Suggestions And Typos:
The submitted PDF exhibits pervasive formatting defects, most notably line numbers frequently overlapping with the body text in multiple places.

Figure 1 and Figure 2, which are central to understanding the benchmark pipeline and task-suite composition, are rendered with poor resolution and visually overcrowded labeling, making key details barely legible.

Why is the Appendix formatted in a single column?

Confidence: 4 = Quite sure. I tried to check the important points carefully. It's unlikely, though conceivable, that I missed something that should affect my ratings.
Soundness: 3 = Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.
Excitement: 3 = Interesting: I might mention some points of this paper to others and/or attend its presentation in a conference if there's time.
Overall Assessment: 3 = Findings: I think this paper could be accepted to the Findings of the ACL.
Ethical Concerns:
There are no concerns with this submission

Needs Ethics Review: No
Reproducibility: 4 = They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.
Datasets: 4 = Useful: I would recommend the new datasets to other researchers or developers for their ongoing work.
Software: 4 = Useful: I would recommend the new software to other researchers or developers for their ongoing work.
Knowledge Of Or Educated Guess At Author Identity: No
Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
Knowledge Of Paper Source: N/A, I do not know anything about the paper from outside sources
Impact Of Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
Reviewer Certification: I certify that the review I entered accurately reflects my assessment of the work. If you used any type of automated tool to help you craft your review, I hereby certify that its use was restricted to improving grammar and style, and the substance of the review is either my own work or the work of an acknowledged secondary reviewer.
Publication Ethics Policy Compliance: I did not use any generative AI tools for this review