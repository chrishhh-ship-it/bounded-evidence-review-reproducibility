# 摘要证据与全文证据冲突时，reviewer agent 的冲突处理与风险提示策略

## 1. 检索与筛选概览

本合成基于给定的8条摘要级证据记录，聚焦于多智能体系统中reviewer agent在摘要证据与全文证据冲突时的处理策略。检索到的证据涵盖多智能体文献综述系统[1]、空间文本到SQL的多智能体框架[7]、系统综述自动化框架[8]以及若干同行评审意见[2][3][4][5][6]。所有证据均为摘要级别，未提供全文内容，因此本合成严格限定于摘要证据所呈现的信息范畴。

## 2. 核心主题与证据

现有摘要证据表明，多智能体系统中的reviewer agent承担着关键的验证与纠错功能。在“Adversarial Multi-Agent System for Systematic Literature Reviews”中，系统设计了作者-评审者工作流，包含可验证证据与批评循环[1]。类似地，“From Questions to Queries”框架在SQL生成后引入基于执行的审查阶段，实验显示经过reviewer纠正后准确率从76.7%提升至87.7%[7]。“LatteReview”框架则采用两轮评审设计：第一轮由两名初级评审者进行标题与摘要筛选，第二轮由高级评审者进行概念提取[8]。

然而，这些摘要证据均未明确讨论“摘要证据与全文证据冲突”这一具体场景。同行评审意见记录[2][3][4][5][6]虽然涉及评审过程，但同样未提供冲突处理的详细机制。

## 3. 证据支持的研究方向

基于现有摘要证据，可识别以下与冲突处理相关的研究方向：

**（1）分层评审与冲突升级机制**：LatteReview框架的两轮设计[8]暗示了冲突处理的潜在路径——当初级评审者（处理摘要级证据）与高级评审者（处理全文级证据）结论不一致时，可通过层级升级机制解决。但摘要证据未描述具体冲突处理流程。

**（2）执行验证作为冲突仲裁手段**：空间Text-to-SQL框架中的“执行-based review”[7]提供了一种客观仲裁思路——当摘要级理解与全文级逻辑冲突时，可通过实际执行结果验证哪一方正确。此方法在SQL领域有效，但能否推广到文献综述场景尚不明确。

**（3）对抗性批评循环**：Adversarial Multi-Agent System中的“critique loops”[1]表明系统支持迭代批评，这为冲突解决提供了对话机制。但摘要证据未说明批评循环如何处理证据层级不一致的问题。

## 4. 摘要级证据的局限

本合成面临显著的证据层级局限：

**（1）缺乏冲突处理的直接证据**：所有8条记录均为摘要级，未提供全文内容。因此，无法确认这些系统是否设计了针对“摘要-全文证据冲突”的专门处理机制[1][7][8]。

**（2）同行评审意见的适用性有限**：记录[2][3][4][5][6]虽以“reviewer”命名，但内容涉及蝙蝠群体涌现建模[2][3]和TRPM亚家族冷却剂结合口袋[4][5][6]，与冲突处理策略无直接关联。这些记录仅表明存在多评审者机制，但未揭示冲突处理逻辑。

**（3）框架细节缺失**：LatteReview的摘要仅提及“title and abstract screening”[8]，未说明当筛选结果与后续全文审查冲突时的处理方式。同样，Adversarial Multi-Agent System的摘要未详细说明“verifiable evidence”如何在不同证据层级间校准[1]。

## 5. 谨慎结论

基于现有摘要级证据，可得出以下谨慎结论：

（1）多智能体系统中的reviewer agent普遍采用分层设计[8]和执行验证[7]来提升准确性，这为处理摘要-全文证据冲突提供了潜在架构基础，但现有摘要证据未明确描述冲突处理的具体协议。

（2）当摘要证据与全文证据冲突时，合理的处理策略应包括：①冲突识别与标记（基于证据层级差异）；②升级至更高级别的评审者或执行验证环节；③通过批评循环进行多轮协商[1]；④在最终输出中明确标注证据冲突的风险等级。

（3）风险提示应至少包含：冲突证据的具体内容、证据层级差异说明、冲突未解决时结论的不确定性声明。现有框架[7]的“reviewer corrections”机制可作为风险提示的参考模板。

（4）强烈建议未来研究在全文层面验证上述推断，并开发标准化的冲突处理与风险提示协议。当前摘要证据不足以支撑具体的操作规范制定。

## 参考文献
[1] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[2] Reviewer #2 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[3] Reviewer #1 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[4] Reviewer #1 (Public Review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[5] Reviewer #2 (Public review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[6] Reviewer #3 (Public Review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[7] From Questions to Queries: An AI-powered Multi-Agent Framework for Spatial Text-to-SQL. arXiv.org. 2025.
[8] LatteReview: a multi-agent framework for systematic review automation using large language models. arXiv preprint arXiv …. 2025.