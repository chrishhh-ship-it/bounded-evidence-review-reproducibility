# 多智能体论文写作流水线中 Reviewer 与 Evidence Agent 的职责边界划分：一项学术综合

## 1. 检索与筛选概览

本综合基于给定的限定证据集 E_q，共包含 8 篇文献，涵盖 2016 年至 2026 年间的多智能体系统研究。这些文献主要来自 CrossRef、arXiv、Decision Support Systems、Systematic Reviews 等学术数据库与预印本平台。筛选标准聚焦于多智能体系统中证据检索、评审与验证机制的设计，尤其是涉及 reviewer 与 evidence agent 角色分工的文献。经筛选，其中 4 篇文献（[1]、[4]、[6]、[8]）直接讨论了多智能体系统中的证据检索与评审流程，其余文献（[2]、[3]、[5]、[7]）提供了多智能体系统在医学决策、社区更新、系统综述等领域的应用背景，可作为职责边界划分的间接参考。

## 2. 核心主题与证据

### 2.1 Reviewer 与 Evidence Agent 的职责边界：现有框架中的分工模式

在多智能体论文写作流水线中，reviewer 与 evidence agent 的职责边界呈现明确的专业化分工趋势。文献 [1] 提出了一种对抗性多智能体系统用于系统文献综述，其中作者与评审者通过可验证证据与批评循环进行协作，暗示 reviewer 承担批判性评估与质量控制的角色，而证据的提供与验证则由专门的机制负责。文献 [6] 在事实核查系统中明确划分了四个专业化智能体：输入摄入代理负责声明分解，查询生成代理制定子查询，证据检索代理负责从可信来源获取证据，而裁决预测代理则综合判断并生成可解释的结论。这一架构中，evidence agent（证据检索代理）的职责是“检索可靠证据”，而 reviewer 的职责（由裁决预测代理体现）是“综合判断并生成可解释的结论”，两者在功能上分离但协作。

文献 [8] 的医疗多智能体框架进一步细化了分工：临床推理代理（Clinical Reasoning agent）生成结构化解释，证据检索代理（Evidence Retrieval agent）查询 PubMed 以将回答扎根于近期文献，精炼代理（Refinement agent）提升清晰度与事实一致性。在此框架中，evidence agent 专注于证据的检索与提供，而 reviewer 的功能由临床推理代理与精炼代理共同承担，负责推理、验证与质量提升。文献 [4] 提出的 ADMP-LS 平台则通过基于大纲的摘要与对话机制实现文献综述，其中证据检索与评审流程被整合为“证据基础问答与提取”功能，但未明确区分 reviewer 与 evidence agent 的独立职责。

### 2.2 职责边界的核心维度：证据检索 vs. 证据评估

综合上述文献，reviewer 与 evidence agent 的职责边界可归纳为两个核心维度：

**证据检索（Evidence Retrieval）**：由 evidence agent 负责，包括从外部数据库（如 PubMed、可信来源）获取相关文献、提取关键信息、确保来源的可信度与时效性。文献 [6] 强调 evidence agent 需“从可信来源检索可靠证据”，文献 [8] 则要求 evidence agent 查询 PubMed 以“将回答扎根于近期文献”。文献 [1] 中的“可验证证据”机制也暗示 evidence agent 需提供可追溯的证据来源。

**证据评估（Evidence Evaluation）**：由 reviewer 负责，包括对证据的质量、相关性、一致性进行批判性评估，生成综合判断，并确保输出的可解释性。文献 [6] 的裁决预测代理负责“综合判断并生成可解释的结论”，文献 [8] 的临床推理代理与精炼代理共同承担“推理、验证与质量提升”功能。文献 [1] 中的“批评循环”进一步强化了 reviewer 的批判性评估职责。

### 2.3 边界划分的潜在挑战

现有文献也揭示了职责边界划分的潜在挑战。文献 [5] 的系统综述指出，超过 60% 的多智能体医疗系统涉及“实用模型但缺乏临床验证”，且伦理问题（如自主性、数据隐私、透明度）有时被忽视。这表明 reviewer 的评估职责若未充分覆盖伦理与验证维度，可能导致系统输出的可靠性不足。文献 [7] 的研究方案则关注 AI 工具（如 EPPI-Reviewer 与 Copilot 365）在系统综述中的准确性与效率，指出“最佳阈值仍不明确”，暗示 reviewer 与 evidence agent 之间的协作阈值（如何时触发人工评审）需要进一步界定。

## 3. 证据支持的研究方向

基于现有证据，以下研究方向值得关注：

**职责边界的正式化建模**：现有文献（[1]、[6]、[8]）提供了分工的实践案例，但缺乏对 reviewer 与 evidence agent 职责边界的正式化定义。未来研究可借鉴文献 [6] 的四代理架构与文献 [8] 的三代理流水线，建立职责边界的形式化模型，明确各代理的输入、输出、触发条件与协作协议。

