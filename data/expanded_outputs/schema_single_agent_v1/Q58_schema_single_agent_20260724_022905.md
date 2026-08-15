## 人工评估子集应优先覆盖哪些高风险 query，才能最有效校验自动指标？

### 1. 检索与筛选概览

本合成基于提供的8条摘要级证据记录，旨在回答“人工评估子集应优先覆盖哪些高风险 query，才能最有效校验自动指标”这一研究问题。证据来源涵盖2018年至2026年的文献，涉及多智能体信息检索、大语言模型（LLM）查询生成、系统评价文献检索、医学证据提取及智慧图书馆信息搜索等主题。所有证据均来自学术出版物或预印本，未进行额外筛选或排除。

### 2. 核心主题与证据

现有证据表明，高风险 query 主要出现在以下场景：**信息需求模糊、临床决策关键、系统评价文献检索复杂、以及多智能体协作中的不确定性**。

首先，**信息需求模糊的小规模查询**是高风险场景之一。由于难以推断用户意图，小规模搜索查询的精度较低，用户信息需求难以有效满足[1]。这类 query 若自动指标失效，将导致检索结果偏离用户真实意图。

其次，**临床医学领域的查询**具有高风险特征。在医学问答中，LLM 的临床使用受限于验证薄弱、证据基础不足和置信信号不可靠[3]。系统评价文献检索中，复杂布尔查询的构建耗时且易出错，低质量查询可能导致遗漏关键证据（造成偏倚）或检索过多无关文献（增加成本）[5]。此外，医学主题词（MeSH）的自动建议方法虽能提升查询效果，但信息专家常不熟悉 MeSH 数据库，难以判断其适用性[6]，这进一步增加了 query 的风险。

第三，**存在冲突证据的临床研究问题**构成高风险。例如，“干细胞移植能否改善克罗恩病患者生活质量”这类问题，需要从文献中提取科学证据，而 CochraneForest 数据集正是为此类任务设计，其复杂性凸显了自动证据提取的挑战[4]。

最后，**多智能体系统中的高不确定性或高风险路径**需要人工验证。在医学多智能体框架中，当系统检测到高不确定性或高风险时，会触发可选的人工验证路径[3]。这表明，自动指标难以完全覆盖的 query 应优先纳入人工评估子集。

### 3. 证据支持的研究方向

基于上述证据，人工评估子集应优先覆盖以下高风险 query 类型：

- **信息需求模糊的短查询**：如用户意图不明确的小规模搜索 query，这类查询在自动评估中容易产生低精度结果[1]。
- **临床决策支持查询**：涉及医学问答、系统评价文献检索及证据提取的 query，其错误可能导致临床偏倚或成本增加[3][5][6]。
- **存在冲突证据的复杂问题**：如 CochraneForest 数据集中的临床研究问题，自动指标难以有效处理[4]。
- **高不确定性或高风险路径**：多智能体系统中，自动指标无法可靠评估的 query 应触发人工验证[3]。

此外，自动指标校验应重点关注**查询生成质量**（如布尔查询的精确度与召回率权衡[5]）、**证据基础充分性**（如是否遗漏关键文献[5]）以及**不确定性量化**（如困惑度评分[3]）。

### 4. 摘要级证据的局限

本合成仅依赖摘要级证据，存在以下局限：首先，摘要可能未完整呈现研究方法的细节，例如具体的高风险 query 定义标准或人工评估协议。其次，部分证据来自预印本（如[3][4][5][6]），尚未经过同行评审，其结论的可靠性需进一步验证。第三，证据覆盖领域有限（以医学和系统评价为主），可能无法全面反映所有高风险 query 类型。最后，摘要中未提供自动指标的具体性能阈值或人工评估的实证案例，限制了结论的精确性。

### 5. 谨慎结论

综合现有证据，人工评估子集应优先覆盖**信息需求模糊的短查询、临床决策支持查询、存在冲突证据的复杂问题以及多智能体系统中的高不确定性路径**，以最有效校验自动指标。这些 query 类型在现有文献中被反复确认为高风险场景，其自动评估的失败可能导致严重后果。然而，由于摘要级证据的局限，建议未来研究进一步通过全文分析和实证实验验证上述结论，并探索更精细的高风险 query 分类标准。

## 参考文献
[1] Multi-Agent-Based Information Retrieval System Using Information Scent in Query Log Mining for Effective Web Search. Information Retrieval and Management. 2018.
[2] Converting Natural Language to Query Languages Using Large Language Models: A Systematic Literature Review. Brazilian Symposium on Multimedia and the Web. 2025.
[3] A Multi-Agent Framework for Medical AI: Leveraging Fine-Tuned GPT, LLaMA, and DeepSeek R1 for Evidence-Based and Bias-Aware Clinical Query Processing. arXiv Preprint. 2026.
[4] Query-driven Document-level Scientific Evidence Extraction from Biomedical Studies. arXiv Preprint. 2025.
[5] Can ChatGPT Write a Good Boolean Query for Systematic Review Literature Search?. arXiv Preprint. 2023.
[6] Automated MeSH Term Suggestion for Effective Query Formulation in Systematic Reviews Literature Search. arXiv Preprint. 2022.
[7] 生成式人工智能驱动下智慧图书馆信息搜索的技术框架及服务模式研究. 专栏:中国特色图书情报学. 2025.
[8] Assemble Your Crew: Automatic Multi-agent Communication Topology Design via Autoregressive Graph Generation. AAAI Conference on Artificial Intelligence. 2025.