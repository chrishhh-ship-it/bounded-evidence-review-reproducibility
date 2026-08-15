## 自动化综合管线中已撤回论文的引用处理：一项学术情报综合

### 1. 检索与筛选概览

本综合基于给定的查询限定证据集E_q，共包含8条摘要级证据记录。这些记录涵盖了自动化元分析[1]、心理安全证据综合[2]、真实世界证据教学[3]、城市绿化效果系统评价[4]、移动支付服务文献分析[5]、诊断数据提取自动化系统基准研究[6]、一篇已撤回的工程英语教学研究[7]以及维基百科自动内容生成系统综述[8]。证据来源包括学术期刊、预印本平台及CrossRef，发表年份从2020年至2025年。其中，记录[7]明确标注为“RETRACTED”（已撤回），发表于《World Journal of Engineering》[7]。本综合将严格依据这些摘要级证据进行推理，不引入任何外部信息。

### 2. 核心主题与证据

本综合的核心主题是：在自动化证据综合管线中，如何处理仍保留在冻结语料库中的已撤回论文的引用问题。现有证据揭示了以下几个关键维度：

**自动化综合的现状与挑战**：一项系统综述指出，自动化元分析（AMA）虽在数据处理自动化方面取得进展（占57%），但在高级综合阶段（如异质性评估和偏倚评价）的自动化仍不成熟，仅17%的研究涉及此阶段[1]。另一项针对诊断数据提取的基准研究强调，自动化系统的可靠性、安全性和可重复性尚未得到充分表征，其评估框架应整合正确性、弃权行为、可重复性和安全性[6]。这表明，自动化管线在处理复杂或存在质量问题的文献时面临根本性挑战。

**已撤回论文的识别与处理**：证据集中明确包含一篇已撤回的论文[7]。该研究探讨了超现实文学与计算机辅助语言学习在工程英语课程中的整合，但其结论的有效性因撤回而失效。在自动化综合中，若管线未能识别撤回状态，该论文的发现可能被错误地纳入综合结果，导致偏倚。现有自动化综合研究[1][6]均未专门讨论如何处理已撤回文献，这构成了一个关键的方法论缺口。

**语料库冻结与文献状态更新**：查询假设“已撤回论文仍保留在冻结语料库中”。这意味着语料库的快照性质与文献状态的动态变化之间存在矛盾。虽然系统综述通常基于特定时间点的检索结果，但已撤回论文的持续存在要求管线具备事后标记或过滤机制。证据[8]讨论了维基百科中自动化内容生成代理的评估，但未涉及撤回处理。证据[2][3][4]均为标准系统综述，其方法部分未提及对撤回文献的特殊处理。

### 3. 证据支持的研究方向

基于现有证据，以下研究方向对于解决已撤回论文的引用问题至关重要：

**开发撤回状态感知的自动化管线**：自动化综合系统应集成文献状态跟踪功能，能够识别并标记已撤回论文。这需要与数据库（如PubMed、Retraction Watch）的撤回通知服务对接，或在管线内嵌入撤回检测算法。证据[6]提出的“弃权行为”概念（即在非可推导场景下正确声明不可推导）可扩展为“撤回弃权”——当系统识别到撤回状态时，应主动弃用该文献而非尝试提取数据。

**建立撤回论文的引用透明度标准**：即使撤回论文保留在语料库中，其引用应附带明确的撤回标识。证据[1]指出，自动化综合在偏倚评估方面存在不足，而撤回论文的未标识引用本身就是一种偏倚来源。管线应强制要求在输出中注明“该文献已被撤回”，并解释其未被纳入综合的理由。

**评估撤回论文对综合结果的影响**：需要进行敏感性分析，以量化撤回论文的纳入或排除对综合结论的影响。证据[4]的更新系统综述方法（对比2010年原始版本）提供了纵向比较的范例，类似方法可用于评估撤回论文的“污染效应”。

### 4. 摘要级证据的局限

本综合完全依赖于摘要级证据，这带来了若干固有局限：

**信息粒度不足**：摘要通常不包含方法细节，例如检索策略是否排除了撤回论文、是否进行了撤回状态核查等。例如，证据[1]虽提及“偏倚评估”，但未说明是否涵盖文献撤回这一特定偏倚来源。证据[7]的摘要未明确说明撤回原因，仅通过标题中的“RETRACTED”标识，这限制了对其撤回性质的理解。

**上下文缺失**：摘要无法提供完整的论证链条。例如，证据[6]的基准研究协议虽提及“安全性”评估，但未在摘要中定义其与撤回文献的具体关联。证据[8]的摘要未讨论维基百科内容生成中的质量保证机制，而该机制可能与撤回处理相关。

**时效性与覆盖范围**：证据集包含2025年的预印本[1][8]和已发表研究[6]，但未涵盖可能专门讨论撤回文献处理的最新指南或实证研究。此外，证据[5]聚焦于移动支付服务，与核心主题关联较弱，其价值主要在于展示文献计量方法在结构分析中的应用。

### 5. 谨慎结论

基于当前摘要级证据，可以得出以下谨慎结论：

自动化证据综合管线在处理已撤回论文时面临显著的方法论空白。现有自动化系统主要关注数据提取效率和可重复性[1][6]，尚未将文献撤回状态作为核心质量控制维度。已撤回论文[7]在冻结语料库中的持续存在，要求管线必须集成撤回识别、透明引用和敏感性分析功能。然而，由于证据完全基于摘要，无法确认现有系统是否已隐含地处理了此类问题（例如通过排除特定期刊或年份的文献）。未来研究应优先开发撤回状态感知的自动化框架，并建立统一的引用透明度标准。在缺乏此类机制的情况下，人工审核仍是确保综合结果免受撤回论文污染的必要补充。

## 参考文献
[1] Transforming Evidence Synthesis: A Systematic Review of the Evolution of Automated Meta-Analysis in the Age of AI. arXiv.org. 2025.
[2] The presence and potential impact of psychological safety in the healthcare setting: an evidence synthesis. BMC Health Services Research. 2021.
[3] How is Real World Evidence taught in Nursing? A Systematic review undertaking a narrative synthesis of the literature (Preprint). CrossRef. 2023.
[4] How effective is ‘greening’ of urban areas in reducing human exposure to ground-level ozone concentrations, UV exposure and the ‘urban heat island effect’? An updated systematic review. Environmental Evidence. 2021.
[5] Understanding the Corpus of Mobile Payment Services Research: An Analysis of the Literature Using Co-Citation Analysis and Social Network Analysis. Journal of Information Systems and Technology Management. 2020.
[6] End-to-End Reliability of Automated Systems for Diagnostic Data Extraction: A Benchmark Study in Uro-Oncologic Evidence Synthesis. CrossRef. 2025.
[7] RETRACTED: Integrating hyperreal literature with CALL in English language curriculum for engineering studies in India: an empirical study of the impact on students’ learning. World Journal of Engineering. 2021.
[8] Machines in the Margins: A Systematic Review of Automated Content Generation for Wikipedia. arXiv Preprint. 2025.