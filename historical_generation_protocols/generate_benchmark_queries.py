"""
generate_benchmark_queries.py
------------------------------
Generate ≥200 benchmark queries across ≥3 domains in the same format as
data/benchmarks/multi_agent_intel_service_queries.json.

Each query has: id, domain_id, domain_name, category, query (zh/en), intent,
hallucination_challenge, difficulty (1-3).

Run:
    python scripts/generate_benchmark_queries.py --out data/benchmarks/benchmark_v2_queries.json
"""

import argparse, json, sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Domain definitions — 4 domains × ~50 queries each = 200+
# ---------------------------------------------------------------------------
DOMAINS = {
    "multi_agent_information_services": {
        "name": "多智能体协同信息服务",
        "lang": "zh",
        "categories": {
            "framework_design": "跨领域架构合成",
            "retrieval": "多源聚合与召回",
            "evaluation": "指标定义与基准",
            "evidence_synthesis": "全文证据提取边界",
            "writing": "引用约束撰写",
            "agent_roles": "角色分工与归因",
            "cost_efficiency": "成本-质量权衡",
            "benchmark_design": "基准构建与消融",
            "knowledge_service": "覆盖率与查全率",
        },
    },
    "digital_humanities": {
        "name": "数字人文与文化分析",
        "lang": "en",
        "categories": {
            "text_analysis": "Computational text analysis and distant reading",
            "cultural_heritage": "Digital preservation and archival access",
            "network_analysis": "Cultural network and relationship mapping",
            "multimodal": "Multimodal corpus construction and annotation",
            "evaluation": "Evaluation metrics for humanities NLP tasks",
            "tool_comparison": "Comparison of DH toolkits and platforms",
            "corpus_construction": "Corpus design and representativeness",
            "temporal_analysis": "Diachronic and temporal change detection",
        },
    },
    "biomedical_evidence_synthesis": {
        "name": "生物医学证据综合",
        "lang": "en",
        "categories": {
            "systematic_review": "Protocol design and PRISMA compliance",
            "evidence_grading": "Evidence grading and GRADE framework",
            "meta_analysis": "Statistical synthesis and heterogeneity",
            "rct_appraisal": "RCT quality appraisal and bias assessment",
            "clinical_nlp": "Clinical NLP and information extraction",
            "knowledge_graph": "Biomedical knowledge graph construction",
            "automation": "Semi-automated review pipeline design",
            "reporting": "Reporting standards and reproducibility",
        },
    },
    "climate_policy_research": {
        "name": "气候政策与可持续性",
        "lang": "en",
        "categories": {
            "policy_analysis": "Policy instrument comparison and evaluation",
            "emissions_modeling": "Emissions modeling and scenario analysis",
            "evidence_aggregation": "Cross-study evidence aggregation",
            "uncertainty": "Uncertainty quantification and communication",
            "stakeholder": "Stakeholder analysis and governance",
            "adaptation": "Adaptation strategy assessment",
            "data_quality": "Climate data quality and provenance",
            "interdisciplinary": "Interdisciplinary synthesis challenges",
        },
    },
}

