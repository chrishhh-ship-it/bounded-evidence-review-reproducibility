# ARL / single-agent error cases for human review

Source run: `data/reports/ipm_major_revision_20260721/repro/v3/title_match_single_vs_arl_20260730/full_20260730_034303`

ARL error cases: 11; single-agent error cases: 2

Labels: `gold_label` is the human reference; `single_label` is the single-agent output; `arl_final_label` is the final DeepSeek adjudication; `arl_critic_label` is the Kimi critic output.

## TM025 [arl_wrong]
- Gold: **match**
- Single agent: **match** (correct=True)
- ARL analyst: **match**
- Kimi critic: **nonmatch**
- ARL final: **nonmatch** (correct=False)
- Reference: Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
- Candidate: Multi-agent systems: A survey
- Analyst raw: {"label":"match","evidence":"Candidate title is identical to the title in the reference record.","risk":"none"}
- Critic raw: {
  "label": "nonmatch",
  "challenge": "The candidate title lacks the authors and publication year, which are essential for distinguishing it from other works with the same title.",
  "confidence": "high"
}
- Adjudicator raw: {"label":"nonmatch","reason":"The candidate lacks authors and publication year, so it is not uniquely identifiable as the 2018 IEEE Access article by Dorri et al."}

## TM026 [arl_wrong]
- Gold: **match**
- Single agent: **match** (correct=True)
- ARL analyst: **match**
- Kimi critic: **nonmatch**
- ARL final: **nonmatch** (correct=False)
- Reference: Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
- Candidate: Multi-agent systems: A survey
- Analyst raw: {"label":"match", "evidence":"Candidate title exactly matches the title in the reference record. The reference record includes authors, journal, and year, which uniquely identifies the publication.", "risk":"Title alone could be ambiguous, but reference record disambiguates."}
- Critic raw: {
  "label": "nonmatch",
  "challenge": "The candidate title lacks the authors, journal, and year information which are crucial for disambiguating between different publications with similar titles. Without this information, the match cannot be confirmed as the same publication.",
  "confidence": "high"
}
- Adjudicator raw: {"label":"nonmatch", "reason":"Candidate title matches the reference title but lacks author and year, making it insufficient to confirm the same bibliographic identity, as other works could share the same title."}

## TM038 [arl_wrong]
- Gold: **match**
- Single agent: **match** (correct=True)
- ARL analyst: **match**
- Kimi critic: **nonmatch**
- ARL final: **nonmatch** (correct=False)
- Reference: Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2017.
- Candidate: Multi-agent systems: A survey
- Analyst raw: {"label":"match", "evidence":"The candidate title 'Multi-agent systems: A survey' is exactly the same as the title in the reference record.", "risk":"None, exact match."}
- Critic raw: {
  "label": "nonmatch",
  "challenge": "The candidate title lacks the authors and publication year, which are crucial for distinguishing it from other works with the same title. Without this information, it's not possible to confirm that the candidate is the same publication as the reference.",
  "confidence": "high"
}
- Adjudicator raw: {"label":"nonmatch", "reason":"The candidate title is common and could refer to multiple works; without authors, year, or other identifiers, it cannot be confirmed as the same publication as the reference."}

## TM043 [arl_wrong]
- Gold: **match**
- Single agent: **match** (correct=True)
- ARL analyst: **match**
- Kimi critic: **nonmatch**
- ARL final: **nonmatch** (correct=False)
- Reference: Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
- Candidate: Multi-agent systems: A survey
- Analyst raw: {"label":"match", "evidence":"Titles are identical: 'Multi-agent systems: A survey'.", "risk":"None, exact match."}
- Critic raw: {
  "label": "nonmatch",
  "challenge": "The candidate title lacks author and publication year information, which are crucial for distinguishing between different publications with similar titles.",
  "confidence": "high"
}
- Adjudicator raw: {"label":"nonmatch", "reason":"The candidate title alone lacks author and publication year, making it impossible to confirm it refers to the same 2018 IEEE Access survey rather than another work with the same title."}

## TM057 [arl_wrong]
- Gold: **match**
- Single agent: **match** (correct=True)
- ARL analyst: **match**
- Kimi critic: **nonmatch**
- ARL final: **nonmatch** (correct=False)
- Reference: Multi-Agent AI Systems in Healthcare: Systematic Evidence Synthesis Via PRISMA of Clinical Decision Support Systems, Robotic Interventions, and Critical Care. International Journal of Latest Technology in Engineering Management & Applied Science. 2025.
- Candidate: Multi-Agent AI Systems in Healthcare: Systematic Evidence Synthesis Via PRISMA of Clinical Decision Support Systems, Robotic Interventions, and Critical Care
- Analyst raw: {"label":"match", "evidence":"Candidate title is identical to the title in the reference record.", "risk":"none"}
- Critic raw: {
  "label": "nonmatch",
  "challenge": "The candidate title is missing the journal name 'International Journal of Latest Technology in Engineering Management & Applied Science', which is a critical part of identifying the exact publication.",
  "confidence": "high"
}
- Adjudicator raw: {"label":"nonmatch", "reason":"The candidate title lacks the journal and year, making it impossible to confirm it refers to the same specific publication."}

