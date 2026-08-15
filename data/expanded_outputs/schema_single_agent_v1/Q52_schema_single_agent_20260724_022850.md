## 1. 检索与筛选概览

本合成基于提供的8篇文献证据集（E_q），旨在回应“当reviewer发现unsupported claim时，应由reviser修复还是回退到evidence agent重抽取”这一研究问题。经过筛选，其中4篇文献（[1]、[2]、[3]、[6]）的摘要级证据与多智能体系统中的证据验证、事实核查或claim修复流程直接相关，其余文献（[4]、[5]、[7]、[8]）虽涉及多智能体系统或证据基础，但未明确讨论unsupported claim的修复机制或回退策略。因此，本合成主要依据[1]、[2]、[3]、[6]展开分析。

## 2. 核心主题与证据

现有文献表明，多智能体系统在处理unsupported claim时，普遍采用“回退到证据检索”而非“由reviser直接修复”的策略。具体证据如下：

- [2]提出的FactAgent系统包含四个专门化智能体：输入摄取、查询生成、证据检索和判决预测。该系统通过“将复杂claim分解为子查询”并“从可信来源检索可靠证据”来确保claim的可验证性，其设计隐含了当证据不足时需回退至检索环节的逻辑[2]。
- [3]描述的AdversarialCI框架明确“通过将智能体约束到已验证的证据库并强制要求来源引用来解决LLM生成unsupported claim的倾向”[3]。该框架采用“多源证据摄取管道，配备自动验证和置信度评分”，并在对抗性法庭模拟中要求“倡导者仅依据已验证证据进行论证”[3]。这表明系统设计上倾向于通过证据管道的回退（而非reviser修复）来保证claim的准确性。
- [1]提出的对抗性多智能体系统包含作者-审稿人工作流，强调“可验证证据和批评循环”[1]。虽然摘要未明确说明修复机制，但其“批评循环”设计暗示当审稿人发现unsupported claim时，系统会触发新一轮的证据验证流程。
- [6]的FactReview系统结合“claim提取、文献定位和执行式claim验证”[6]，其“执行式验证”机制要求claim必须通过可执行的证据验证，这本质上要求unsupported claim回退到证据定位阶段。

## 3. 证据支持的研究方向

基于现有证据，可以识别出以下研究方向：

**方向一：回退至证据检索的标准化流程设计。** [2]和[3]均强调证据检索智能体在验证流程中的核心地位。未来研究可探索当reviewer发现unsupported claim时，如何设计标准化的回退协议，包括：回退触发条件（如置信度阈值）、回退后证据检索的优化策略（如子查询生成）、以及回退次数限制[2][3]。

**方向二：reviser的辅助修复角色。** 虽然现有系统倾向于回退策略，但[1]的“批评循环”和[6]的“执行式验证”暗示reviser可能承担辅助角色，例如：在回退前对unsupported claim进行初步分类（如“证据缺失”vs“证据矛盾”），或对回退后检索到的证据进行整合与表述优化[1][6]。

**方向三：混合策略的评估框架。** 现有文献缺乏对“纯回退”与“reviser修复”策略的对比评估。未来研究可构建评估指标（如修复准确率、系统延迟、token消耗），在标准化benchmark（如[2]使用的FEVEROUS、HOVER、SciFact）上比较两种策略的优劣[2][3]。

## 4. 摘要级证据的局限

本合成基于摘要级证据，存在以下局限：

- **机制细节缺失**：摘要未详细描述unsupported claim的具体处理流程。例如，[2]虽提及“claim分解”和“证据检索”，但未说明当检索结果仍不支持claim时系统的下一步操作[2]。[3]的“自动验证和置信度评分”机制的具体阈值和回退逻辑也未披露[3]。
- **缺乏对比实验**：现有文献未直接比较“reviser修复”与“回退重抽取”两种策略的效果。因此，本合成无法基于实证数据判断哪种策略更优。
- **领域覆盖有限**：证据集主要来自科学文献综述（[1]、[6]）和事实核查（[2]）领域，[3]虽涉及竞争情报但同样强调证据约束。这些领域的结论可能不直接适用于其他领域（如临床决策支持[4]或社区规划[5]）。

## 5. 谨慎结论

基于现有摘要级证据，可以得出以下谨慎结论：

1. **主流策略倾向于回退至evidence agent重抽取**：[2]和[3]的系统设计均强调通过证据检索管道和强制来源引用来防止unsupported claim，而非依赖reviser的修复能力。这表明在现有文献中，回退策略是更受青睐的解决方案。

2. **reviser修复的角色尚不明确**：虽然[1]和[6]暗示了reviser或类似智能体可能参与claim的修正，但摘要级证据未提供具体机制或效果评估。因此，无法确认reviser修复是否构成一个独立有效的策略。

3. **需要更细粒度的实证研究**：当前证据不足以支持“哪种策略更好”的结论。未来研究应在完整论文中披露unsupported claim的处理流程，并通过对比实验（如A/B测试）评估两种策略在准确性、效率和可解释性方面的差异。

综上，基于现有摘要级证据，当reviewer发现unsupported claim时，建议优先采用回退到evidence agent重抽取的策略，同时保留reviser在证据整合和表述优化方面的辅助角色。这一结论有待全文证据和实证研究的进一步验证。

## 参考文献
[1] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[2] Towards Robust Fact-Checking: A Multi-Agent System with Advanced Evidence Retrieval. arXiv Preprint. 2025.
[3] AdversarialCI: A Buyer-Adaptive Multi-Agent Framework for Evidence-Grounded Competitive Intelligence. CrossRef. 2026.
[4] A multi-agent system to support evidence based medicine and clinical decision making via data sharing and data privacy. Decision Support Systems. 2016.
[5] Decision Support for Regeneration Mode of Old Community Under Multi-Agent Interaction: Evidence from China. CrossRef. 2023.
[6] FactReview: Evidence-Grounded Reviews with Literature Positioning and Execution-Based Claim Verification. arXiv preprint arXiv …. 2026.
[7] SciTrue: Evidence-Grounded Claim Verification in Science. Proceedings of the 19th Conference of …. 2026.
[8] ADMP-LS: Agent-Based Dialogue and Mining Platform for Evidence-Grounded QA, Extraction, and Literature Review in Life Science. … Conference on Data …. 2025.