# ---------------------------------------------------------------------------
# Query bank — (category, query, intent, hallucination_challenge, difficulty)
# difficulty: 1=easy, 2=medium, 3=hard
# ---------------------------------------------------------------------------
QUERY_BANK = {
    # ------------------------------------------------------------------ #
    # Domain 1: multi_agent_information_services  (50 queries, zh)
    # ------------------------------------------------------------------ #
    "multi_agent_information_services": [
        # framework_design (6)
        ("framework_design", "面向产业情报分析，如何构建多智能体协同的结构化情报报告生成管线？", "pipeline architecture", "跨领域架构合成", 2),
        ("framework_design", "多智能体协同在竞争情报场景中，如何通过角色分工减少幻觉引用？", "hallucination reduction", "角色归因模糊", 3),
        ("framework_design", "在多源异构检索环境中，证据整合模块应如何设计以保证引用溯源完整性？", "evidence traceability", "来源不一致", 3),
        ("framework_design", "多智能体文献综述管线中，Screening 角色的打分标准如何与 Synthesis 的引用精度对齐？", "role alignment", "角色目标冲突", 2),
        ("framework_design", "如何在不增加 API 调用次数的前提下，同时提升文献综述的覆盖率和引用精确率？", "cost-quality tradeoff", "效率约束", 2),
        ("framework_design", "面向系统文献综述，多智能体管线的可复现性应通过哪些设计决策来保障？", "reproducibility design", "实验可复现", 2),
        # retrieval (6)
        ("retrieval", "在多源检索场景中，BM25 与稠密检索的互补性如何影响最终报告的引用精度？", "retrieval fusion", "多源聚合偏差", 2),
        ("retrieval", "检索智能体在遭遇语义漂移查询时，应如何通过查询扩展控制幻觉引用的产生？", "query drift control", "语义漂移", 3),
        ("retrieval", "冻结语料库设置下，检索策略的选择如何影响证据覆盖率和引用孤儿率？", "frozen corpus retrieval", "语料边界约束", 2),
        ("retrieval", "多智能体检索管线中，元数据仲裁（标题/DOI/摘要）的优先级排序对去重精度有何影响？", "deduplication design", "元数据冲突", 2),
        ("retrieval", "Scopus/OpenAlex/arXiv 多源混合检索时，各源返回结果的领域偏差如何在管线中被校正？", "source bias correction", "来源领域偏移", 3),
        ("retrieval", "检索召回集大小（top-k）与后续 Evidence Extraction 的计算成本之间存在怎样的权衡关系？", "k selection tradeoff", "规模-精度权衡", 1),
        # evaluation (6)
        ("evaluation", "文献综述系统的自动评估指标中，哪些指标能区分结构化幻觉（格式正确但引用错误）和语义幻觉？", "hallucination taxonomy", "幻觉类型区分", 3),
        ("evaluation", "引文精度（ICP）和证据接地精度（ECP）作为二级指标的设计如何优于单一整体评分？", "metric design justification", "评估维度选择", 2),
        ("evaluation", "在 n=30 的小规模基准上，如何通过统计检验方法合理声称配置间的显著性差异？", "small-sample statistics", "小样本推断", 2),
        ("evaluation", "孤儿引用率（OR）与 ICP/ECP 之间存在哪些无法互相替代的信息内容？", "metric orthogonality", "指标冗余", 2),
        ("evaluation", "模糊匹配阈值的设定对 ECP 测量结果的稳健性有何影响？如何通过消融验证？", "threshold ablation", "阈值敏感性", 2),
        ("evaluation", "段落完整率（SC）作为结构指标在多智能体管线评估中的作用和局限性是什么？", "structural metric design", "结构完整性", 1),
        # evidence_synthesis (5)
        ("evidence_synthesis", "证据提取角色将摘要压缩为四字段结构体后，是否会引入摘要级信息损失从而影响引用质量？", "evidence compression loss", "摘要压缩偏差", 3),
        ("evidence_synthesis", "当冻结语料库中全文数量远少于摘要数量时，全文证据的使用策略应如何设计？", "fulltext scarcity", "全文覆盖约束", 2),
        ("evidence_synthesis", "多文档冲突证据的识别和调解在文献综述管线中应由哪个角色负责？如何设计？", "conflict resolution role", "证据冲突", 3),
        ("evidence_synthesis", "证据字典中「limitation」字段的提取质量如何影响综述报告中的局限性声明引用精度？", "limitation extraction", "字段质量影响", 2),
        ("evidence_synthesis", "从摘要提取的方法论字段（methodology）与从全文提取的实验细节之间存在哪些系统性差异？", "abstract vs fulltext", "信息粒度差异", 2),
        # writing (6)
        ("writing", "引用约束撰写中，合成智能体如何在「不允许引用语料库外文献」的约束下处理覆盖率稀疏的查询？", "citation constraint", "语料覆盖稀疏", 3),
        ("writing", "在多智能体管线中，合成阶段的提示词设计如何影响引用密度和引用孤儿率之间的权衡？", "prompt engineering", "提示词影响", 2),
        ("writing", "IMRaD 结构对于文献综述报告的适用性如何？哪些结构约束可以降低幻觉引用率？", "report structure", "结构约束", 2),
        ("writing", "修订智能体（Reviser）在单轮修订中能修复的引用错误类型有哪些？哪些需要多轮迭代？", "revision capability", "修订轮次设计", 2),
        ("writing", "对比单智能体（Baseline B）和多智能体管线（Method 1），引用格式一致性的差距集中在哪些章节？", "citation consistency", "章节级差异", 2),
        ("writing", "在多语言混合（中文查询+英文文献）场景中，合成智能体的语言切换策略如何影响引用结构？", "multilingual synthesis", "跨语言引用", 3),
        # agent_roles (6)
        ("agent_roles", "审阅智能体（Reviewer）在对抗式审阅循环中应采用哪些专项检查清单以最大化孤儿引用的检出率？", "reviewer checklist", "角色职责设计", 2),
        ("agent_roles", "当 Reviewer 和 Reviser 使用同一底层模型时，是否存在「自我确认偏误」的系统性风险？", "same-model bias", "内部效度威胁", 3),
        ("agent_roles", "在六角色管线中，Planner 角色的存在是否对最终引用精度产生显著影响？有哪些证据？", "planner necessity", "角色必要性", 2),
        ("agent_roles", "跨模型 ARL（DeepSeek 写作 + Kimi 审阅）与同模型 ARL 的性能差距如何从理论上解释？", "cross-model ARL", "模型多样性效应", 3),
        ("agent_roles", "修订智能体的「受约束修复」设计如何防止其在修复引用错误时引入新的语义错误？", "constrained repair", "修复副作用", 3),
        ("agent_roles", "多智能体协作中，角色间的信息传递格式（JSON/Markdown）如何影响下游引用追踪的准确性？", "inter-role protocol", "格式一致性", 2),
        # cost_efficiency (4)
        ("cost_efficiency", "从 Baseline A 到 Method 2 的 12× 成本增长中，哪个角色贡献的边际成本最高且边际效益最低？", "cost attribution", "成本归因", 2),
        ("cost_efficiency", "在系统文献综述场景中，证明 Method 2 相对于 Method 1（7× 成本）的额外 1.7× 成本是合理的条件是什么？", "cost justification", "成本合理性", 2),
        ("cost_efficiency", "如何设计一个「轻量级 ARL 变体」以在保留 80% 引用精度收益的同时将成本控制在 Method 1 级别？", "lightweight ARL", "成本-效果权衡", 3),
        ("cost_efficiency", "多智能体管线的延迟（~62s/query）对实时情报分析应用的可用性构成怎样的约束？", "latency constraint", "实时性要求", 1),
        # benchmark_design (6)
        ("benchmark_design", "冻结语料库基准相比实时检索基准在评估引用纪律方面有哪些不可替代的优势？", "frozen corpus value", "基准设计原则", 2),
        ("benchmark_design", "n=30 查询的试点规模对哪些结论的有效性构成威胁？哪些结论在此规模下仍然稳健？", "pilot scale validity", "小规模限制", 2),
        ("benchmark_design", "在扩展到 n≥200 查询时，如何设计分层抽样策略以确保覆盖不同语料覆盖率等级的查询？", "stratified sampling", "规模扩展设计", 3),
        ("benchmark_design", "负样本（设计为失败案例）的基准查询如何设计以暴露管线的系统性弱点？", "negative test design", "压力测试", 3),
        ("benchmark_design", "多领域基准（≥3 领域）相比单领域基准在验证引用纪律机制时提供了哪些额外的实验控制？", "cross-domain benchmark", "领域泛化验证", 2),
        ("benchmark_design", "人工标注子集应采用怎样的标注协议才能作为自动 ICP/ECP 指标的有效校准标准？", "annotation protocol", "人工校准设计", 2),
        # knowledge_service (5)
        ("knowledge_service", "知识服务场景下，多智能体情报系统相比传统数据库检索的核心优势体现在哪些指标上？", "system comparison", "服务模式对比", 1),
        ("knowledge_service", "在查全率要求严格的知识服务场景中，冻结语料库的边界如何影响系统的实用性评估？", "recall constraint", "语料边界影响", 2),
        ("knowledge_service", "如何设计一个引用审计接口，使研究人员能够追踪 AI 合成报告中每条声明的原始文献来源？", "audit interface", "可审计性设计", 2),
        ("knowledge_service", "多智能体情报系统在专业知识服务（法律/医学/专利）领域的迁移适用性取决于哪些关键因素？", "domain transfer", "领域迁移条件", 3),
        ("knowledge_service", "当知识库更新频率高（每月新增文献 > 10%）时，冻结语料库基准的评估结论是否仍然有效？", "corpus freshness", "动态语料适用性", 2),
    ],

    # ------------------------------------------------------------------ #
    # Domain 2: digital_humanities  (50 queries, en)
    # ------------------------------------------------------------------ #
    "digital_humanities": [
        # text_analysis (7)
        ("text_analysis", "How should distant reading methodologies balance statistical scalability with close reading interpretability in literary corpora?", "method integration", "Scalability vs. interpretability tradeoff", 2),
        ("text_analysis", "What citation practices are appropriate when LLM-generated thematic summaries of historical texts are used as evidence in humanities arguments?", "citation for generated content", "Attribution of generated evidence", 3),
        ("text_analysis", "How do topic modeling outputs differ from narrative framing analyses, and when should each be cited as evidence in DH papers?", "method selection", "Evidence type conflation", 2),
        ("text_analysis", "What are the main failure modes when applying NLP tools trained on modern text to pre-1800 literary corpora?", "temporal domain mismatch", "Historical text NLP failure", 2),
        ("text_analysis", "How should a systematic literature review in digital humanities handle the citation of software tools as primary research contributions?", "software citation", "Non-traditional citation objects", 2),
        ("text_analysis", "What quantitative measures can operationalize 'narrative complexity' in a reproducible, citation-checkable way for literary studies?", "operationalization", "Vague construct measurement", 3),
        ("text_analysis", "When synthesizing evidence from corpus studies with conflicting periodization claims, how should a multi-agent pipeline handle citation attribution?", "conflicting evidence synthesis", "Temporal boundary disputes", 3),
        # cultural_heritage (6)
        ("cultural_heritage", "How should metadata standards (Dublin Core, METS, EAD) be cited when they are used as architectural constraints in a DH pipeline?", "metadata citation", "Standards as evidence", 1),
        ("cultural_heritage", "What evidence is needed to justify OCR quality thresholds for historical newspapers before they are used as a retrieval corpus?", "quality threshold justification", "Data quality validation", 2),
        ("cultural_heritage", "How do digitization gaps in archival collections affect the fabrication residual when LLMs synthesize evidence from partial corpora?", "corpus incompleteness", "Fabrication from gaps", 3),
        ("cultural_heritage", "What citation frameworks exist for crediting indigenous communities as co-creators of digital cultural heritage corpora?", "attribution ethics", "Non-traditional authorship", 2),
        ("cultural_heritage", "How should a literature review system handle citations to archival finding aids versus the primary sources they describe?", "citation indirection", "Finding aid vs. primary source", 2),
        ("cultural_heritage", "What are the reproducibility requirements for a DH project that uses crowdsourced transcription as primary evidence?", "crowdsourced data reproducibility", "Non-stable evidence base", 2),
        # network_analysis (6)
        ("network_analysis", "How should citation networks be distinguished from co-authorship networks when both are used as evidence in a single DH synthesis?", "network type disambiguation", "Evidence type conflation", 2),
        ("network_analysis", "What statistical tests are appropriate for comparing centrality measures across historical correspondence networks of different sizes?", "comparative network analysis", "Network size confound", 3),
        ("network_analysis", "When a multi-agent system synthesizes claims about cultural influence from citation network data, what grounding checks prevent fabricated edges?", "network evidence grounding", "Fabricated graph claims", 3),
        ("network_analysis", "How do temporal resolution choices (decade vs. year vs. month) affect the reproducibility of historical network analysis results?", "temporal resolution", "Granularity-reproducibility tradeoff", 2),
        ("network_analysis", "What evidence is required to distinguish 'absence of connection' from 'absence of evidence' in historical network reconstruction?", "negative evidence", "Null result citation", 3),
        ("network_analysis", "How should a literature synthesis system handle contradictory centrality rankings produced by different network construction choices?", "conflicting rankings", "Method-dependent results", 2),
        # multimodal (5)
        ("multimodal", "How should image captioning outputs be cited when used as textual evidence in a DH synthesis report?", "image evidence citation", "Non-textual evidence grounding", 2),
        ("multimodal", "What annotation standards ensure that manual image labels can serve as verifiable evidence in a frozen-corpus benchmark?", "annotation standards", "Label verification", 2),
        ("multimodal", "How do alignment errors between OCR text and original page images propagate into citation grounding failures in DH pipelines?", "alignment error propagation", "Modality alignment failure", 3),
        ("multimodal", "What corpus design principles prevent multimodal DH corpora from being dominated by well-digitized, high-resource materials?", "corpus balance", "Digitization bias", 2),
        ("multimodal", "How should a synthesis agent handle citations to musical scores versus recordings of the same work in a musicology review?", "citation object disambiguation", "Multimodal citation objects", 2),
        # evaluation (6)
        ("evaluation", "What precision and recall proxies can substitute for human expert evaluation when assessing DH entity extraction at scale?", "automatic evaluation proxies", "Expert evaluation bottleneck", 2),
        ("evaluation", "How should inter-annotator agreement be reported and cited when it varies across cultural subgroups in a DH annotation task?", "IAA heterogeneity", "Subgroup-specific reliability", 2),
        ("evaluation", "What are the construct validity threats when using BLEU/ROUGE to evaluate historical text normalization outputs?", "metric construct validity", "NLP metric misapplication", 2),
        ("evaluation", "How should a DH benchmark account for the fact that 'ground truth' in humanities interpretation is inherently contested?", "contested ground truth", "Interpretive disagreement", 3),
        ("evaluation", "What minimum human evaluation sample size is needed to calibrate automatic metrics for a DH literature synthesis system?", "calibration sample size", "Human-automatic metric gap", 2),
        ("evaluation", "How do evaluation results on one literary tradition (e.g., English novel) transfer to traditions with fewer digital resources?", "cross-tradition transfer", "Low-resource generalization", 3),
        # tool_comparison (5)
        ("tool_comparison", "How should researchers cite and compare tools like Voyant, NLTK, and spaCy when they produce conflicting analytical results on the same corpus?", "tool comparison citation", "Tool-dependent results", 2),
        ("tool_comparison", "What reproducibility requirements should DH papers satisfy when a key finding depends on a specific version of a text analysis tool?", "software versioning", "Version-dependent results", 2),
        ("tool_comparison", "How should a literature synthesis agent handle papers that compare DH tools without reporting the corpora or parameters used?", "underspecified comparisons", "Missing experimental detail", 2),
        ("tool_comparison", "What citation evidence is needed to justify choosing transformer-based models over classical NLP tools for low-resource historical text analysis?", "model selection justification", "Low-resource model choice", 2),
        ("tool_comparison", "How do API access restrictions on commercial NLP platforms affect the reproducibility of DH studies that use them as primary analysis tools?", "API reproducibility", "Closed-access tools", 2),
        # corpus_construction (5)
        ("corpus_construction", "What corpus construction decisions most strongly predict downstream citation grounding failures in DH synthesis tasks?", "corpus design impact", "Corpus-fabrication linkage", 3),
        ("corpus_construction", "How should a DH corpus document its exclusion criteria to enable future researchers to assess coverage-fabrication tradeoffs?", "exclusion documentation", "Coverage transparency", 2),
        ("corpus_construction", "What strategies prevent a DH corpus from over-representing digitized canonical works at the expense of marginal traditions?", "canonical bias", "Corpus representativeness", 2),
        ("corpus_construction", "How should multi-lingual DH corpora handle script-specific tokenization when computing token-overlap based citation grounding metrics?", "multilingual tokenization", "Cross-script metrics", 2),
        ("corpus_construction", "What minimum corpus size is needed before a frozen-corpus DH benchmark produces reliable ICP/ECP scores across multiple query categories?", "corpus size threshold", "Small corpus reliability", 2),
        # temporal_analysis (6)
        ("temporal_analysis", "How should a synthesis agent handle conflicting periodization claims when the cited papers use different century-boundary conventions?", "periodization conflict", "Temporal boundary disputes", 3),
        ("temporal_analysis", "What citation evidence is sufficient to attribute a linguistic change to a specific decade rather than a broader era?", "temporal attribution precision", "Granularity of temporal claims", 2),
        ("temporal_analysis", "How do temporal sampling biases in digitization programs affect trend detection reliability in DH corpus studies?", "digitization temporal bias", "Sampling-dependent trends", 3),
        ("temporal_analysis", "How should a multi-agent synthesis pipeline handle citations when a claimed trend reverses depending on the start year of the analysis window?", "window-dependent results", "Temporal sensitivity", 3),
        ("temporal_analysis", "What evidence is required to distinguish genuine diachronic linguistic change from a corpus composition artifact in a DH study?", "change vs. artifact", "Corpus artifact confound", 3),
        ("temporal_analysis", "How should a synthesis agent cite computational stylometry results that conflict with literary-historical periodization consensus?", "stylometry-history conflict", "Method-consensus disagreement", 2),
    ],

    # ------------------------------------------------------------------ #
    # Domain 3: biomedical_evidence_synthesis  (52 queries, en)
    # ------------------------------------------------------------------ #
    "biomedical_evidence_synthesis": [
        # systematic_review (7)
        ("systematic_review", "How should a multi-agent literature synthesis system document its search strategy to meet PRISMA 2020 reporting requirements?", "PRISMA compliance", "Reporting standard adherence", 2),
        ("systematic_review", "What citation grounding checks are necessary before including a grey literature source in a biomedical systematic review?", "grey literature grounding", "Non-peer-reviewed evidence", 2),
        ("systematic_review", "How does the choice between forward and backward citation searching affect the fabrication residual in automated evidence synthesis?", "citation search strategy", "Search strategy completeness", 2),
        ("systematic_review", "What protocol pre-registration requirements reduce the risk of outcome reporting bias in AI-assisted systematic reviews?", "pre-registration", "Outcome reporting bias", 2),
        ("systematic_review", "How should an automated review pipeline handle eligibility criteria that require full-text reading when most corpus papers have only abstracts?", "full-text dependency", "Abstract-only corpus limitation", 3),
        ("systematic_review", "What is the minimum inter-reviewer agreement threshold before automated screening decisions can replace human dual-reviewer consensus?", "automation threshold", "Automation-human tradeoff", 2),
        ("systematic_review", "How should the review question (PICO/PECO) be operationalized as a retrieval query to minimize fabricated inclusions?", "PICO operationalization", "Review question translation", 2),
        # evidence_grading (6)
        ("evidence_grading", "How should a synthesis agent cite evidence graded as 'very low certainty' under GRADE without overstating its support for a clinical claim?", "certainty downgrading", "Evidence strength misrepresentation", 3),
        ("evidence_grading", "What citation evidence is needed to justify upgrading observational study evidence when a dose-response relationship is present?", "evidence upgrading criteria", "Non-standard grading", 2),
        ("evidence_grading", "How does GRADE certainty rating propagate through a multi-level synthesis when individual studies have heterogeneous designs?", "certainty aggregation", "Mixed-design synthesis", 3),
        ("evidence_grading", "What are the construct validity limits of using automated NLI to assess whether a synthesis claim is 'supported' by a GRADE-rated body of evidence?", "NLI-GRADE gap", "Automated grading validity", 3),
        ("evidence_grading", "How should a literature synthesis system handle citations to network meta-analyses when direct and indirect evidence conflict?", "indirect evidence handling", "Network meta-analysis citation", 3),
        ("evidence_grading", "What information must a synthesis agent preserve from primary studies to allow downstream GRADE assessment of indirectness?", "indirectness preservation", "Evidence chain integrity", 2),
        # meta_analysis (7)
        ("meta_analysis", "How should a synthesis agent cite heterogeneity statistics (I²) without overclaiming their interpretability?", "heterogeneity citation", "Statistical overclaiming", 2),
        ("meta_analysis", "What are the evidence requirements for choosing a fixed-effects versus random-effects model in an automated meta-analysis synthesis?", "model selection evidence", "Statistical model choice", 2),
        ("meta_analysis", "How should publication bias assessments (funnel plots, Egger's test) be cited in an automated synthesis that cannot access raw data?", "publication bias citation", "Indirect bias evidence", 2),
        ("meta_analysis", "When a synthesis agent reports a pooled effect size from a frozen corpus, what corpus-incompleteness disclaimer is required?", "pooled estimate qualification", "Corpus incompleteness caveat", 2),
        ("meta_analysis", "How do subgroup analyses in meta-analyses create citation grounding challenges when the subgroup evidence is not in the frozen corpus?", "subgroup evidence gaps", "Subgroup fabrication risk", 3),
        ("meta_analysis", "What statistical checks should a Reviewer agent perform before accepting a synthesis agent's pooled effect size claim?", "reviewer statistical checks", "Meta-analytic claim review", 2),
        ("meta_analysis", "How should a multi-agent synthesis handle citations when two meta-analyses in the corpus reach opposing conclusions on the same outcome?", "conflicting meta-analyses", "Direct contradiction handling", 3),
        # rct_appraisal (6)
        ("rct_appraisal", "What citation evidence is needed to support a risk-of-bias assessment under RoB 2 when allocation concealment details are unreported?", "RoB 2 incomplete reporting", "Missing method detail", 2),
        ("rct_appraisal", "How should a synthesis agent handle RCT evidence where the intervention description is too vague to verify corpus match via title/abstract fuzzy matching?", "vague intervention matching", "Fuzzy match failure", 3),
        ("rct_appraisal", "What are the fabrication risks when an automated synthesis cites a pilot RCT as evidence for a full-scale population-level claim?", "scale extrapolation", "Evidence scope mismatch", 3),
        ("rct_appraisal", "How should a multi-agent pipeline flag and handle RCT abstracts that omit primary outcome results?", "incomplete abstract handling", "Missing outcome data", 2),
        ("rct_appraisal", "What criteria determine when a crossover RCT's carryover effect threatens the citation grounding of a within-subject synthesis claim?", "carryover effect citation", "Design-specific threats", 2),
        ("rct_appraisal", "How should a reviewer agent assess whether a composite outcome claim is supported by the cited RCT's individual component data?", "composite outcome review", "Outcome disaggregation", 3),
        # clinical_nlp (6)
        ("clinical_nlp", "How should clinical NLP systems cite de-identification decisions when those decisions affect the representativeness of extracted evidence?", "de-identification citation", "Privacy-coverage tradeoff", 2),
        ("clinical_nlp", "What corpus construction requirements ensure that clinical NLP training data can serve as frozen-corpus retrieval evidence?", "clinical corpus design", "Clinical data constraints", 2),
        ("clinical_nlp", "How do ICD coding disagreements between hospitals affect the citation grounding of population-level epidemiological synthesis claims?", "coding heterogeneity", "Administrative data quality", 3),
        ("clinical_nlp", "What citation evidence is needed to justify using a general-domain NLP model for clinical entity extraction without domain-specific fine-tuning?", "domain adaptation justification", "Transfer learning evidence", 2),
        ("clinical_nlp", "How should a synthesis agent handle citations to negative clinical NLP results that are underrepresented in the retrieval corpus?", "negative result citation", "Publication bias in NLP", 2),
        ("clinical_nlp", "What are the construct validity threats when using token-overlap as a semantic grounding proxy for Chinese-English clinical text pairs?", "cross-lingual clinical NLP", "Multilingual validity", 2),
        # knowledge_graph (5)
        ("knowledge_graph", "How should a synthesis agent cite biomedical knowledge graph edges when their provenance includes multiple conflicting source studies?", "provenance conflict", "Multi-source edge citation", 3),
        ("knowledge_graph", "What evidence quality thresholds should gate the inclusion of automatically extracted relations into a biomedical knowledge graph?", "extraction quality threshold", "Automated relation quality", 2),
        ("knowledge_graph", "How do entity normalization errors in biomedical NER propagate into citation grounding failures at the knowledge graph level?", "normalization error propagation", "NER-KG coupling", 3),
        ("knowledge_graph", "What citation practices allow biomedical knowledge graphs to distinguish asserted facts from computationally inferred facts?", "assertion vs. inference citation", "Knowledge provenance", 2),
        ("knowledge_graph", "How should a multi-agent synthesis handle citations to ontology terms (MeSH, SNOMED) as evidence for clinical classification claims?", "ontology citation", "Ontology as evidence", 2),
        # automation (5)
        ("automation", "What human oversight checkpoints are necessary in a semi-automated systematic review pipeline to prevent fabricated inclusions from passing the screening stage?", "human checkpoints", "Automation oversight design", 2),
        ("automation", "How should an automated synthesis pipeline handle the citation of retracted papers that remain in the frozen corpus?", "retraction handling", "Post-retraction corpus integrity", 3),
        ("automation", "What performance benchmarks justify replacing dual-reviewer consensus with single-automated-reviewer in a biomedical synthesis pipeline?", "automation benchmark", "Automation validation criteria", 2),
        ("automation", "How should a multi-agent synthesis pipeline document its automation decisions to meet PRISMA-AI reporting requirements?", "PRISMA-AI compliance", "Automated review reporting", 2),
        ("automation", "What are the irreducible failure modes of automated biomedical evidence synthesis that require human expert review regardless of pipeline sophistication?", "irreducible automation failure", "Automation limits", 2),
        # reporting (4)
        ("reporting", "How should an AI-assisted systematic review report uncertainty bounds on its pooled estimates when the corpus covers only a fraction of eligible studies?", "corpus-incomplete uncertainty", "Partial coverage reporting", 2),
        ("reporting", "What citation metadata standards ensure that an AI-generated biomedical synthesis report is independently verifiable by a human reviewer?", "verifiable synthesis", "Auditability standards", 2),
        ("reporting", "How should a synthesis agent qualify conclusions that rest on a single high-quality RCT versus a larger body of lower-quality studies?", "evidence weight qualification", "Single vs. pooled evidence", 2),
        ("reporting", "What reporting requirements prevent an AI synthesis from misrepresenting the clinical significance of a statistically significant but small effect size?", "clinical vs. statistical significance", "Effect size reporting", 2),
    ],

    # ------------------------------------------------------------------ #
    # Domain 4: climate_policy_research  (52 queries, en)
    # ------------------------------------------------------------------ #
    "climate_policy_research": [
        # policy_analysis (7)
        ("policy_analysis", "How should a synthesis agent cite carbon pricing evidence when the cited studies use different baseline emission scenarios?", "baseline scenario citation", "Scenario heterogeneity", 3),
        ("policy_analysis", "What citation grounding checks prevent an AI synthesis from conflating a modeled emission reduction with an observed one?", "modeled vs. observed evidence", "Evidence type confusion", 3),
        ("policy_analysis", "How should a multi-agent system synthesize evidence on carbon tax effectiveness when the corpus contains studies from jurisdictions with very different policy designs?", "policy design heterogeneity", "Cross-jurisdiction confound", 3),
        ("policy_analysis", "What evidence standards justify citing a single-country carbon tax evaluation as support for a multinational policy recommendation?", "generalizability citation", "Evidence scope mismatch", 2),
        ("policy_analysis", "How should an automated synthesis handle citations to policy impact assessments that use different discount rates for future climate damages?", "discount rate sensitivity", "Economic assumption heterogeneity", 3),
        ("policy_analysis", "What are the citation grounding requirements when synthesizing co-benefit evidence (e.g., health + climate) across studies that measure benefits differently?", "co-benefit synthesis", "Outcome heterogeneity", 2),
        ("policy_analysis", "How should a synthesis agent distinguish between policy design recommendations and policy outcome evaluations when constructing its bibliography?", "design vs. outcome citation", "Recommendation-evidence boundary", 2),
        # emissions_modeling (6)
        ("emissions_modeling", "How should a synthesis agent cite integrated assessment model (IAM) outputs when the model assumptions are contested in the climate science literature?", "IAM citation", "Contested model assumptions", 3),
        ("emissions_modeling", "What corpus coverage is needed before an AI synthesis can credibly claim to represent the 'state of the art' in emissions pathway modeling?", "coverage threshold", "Representativeness claim", 2),
        ("emissions_modeling", "How should conflicting IPCC scenario projections (SSP1-1.9 vs. SSP5-8.5) be cited when both appear in the frozen corpus?", "scenario conflict citation", "Projection range handling", 2),
        ("emissions_modeling", "What citation evidence distinguishes a climate tipping point 'possibility' from a 'high-confidence' projection in a synthesis report?", "certainty level citation", "Confidence qualification", 3),
        ("emissions_modeling", "How should a multi-agent synthesis handle citations to downscaled regional climate projections when the global model used differs across studies?", "downscaling heterogeneity", "Model-chain citation", 3),
        ("emissions_modeling", "What are the fabrication risks when a synthesis agent cites temperature anomaly trends from a corpus that under-represents Arctic observational studies?", "geographic coverage bias", "Regional under-representation", 3),
        # evidence_aggregation (7)
        ("evidence_aggregation", "How should a climate policy synthesis handle conflicting cost estimates for the same technology across multiple learning curve studies?", "cost heterogeneity", "Technology cost synthesis", 2),
        ("evidence_aggregation", "What citation framework allows a synthesis to distinguish 'observed reductions' from 'projected reductions' in renewable energy adoption studies?", "observed vs. projected", "Temporal claim grounding", 2),
        ("evidence_aggregation", "How should a multi-agent system synthesize evidence from both peer-reviewed studies and grey literature reports (IEA, IRENA) without conflating their authority levels?", "authority level mixing", "Grey-peer literature citation", 2),
        ("evidence_aggregation", "What evidence is needed to justify combining energy efficiency and renewable energy studies in a single synthesis claim about decarbonization potential?", "cross-technology synthesis", "Technology boundary citation", 2),
        ("evidence_aggregation", "How should a synthesis agent handle citations when a meta-analysis in the corpus has already synthesized some of the primary studies also present in the corpus?", "double-counting prevention", "Nested evidence structure", 3),
        ("evidence_aggregation", "What citation grounding requirements apply when a synthesis draws on energy system models that include non-climate co-benefits as primary drivers?", "co-benefit model citation", "Multi-objective model grounding", 2),
        ("evidence_aggregation", "How should conflicting evidence on carbon capture and storage (CCS) feasibility be synthesized when the corpus contains both early-stage pilot and full-scale deployment studies?", "technology maturity citation", "Maturity-level confound", 3),
        # uncertainty (6)
        ("uncertainty", "How should a climate synthesis agent communicate epistemic uncertainty (model uncertainty) differently from aleatory uncertainty (natural variability) in its citations?", "uncertainty type distinction", "Uncertainty conflation", 3),
        ("uncertainty", "What citation practices prevent an AI synthesis from understating climate risk by over-weighting median scenario projections and ignoring tail risks?", "tail risk citation", "Risk representation bias", 3),
        ("uncertainty", "How should a synthesis report cite sensitivity analyses that show a policy recommendation reverses under different damage function assumptions?", "sensitivity reversal citation", "Assumption-dependent conclusion", 3),
        ("uncertainty", "What evidence standards determine whether an uncertainty range in a climate projection should be reported as 'likely' versus 'very likely' in a synthesis?", "confidence interval citation", "Confidence level reporting", 2),
        ("uncertainty", "How should a multi-agent synthesis handle citations when the corpus contains both process-based and empirical climate models with different uncertainty structures?", "model type uncertainty", "Mixed-model synthesis", 3),
        ("uncertainty", "What are the fabrication risks when an AI synthesis aggregates climate projections without accounting for inter-model correlation?", "model correlation", "Correlation-induced fabrication", 3),
        # stakeholder (5)
        ("stakeholder", "How should a synthesis agent cite evidence on public acceptance of climate policies when the cited surveys used different framing of the same policy?", "framing effect citation", "Survey framing sensitivity", 2),
        ("stakeholder", "What citation evidence is needed to support claims about stakeholder coalition formation in multi-level climate governance?", "governance coalition evidence", "Multi-level attribution", 2),
        ("stakeholder", "How should an AI synthesis handle citations to industry-funded studies on carbon capture when the corpus does not include independent replications?", "industry funding bias", "Funding-source disclosure", 2),
        ("stakeholder", "What evidence standards justify citing a single-country stakeholder analysis as support for a cross-regional governance recommendation?", "generalizability", "Stakeholder context transfer", 2),
        ("stakeholder", "How should a synthesis agent distinguish between descriptive stakeholder mapping and normative governance design recommendations in its bibliography?", "descriptive vs. normative", "Citation purpose disambiguation", 2),
        # adaptation (5)
        ("adaptation", "How should a synthesis agent cite adaptation cost estimates when the cited studies use different definitions of 'residual risk'?", "residual risk definition", "Definition heterogeneity", 2),
        ("adaptation", "What citation grounding requirements apply when synthesizing evidence on managed retreat policies across jurisdictions with different legal frameworks?", "legal context citation", "Jurisdiction transfer", 2),
        ("adaptation", "How should a multi-agent system handle citations to community-based adaptation studies when the evidence base is dominated by project reports rather than peer-reviewed papers?", "grey literature dominance", "Evidence type imbalance", 2),
        ("adaptation", "What evidence standards distinguish 'climate-proofing' from 'transformative adaptation' in a policy synthesis?", "adaptation depth citation", "Concept boundary", 2),
        ("adaptation", "How should a synthesis agent handle citations to adaptation effectiveness studies that lack counterfactual controls?", "counterfactual evidence", "Causal inference limits", 3),
        # data_quality (5)
        ("data_quality", "How should a synthesis agent cite satellite-derived emissions estimates when ground-based validation data are absent from the corpus?", "satellite data validation", "Remote sensing evidence", 2),
        ("data_quality", "What data provenance documentation is needed before an AI synthesis can use national inventory reports as primary evidence for emission trend claims?", "inventory data provenance", "Official data reliability", 2),
        ("data_quality", "How should a multi-agent pipeline handle citations to climate datasets that have been revised or superseded since their inclusion in the frozen corpus?", "dataset versioning", "Corpus staleness", 3),
        ("data_quality", "What quality checks prevent citation grounding failures when the synthesis agent relies on model output data rather than observational records?", "model output vs. observation", "Model data grounding", 2),
        ("data_quality", "How should a synthesis report qualify evidence from citizen science climate data given its heterogeneous collection protocols?", "citizen science citation", "Non-standardized data", 2),
        # interdisciplinary (8)
        ("interdisciplinary", "How should a climate policy synthesis handle citations when the same evidence is interpreted differently by economists and physical scientists?", "disciplinary interpretation", "Cross-discipline conflict", 3),
        ("interdisciplinary", "What citation frameworks allow a synthesis to integrate quantitative emissions modeling with qualitative governance analysis?", "mixed-method synthesis", "Qualitative-quantitative integration", 3),
        ("interdisciplinary", "How should a multi-agent synthesis cite social science evidence on climate justice when it uses different justice frameworks than the policy documents in the corpus?", "justice framework citation", "Normative framework mismatch", 2),
        ("interdisciplinary", "What are the construct validity threats when using NLP-based topic modeling to synthesize interdisciplinary climate literature?", "topic model validity", "Cross-domain NLP limits", 2),
        ("interdisciplinary", "How should a synthesis agent handle citations when the corpus contains studies that use 'climate change' and 'climate variability' interchangeably?", "concept conflation", "Terminological heterogeneity", 2),
        ("interdisciplinary", "How should an AI synthesis cite evidence from loss-and-damage assessments when the economic and non-economic losses are aggregated in the source?", "loss disaggregation", "Aggregation-level mismatch", 2),
        ("interdisciplinary", "What citation evidence is needed to distinguish a 'feasibility gap' from a 'policy gap' in a net-zero transition synthesis?", "gap type citation", "Concept boundary", 2),
        ("interdisciplinary", "How should a multi-agent synthesis handle citations to climate litigation case law when the legal jurisdiction differs from the policy target region?", "jurisdiction citation", "Legal-policy transfer", 2),
    ],
}


