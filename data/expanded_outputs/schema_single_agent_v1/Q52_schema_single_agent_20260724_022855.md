## 1. 检索与筛选概览

本合成基于提供的8篇文献证据集（E_q），聚焦于多智能体系统中“unsupported claim”（无证据支持的主张）的修复机制。经筛选，[1]、[2]、[3]、[6]、[7] 直接涉及证据约束下的主张验证与修复流程，[4]、[5]、[8] 虽涉及多智能体系统或证据基础，但未直接讨论 unsupported claim 的修复路径。核心分析围绕 [1]、[2]、[3] 展开，它们分别从 adversarial review、fact-checking 和 competitive intelligence 角度提供了机制设计。

## 2. 核心主题与证据

现有文献对 unsupported claim 的修复存在两种主要路径：**reviser 修复** 与 **回退至 evidence agent 重抽取**。

- **Reviser 修复路径**：[1] 提出的 adversarial multi-agent 系统中，author–reviewer 工作流通过 critique loops 实现主张的迭代修正。当 reviewer 发现 unsupported claim 时，系统设计倾向于由 reviser（即 author agent）基于 reviewer 的反馈直接修复主张，而非重新启动证据抽取流程。该机制强调“verifiable evidence and critique loops”，表明修复发生在合成阶段。
- **回退至 evidence agent 重抽取路径**：[2] 的 fact-checking 系统采用四智能体架构，其中 Evidence Retrieval Agent 负责 sourcing credible evidence。当 Verdict Prediction Agent 发现证据不足时，系统通过 Query Generation Agent 重新生成子查询，回退至证据检索阶段。这明确支持了“回退重抽取”的路径。[3] 的 AdversarialCI 框架同样强调“constraining agents to a verified evidence bank”，当 advocate agents 产生 unsupported claims 时，系统依赖证据库的重新检索与置信度评分来修正，而非由 agent 自行修复。

## 3. 证据支持的研究方向

基于现有证据，两种路径各有适用场景：

- **Reviser 修复** 更适合 **主张级微调**：当 unsupported claim 仅涉及局部表述不精确或引用缺失，且证据库已包含相关信息时，[1] 的 critique loop 可高效完成修复，避免重复检索成本。
- **回退至 evidence agent 重抽取** 更适合 **证据基础缺失或错误**：[2] 和 [3] 的证据表明，当 claim 完全缺乏证据支撑或证据来源不可靠时，必须回退至证据检索阶段。例如 [2] 强调“source credibility”和“transparency”，[3] 强调“verified evidence bank”和“mandatory source citation”，均指向证据层的根本性修正。

## 4. 摘要级证据的局限

本合成仅依赖摘要级证据，存在以下局限：
- **流程细节缺失**：[1] 的摘要未明确说明 reviser 修复的具体触发条件（如置信度阈值）；[2] 和 [3] 的摘要未区分“部分支持”与“完全无支持”的不同处理逻辑。
- **性能对比不足**：现有摘要未提供两种路径在准确率、延迟或成本上的定量对比。[2] 虽报告了 12.3% 的 Macro F1 提升，但未分解 unsupported claim 修复的贡献度。
- **领域泛化性不明**：[3] 在数据库选商领域达到 87.9% 准确率，但未说明该机制是否适用于其他科学文献综述场景。

## 5. 谨慎结论

基于现有摘要级证据，**unsupported claim 的修复路径应取决于错误类型**：
- 若为 **局部引用缺失或表述偏差**，可采用 [1] 的 reviser 修复机制，通过 critique loop 在合成阶段修正。
- 若为 **证据基础缺失、来源不可靠或主张完全无支撑**，则应采用 [2] 和 [3] 的回退至 evidence agent 重抽取路径，确保证据层的可信度。

当前证据不足以支持单一最优路径。建议未来研究在完整全文证据下，设计混合机制：先由 reviser 尝试修复，若修复失败（如置信度低于阈值）则回退至 evidence agent。该混合策略可兼顾效率与可靠性，但需进一步实验验证。

## 参考文献
[1] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[2] Towards Robust Fact-Checking: A Multi-Agent System with Advanced Evidence Retrieval. arXiv Preprint. 2025.
[3] AdversarialCI: A Buyer-Adaptive Multi-Agent Framework for Evidence-Grounded Competitive Intelligence. CrossRef. 2026.
[4] A multi-agent system to support evidence based medicine and clinical decision making via data sharing and data privacy. Decision Support Systems. 2016.
[5] Decision Support for Regeneration Mode of Old Community Under Multi-Agent Interaction: Evidence from China. CrossRef. 2023.
[6] FactReview: Evidence-Grounded Reviews with Literature Positioning and Execution-Based Claim Verification. arXiv preprint arXiv …. 2026.
[7] SciTrue: Evidence-Grounded Claim Verification in Science. Proceedings of the 19th Conference of …. 2026.
[8] ADMP-LS: Agent-Based Dialogue and Mining Platform for Evidence-Grounded QA, Extraction, and Literature Review in Life Science. … Conference on Data …. 2025.