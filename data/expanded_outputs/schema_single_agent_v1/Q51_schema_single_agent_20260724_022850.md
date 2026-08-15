# 多智能体论文写作流水线中 Reviewer 与 Evidence Agent 的职责边界划分：一项学术智能综合

## 1. 检索与筛选概览

本综合基于提供的8篇摘要级证据记录，聚焦于多智能体系统中“评审者（Reviewer）”与“证据智能体（Evidence Agent）”的职责边界划分问题。检索范围涵盖2025—2026年的前沿研究（[1][4][5][6][7][8]）以及2016年、2023年的基础性工作（[2][3]）。所有证据均来自摘要层面，未涉及全文细节。筛选标准为：直接涉及多智能体系统中的证据检索、评审或验证功能划分的文献。最终纳入8篇记录，其中4篇明确描述了证据检索智能体的独立角色（[1][4][6][8]），2篇涉及评审或批判循环机制（[1][7]），2篇提供了多智能体系统在医学或决策支持领域的应用背景（[2][5]）。

## 2. 核心主题与证据

### 2.1 证据智能体的核心职责：检索与验证
在多智能体论文写作流水线中，证据智能体（Evidence Agent）的核心职责被明确界定为**证据的检索、筛选与初步验证**。例如，在面向事实核查的多智能体系统中，Evidence Retrieval Agent 专门负责“从可信来源检索可靠证据”[6]。类似地，在医学AI框架中，Evidence Retrieval agent 被设计为“查询PubMed以将回答锚定在近期文献中”[8]。ADMP-LS平台也强调了“证据锚定”能力，通过文献综述和问答实现证据基础的构建[4]。这些证据表明，证据智能体的首要任务是**确保输出内容的可追溯性和事实基础**。

### 2.2 评审者的核心职责：批判与质量控制
评审者（Reviewer）的职责则更侧重于**批判性评估与质量控制**。在对抗性多智能体系统（Adversarial Multi-Agent System）中，作者–评审者工作流被设计为包含“可验证证据与批判循环”[1]，这意味着评审者负责对证据智能体提供的证据进行质疑、验证和迭代改进。此外，在系统综述自动化研究中，评审者的角色被类比为人类评审员，负责“独立筛选研究、提取数据并评估纳入研究”[7]，其核心是**判断证据的适用性与质量**。

### 2.3 职责边界的模糊性与互补性
尽管职责有区分，但边界并非绝对清晰。证据智能体在检索后可能需要进行初步的“可信度判断”[6]，而评审者也可能需要“生成结构化解释”[8]来支持其批判。两者形成**互补循环**：证据智能体提供原始材料，评审者进行批判性评估，评估结果可能触发新一轮的证据检索[1][8]。这种循环机制在医学AI框架中体现为“可选的验证路径”，当不确定性高时触发人类评审[8]。

## 3. 证据支持的研究方向

### 3.1 明确职责分离的架构设计
现有证据支持将证据检索与评审批判设计为**独立的智能体模块**。例如，事实核查系统明确区分了“Query Generation Agent”、“Evidence Retrieval Agent”和“Verdict Prediction Agent”[6]；医学AI框架则区分了“Clinical Reasoning agent”、“Evidence Retrieval agent”和“Refinement agent”[8]。这种分离有助于专业化分工和可解释性提升。

### 3.2 引入批判循环与迭代验证
对抗性工作流[1]和可选的验证路径[8]表明，**迭代的批判循环**是划分职责边界的关键机制。评审者不应仅做一次性判断，而应能与证据智能体进行多轮交互，以提升证据的可靠性和一致性。

### 3.3 基于不确定性或风险的动态边界调整
医学AI框架中，当“高风险或高不确定性”时触发人类验证路径[8]，这提示职责边界可根据**任务风险等级**动态调整。在低风险场景下，证据智能体可承担更多验证职责；在高风险场景下，评审者（或人类）的介入应更深入。

## 4. 摘要级证据的局限

本综合完全基于摘要级证据，存在以下局限：
- **缺乏操作细节**：摘要未描述证据智能体与评审者之间的具体交互协议、数据格式或冲突解决机制。例如，[1]虽提及“批判循环”，但未说明循环的具体触发条件和终止标准。
- **领域偏差**：多数证据来自医学或事实核查领域（[5][6][8]），其在论文写作流水线中的适用性需进一步验证。社区更新等非医学场景（[3]）的摘要未提供相关职责划分信息。
- **时效性与验证不足**：部分文献为2025—2026年的预印本或会议论文（[4][6][8]），尚未经过同行评审的全文验证。系统综述协议（[7]）仅描述计划，未报告实际结果。
- **术语不一致**：不同系统对“评审者”的命名各异（如“Verdict Prediction Agent”[6]、“Refinement agent”[8]、“Critique Loop”[1]），可能掩盖职责的实质差异。

## 5. 谨慎结论

基于现有摘要级证据，在多智能体论文写作流水线中，Reviewer 与 Evidence Agent 的职责边界应遵循以下原则：
1. **功能分离**：Evidence Agent 负责证据的检索、筛选与初步锚定（[4][6][8]），Reviewer 负责批判性评估与质量控制（[1][7]）。
2. **迭代交互**：两者应通过批判循环（[1]）或验证路径（[8]）进行多轮交互，而非单向传递。
3. **动态调整**：职责边界可根据任务风险或不确定性水平动态调整，高风险场景下 Reviewer 的介入应更深入（[8]）。

然而，这些结论受限于摘要级证据的颗粒度与领域偏差。未来研究需基于全文证据，进一步明确交互协议、冲突解决机制以及跨领域泛化能力。当前证据尚不足以支持统一的、可操作化的职责边界规范。

## 参考文献
[1] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[2] A multi-agent system to support evidence based medicine and clinical decision making via data sharing and data privacy. Decision Support Systems. 2016.
[3] Decision Support for Regeneration Mode of Old Community Under Multi-Agent Interaction: Evidence from China. CrossRef. 2023.
[4] ADMP-LS: Agent-Based Dialogue and Mining Platform for Evidence-Grounded QA, Extraction, and Literature Review in Life Science. … Conference on Data …. 2025.
[5] Multi-Agent AI Systems in Healthcare: Systematic Evidence Synthesis Via PRISMA of Clinical Decision Support Systems, Robotic Interventions, and Critical Care. International Journal of Latest Technology in Engineering Management &amp; Applied Science. 2025.
[6] Towards Robust Fact-Checking: A Multi-Agent System with Advanced Evidence Retrieval. arXiv Preprint. 2025.
[7] Study protocol for evaluating automation of systematic review processes with EPPI-Reviewer and Copilot 365 in updating the cataract evidence gap map. Systematic Reviews. 2026.
[8] A Multi-Agent Framework for Medical AI: Leveraging Fine-Tuned GPT, LLaMA, and DeepSeek R1 for Evidence-Based and Bias-Aware Clinical Query Processing. arXiv Preprint. 2026.