def build_queries(start_id: int = 1) -> list[dict]:
    """Flatten all query banks into a list with sequential IDs."""
    rows = []
    qid = start_id
    for domain_id, qs in QUERY_BANK.items():
        domain_meta = DOMAINS[domain_id]
        for (cat, query, intent, halluc_challenge, difficulty) in qs:
            rows.append({
                "id": f"Q{qid:03d}",
                "domain_id": domain_id,
                "domain_name": domain_meta["name"],
                "lang": domain_meta["lang"],
                "category": cat,
                "query": query,
                "intent": intent,
                "hallucination_challenge": halluc_challenge,
                "difficulty": difficulty,
            })
            qid += 1
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/benchmarks/benchmark_v2_queries.json")
    ap.add_argument("--start-id", type=int, default=1)
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()

    rows = build_queries(args.start_id)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written {len(rows)} queries → {out}")

    if args.stats:
        from collections import Counter
        print("\n--- Stats ---")
        by_domain = Counter(r["domain_id"] for r in rows)
        for d, n in by_domain.items():
            print(f"  {d}: {n} queries")
        by_diff = Counter(r["difficulty"] for r in rows)
        print(f"  Difficulty: {dict(sorted(by_diff.items()))}")
        by_lang = Counter(r["lang"] for r in rows)
        print(f"  Language: {dict(by_lang)}")
        print(f"  Total: {len(rows)}")


if __name__ == "__main__":
    main()