## TM077 [both_wrong]
- Gold: **match**
- Single agent: **nonmatch** (correct=False)
- ARL analyst: **nonmatch**
- Kimi critic: **nonmatch**
- ARL final: **nonmatch** (correct=False)
- Reference: A survey on LLM-based multi-agent systems: workflow, infrastructure, and challenges. Vicinagearth. 2024.
- Candidate: Multi-agent systems: A survey
- Analyst raw: {"label":"nonmatch", "evidence":"The reference specifically surveys LLM-based multi-agent systems with workflow, infrastructure, and challenges, while the candidate is a generic survey on multi-agent systems without the LLM context.", "risk":"No ambiguity; the candidate omits the crucial LLM-based aspect and specific subtopics."}
- Critic raw: {
  "label": "nonmatch",
  "challenge": "The reference record specifies a survey on LLM-based multi-agent systems, including details on workflow, infrastructure, and challenges. The candidate title is a generic survey on multi-agent systems without any mention of LLM-based systems or the specific subtopics covered in the reference.",
  "confidence": "high"
}
- Adjudicator raw: {"label":"nonmatch", "reason":"The reference is a survey on LLM-based multi-agent systems with specific subtopics, while the candidate is a generic survey on multi-agent systems without LLM focus."}

## TM100 [arl_wrong]
- Gold: **match**
- Single agent: **match** (correct=True)
- ARL analyst: **match**
- Kimi critic: **nonmatch**
- ARL final: **nonmatch** (correct=False)
- Reference: Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
- Candidate: Multi-agent systems: A survey
- Analyst raw: {"label":"match", "evidence":"The candidate title is identical to the title in the reference record.", "risk":"Generic title could match other surveys, but with no conflicting details it directly corresponds to the provided reference."}
- Critic raw: {
  "label": "nonmatch",
  "challenge": "The candidate title lacks specific details such as authors and publication year, which are crucial for distinguishing it from other surveys on the same topic.",
  "confidence": "high"
}
- Adjudicator raw: {"label":"nonmatch", "reason":"The candidate title lacks authors and year, making it indistinguishable from other surveys with the same generic title, so it cannot be confirmed as the specific 2018 Dorri et al. publication."}

## TM117 [arl_wrong]
- Gold: **match**
- Single agent: **match** (correct=True)
- ARL analyst: **match**
- Kimi critic: **nonmatch**
- ARL final: **nonmatch** (correct=False)
- Reference: Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
- Candidate: Multi-agent systems: A survey
- Analyst raw: {"label":"match", "evidence":"The candidate title 'Multi-agent systems: A survey' matches the reference title exactly, including the same wording and structure.", "risk":"none"}
- Critic raw: {
  "label": "nonmatch",
  "challenge": "The candidate title lacks the authors' names and the publication year, which are crucial for distinguishing it from other works with the same title. Without this information, the match is not unambiguous.",
  "confidence": "high"
}
- Adjudicator raw: {"label":"nonmatch", "reason":"The bare title 'Multi-agent systems: A survey' is too generic to unambiguously identify the specific 2018 work by Dorri et al., as many publications may share the same title."}

## TM152 [arl_wrong]
- Gold: **match**
- Single agent: **match** (correct=True)
- ARL analyst: **match**
- Kimi critic: **nonmatch**
- ARL final: **nonmatch** (correct=False)
- Reference: Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
- Candidate: Multi-agent systems: A survey
- Analyst raw: {"label":"match", "evidence":"The candidate title is identical to the title in the reference record.", "risk":"None"}
- Critic raw: {
  "label": "nonmatch",
  "challenge": "The candidate title lacks the authors and publication year, which are essential for distinguishing it from other works with the same title.",
  "confidence": "high"
}
- Adjudicator raw: {"label":"nonmatch", "reason":"The candidate provides only the title, which is insufficient to distinguish the reference's specific 2018 survey by Dorri et al. in IEEE Access from potentially other works with the same title."}

## TM207 [arl_wrong]
- Gold: **match**
- Single agent: **match** (correct=True)
- ARL analyst: **match**
- Kimi critic: **nonmatch**
- ARL final: **nonmatch** (correct=False)
- Reference: Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
- Candidate: Multi-agent systems: A survey
- Analyst raw: {"label":"match", "evidence":"The candidate title exactly matches the title in the reference record.", "risk":"None"}
- Critic raw: {
  "label": "nonmatch",
  "challenge": "The candidate title lacks the authors and publication year, which are essential for distinguishing it from other works with the same title.",
  "confidence": "high"
}
- Adjudicator raw: {"label":"nonmatch", "reason":"The candidate provides only a title, which is generic and insufficient to confirm it is the same work as the reference without authors or publication year."}

## TM240 [both_wrong]
- Gold: **nonmatch**
- Single agent: **match** (correct=False)
- ARL analyst: **match**
- Kimi critic: **nonmatch**
- ARL final: **match** (correct=False)
- Reference: Automated MeSH Term Suggestion for Effective Query Formulation in Systematic Reviews Literature Search. arXiv Preprint. 2022.
- Candidate: MeSH Term Suggestion for Systematic Review Literature Search
- Analyst raw: {"label":"match", "evidence":"Core concepts identical: 'MeSH Term Suggestion' and 'Systematic Review(s) Literature Search' match the reference. Missing 'Automated' and 'Effective Query Formulation' are non-essential modifiers; singular vs. plural 'Review' is a minor variation.", "risk":"Low; candidate is a plausible shortened form of the reference title."}
- Critic raw: {
  "label": "nonmatch",
  "challenge": "The candidate title omits 'Automated' and 'Effective Query Formulation', which are essential to the reference's focus on an automated system for query formulation. The singular 'Review' in the candidate also deviates from the plural 'Reviews' in the reference, affecting the scope.",
  "confidence": "high"
}
- Adjudicator raw: {"label":"match", "reason":"The candidate title preserves the distinctive core topic 'MeSH Term Suggestion for Systematic Review Literature Search' and omits only non-essential modifiers ('Automated', 'Effective Query Formulation'), making it a plausible shortened form of the reference title."}

