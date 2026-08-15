## 1. 检索与筛选概览

本合成基于提供的8篇文献证据，聚焦于多源学术检索中由query drift引发的主题偏移识别与抑制问题。检索来源涵盖2018至2026年间的期刊章节、会议论文及预印本，涉及信息检索、临床决策支持、系统综述方法及生成式人工智能等领域。筛选标准为：文献需直接或间接涉及查询漂移、主题偏移、多源检索或查询优化策略。最终纳入的证据包括多智能体系统、输出漂移检测、查询公式化及大语言模型应用等方向的研究成果。

## 2. 核心主题与证据

**2.1 Query Drift的成因与表现**  
多源检索中，query drift常源于用户信息需求难以从短查询中准确推断，导致检索精度低下[1]。在系统综述场景中，复杂的布尔查询构建耗时且易出错，不当的查询可能导致关键证据遗漏或大量无关文献检索，从而引发主题偏移[6]。此外，跨站点临床决策支持系统中，患者群体、成像硬件及采集协议的差异会导致模型输出分布漂移，类似地，多源学术检索中不同数据库的索引差异也可能引发查询主题偏移[2]。

**2.2 识别与抑制策略**  
- **多智能体与信息线索方法**：基于信息线索（Information Scent）的多智能体系统通过挖掘查询日志中的用户会话，聚类相似信息需求，并利用HITS算法生成权威网页推荐，从而抑制查询漂移[1]。类似地，多智能体医疗QA框架通过分工协作（如临床推理、证据检索、精炼）增强回答可靠性，其证据增强机制可降低不确定性（困惑度降至4.13），间接抑制主题偏移[4]。  
- **输出漂移检测**：在跨站点环境中，基于智能体的输出漂移检测方法通过站点级参考分布对比，优于集中式监测（F1提升10.3%），自适应方案在无站点参考时表现最佳（漂移检测F1=74.3%，严重性分类F1=83.7%）[2]。该思路可迁移至学术检索中，通过监测检索结果的主题分布变化来识别query drift。  
- **查询公式化优化**：ChatGPT生成的布尔查询在系统综述中可实现高精度（但牺牲召回率），有助于减少无关文献检索[6]。自动MeSH术语建议方法通过预训练语言模型识别有效索引词，提升查询质量，从而降低因术语不当导致的主题偏移[7]。  
- **检索增强生成（RAG）框架**：URCA框架通过统一检索与聚类增强，在冲突证据提取任务中F1提升10.3%，其文档级证据提取能力有助于在多源检索中保持主题聚焦[5]。生成式AI驱动的智慧图书馆框架则通过LLM智能体协调用户、提供者、内容与策略四要素，实现意图感知与认知建构，抑制检索中的主题漂移[8]。

## 3. 证据支持的研究方向

基于现有证据，以下研究方向具有潜力：  
- **多智能体协同漂移抑制**：结合信息线索模型[1]与输出漂移检测[2]，构建自适应多智能体系统，实时监测并纠正检索中的主题偏移。  
- **大语言模型驱动的查询优化**：利用LLM生成高精度布尔查询[6]并结合自动MeSH建议[7]，减少因查询公式化不当引发的漂移。  
- **RAG框架与证据增强**：借鉴URCA[5]和医疗QA框架[4]的证据检索与不确定性估计机制，在多源检索中增强主题一致性。  
- **人智协同的认知建构**：基于智慧图书馆框架[8]，通过人机交互动态调整检索策略，抑制认知层面的query drift。

## 4. 摘要级证据的局限

本合成仅依赖摘要级证据，存在以下局限：  
- **方法细节缺失**：如多智能体系统的具体漂移检测算法[1][2]、LLM查询生成的评估指标[6]及URCA的聚类策略[5]均需全文验证。  
- **领域特异性**：多数证据来自生物医学或临床领域[2][4][5][6][7]，其结论向通用学术检索的泛化性有待检验。  
- **时效性与规模**：部分文献为预印本[2][4][5][6][7]，且样本量有限（如CochraneForest仅202个注释图[5]），可能影响结论稳健性。  
- **缺乏直接实验**：无文献直接以“query drift抑制”为核心实验，现有证据均为间接推断。

## 5. 谨慎结论

现有证据表明，多源学术检索中的query drift可通过多智能体协同、输出漂移监测、LLM驱动的查询优化及RAG框架等策略进行识别与抑制。然而，这些方法多源自特定领域（如医学、图书馆学），且缺乏直接针对query drift的对比实验。未来研究需在通用学术检索场景中开展系统性评估，尤其应关注跨数据库索引差异、用户意图动态变化及实时漂移检测的可行性。在获得更充分证据前，建议结合多种策略（如查询扩展+输出监测）以降低主题偏移风险。

## 参考文献
[1] Multi-Agent-Based Information Retrieval System Using Information Scent in Query Log Mining for Effective Web Search. Information Retrieval and Management. 2018.
[2] Agent-Based Output Drift Detection for Breast Cancer Response Prediction in a Multisite Clinical Decision Support System. arXiv Preprint. 2025.
[3] Converting Natural Language to Query Languages Using Large Language Models: A Systematic Literature Review. Brazilian Symposium on Multimedia and the Web. 2025.
[4] A Multi-Agent Framework for Medical AI: Leveraging Fine-Tuned GPT, LLaMA, and DeepSeek R1 for Evidence-Based and Bias-Aware Clinical Query Processing. arXiv Preprint. 2026.
[5] Query-driven Document-level Scientific Evidence Extraction from Biomedical Studies. arXiv Preprint. 2025.
[6] Can ChatGPT Write a Good Boolean Query for Systematic Review Literature Search?. arXiv Preprint. 2023.
[7] Automated MeSH Term Suggestion for Effective Query Formulation in Systematic Reviews Literature Search. arXiv Preprint. 2022.
[8] 生成式人工智能驱动下智慧图书馆信息搜索的技术框架及服务模式研究. 专栏:中国特色图书情报学. 2025.