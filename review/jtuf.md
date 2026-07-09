Official Review of Submission15729 by Reviewer jtUf
Official Reviewby Reviewer jtUf03 Jul 2026, 16:58 (modified: 09 Jul 2026, 07:02)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Reviewer jtUf, AuthorsRevisions
Paper Summary:
This paper introduces EvoClawBench, a benchmark for evaluating whether LLM agents can turn their own previous runs into reusable skills. The benchmark compares three settings: direct execution without skills, pre-execution skill writing, and post-run skill summarization followed by a fresh second execution.

The benchmark includes 100 tasks and 502 sub-problems across coding, data, office, security, operations, and domain-document workflows. The main result is that self-authored skills do not reliably improve performance; their effect depends heavily on the model, runtime scaffold, skill quality, and end-to-end cost.

Summary Of Strengths:
The paper targets a relevant and underexplored question in agent evaluation. It moves beyond asking whether skills are useful, and instead asks whether agents can create useful skills from their own runs.

The three-mode setup is well motivated. BASELINE, PRESKILL, and POSTSKILL provide a useful way to compare direct solving, pre-task skill writing, and post-run skill distillation.

The paper gives a useful diagnostic finding. It shows that self-authored skills can be helpful in some settings, but can also overfit to first-run context, depend strongly on the runtime scaffold, or add too much overhead.

Summary Of Weaknesses:
The evaluation does not fully isolate the effect of the generated skill itself. Skill-based runs also change the prompt mode, context, workspace, and execution procedure. This makes it difficult to know whether a score change comes from skill content, the skill-reuse wrapper, the workspace reset, or runtime-specific scaffold behavior.

POSTSKILL may partly measure task-specific repair rather than reusable skill learning. The first-run feedback and grading information can make the generated skill look more like a task patch than a general procedure. This issue becomes more concerning when combined with the zero-skill collapse above, because the experiment does not cleanly separate skill-content effects from workflow effects.

The experimental coverage is still limited. The main results use only two runtimes, one local setup, and one run per task and mode. Given the large runtime-specific differences and the severe collapses in some rows, repeated seeds or reruns would be important for judging whether these are stable phenomena or implementation/runtime artifacts.

Comments Suggestions And Typos:
The paper would benefit from reporting failed skill-authoring attempts, not only created-skill counts. If a model tries to create skills but produces no valid artifacts, that is a different failure mode from deciding not to create a skill.skills/<skill-name>/SKILL.md

The authors should report absolute score changes more prominently, since ratio-based gains can be unstable when baseline scores are very low or very high.

Confidence: 4 = Quite sure. I tried to check the important points carefully. It's unlikely, though conceivable, that I missed something that should affect my ratings.
Soundness: 3 = Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.
Excitement: 3.5
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
Publication Ethics Policy Compliance: I used a privacy-preserving tool exclusively for the use case(s) approved by PEC policy, such as language edits