**证据质量评估的自动化标准**：文献 [5] 指出临床验证不足的问题，文献 [7] 则关注 AI 工具准确性的阈值。未来研究可探索 reviewer 代理如何自动化评估证据质量（如来源可信度、时效性、一致性），并设定可量化的评估标准，以降低对人工评审的依赖。

**伦理与偏见的边界管理**：文献 [8] 引入了基于 LIME/SHAP 的偏见检测机制，文献 [5] 强调伦理与法律问责的重要性。未来研究应探讨 reviewer 与 evidence agent 在伦理审查与偏见检测中的职责划分，例如 evidence agent 是否应主动标记潜在偏见，或 reviewer 是否应承担最终的伦理裁决。

**人机协作的边界触发机制**：文献 [8] 设置了“高风险或高不确定性情况下触发可选人工验证路径”的机制。未来研究可进一步探索 reviewer 与 evidence agent 在何种条件下应引入人工评审，以及如何通过不确定性估计（如文献 [8] 中的蒙特卡洛 dropout 与困惑度评分）自动触发边界切换。

## 4. 摘要级证据的局限

本综合完全基于摘要级证据，存在以下固有局限：

**信息粒度不足**：摘要通常仅提供研究的高层概述，缺乏对 reviewer 与 evidence agent 职责边界的详细描述。例如，文献 [1] 的摘要仅提及“可验证证据与批评循环”，但未说明证据如何被验证、批评循环的具体机制，以及 reviewer 与 evidence agent 之间的交互协议。文献 [4] 的摘要仅提及“文献综述与证据基础问答”，但未区分不同代理的职责。

**方法学细节缺失**：摘要无法提供实验设计、评估指标、参数设置等关键方法学信息。例如，文献 [6] 的摘要报告了 12.3% 的 Macro F1 提升，但未说明 reviewer 与 evidence agent 的协作如何影响这一性能。文献 [8] 的摘要报告了 87% 的准确率与 36.5 秒的延迟，但未分解各代理的贡献。

**潜在的选择性报告**：摘要可能倾向于报告正面结果而忽略局限性。文献 [5] 的摘要指出“超过 60% 的模型缺乏临床验证”，但未说明 reviewer 代理是否本应承担验证职责。文献 [7] 的研究方案虽提及“最佳阈值仍不明确”，但未提供具体数据。

**跨领域泛化性存疑**：现有证据主要来自医疗（[2]、[5]、[8]）、事实核查（[6]）与系统综述（[1]、[7]）领域，其职责边界划分模式是否适用于通用论文写作流水线尚需验证。文献 [3] 的社区更新案例提供了多智能体交互的另一种视角，但未涉及证据检索与评审。

## 5. 谨慎结论

基于现有摘要级证据，可得出以下谨慎结论：

在多智能体论文写作流水线中，reviewer 与 evidence agent 的职责边界应遵循“检索-评估”分离原则：evidence agent 专注于从外部数据库检索可信证据并确保来源可追溯，reviewer 则负责对证据进行批判性评估、综合判断与质量提升。现有框架（如 [1]、[6]、[8]）已初步实现这一分工，但职责边界的正式化定义、自动化评估标准、伦理与偏见管理机制，以及人机协作的触发条件仍需进一步研究。

然而，上述结论受限于摘要级证据的信息粒度不足与方法学细节缺失。未来研究应基于全文证据，深入分析 reviewer 与 evidence agent 的具体交互协议、性能贡献分解与跨领域泛化性，以建立更可靠的职责边界划分框架。

## 参考文献
[1] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[2] A multi-agent system to support evidence based medicine and clinical decision making via data sharing and data privacy. Decision Support Systems. 2016.
[3] Decision Support for Regeneration Mode of Old Community Under Multi-Agent Interaction: Evidence from China. CrossRef. 2023.
[4] ADMP-LS: Agent-Based Dialogue and Mining Platform for Evidence-Grounded QA, Extraction, and Literature Review in Life Science. … Conference on Data …. 2025.
[5] Multi-Agent AI Systems in Healthcare: Systematic Evidence Synthesis Via PRISMA of Clinical Decision Support Systems, Robotic Interventions, and Critical Care. International Journal of Latest Technology in Engineering Management &amp; Applied Science. 2025.
[6] Towards Robust Fact-Checking: A Multi-Agent System with Advanced Evidence Retrieval. arXiv Preprint. 2025.
[7] Study protocol for evaluating automation of systematic review processes with EPPI-Reviewer and Copilot 365 in updating the cataract evidence gap map. Systematic Reviews. 2026.
[8] A Multi-Agent Framework for Medical AI: Leveraging Fine-Tuned GPT, LLaMA, and DeepSeek R1 for Evidence-Based and Bias-Aware Clinical Query Processing. arXiv Preprint. 2026.