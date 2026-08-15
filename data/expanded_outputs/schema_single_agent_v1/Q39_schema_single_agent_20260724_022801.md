## 1. 检索与筛选概览

本合成基于提供的8篇文献证据，聚焦于多源学术检索中由query drift引发的主题偏移识别与抑制问题。检索范围涵盖2018年至2026年的研究，包括多智能体信息检索系统、输出漂移检测、大语言模型查询生成、以及智慧图书馆信息搜索框架等方向。筛选标准为直接涉及查询漂移、主题偏移、或检索质量控制的文献。最终纳入的证据包括[1]中基于信息 scent 的查询日志挖掘方法、[2]中多站点临床决策支持系统的输出漂移检测框架、[6]和[7]中关于系统综述布尔查询生成的优化策略、以及[8]中生成式人工智能驱动的信息搜索技术框架。这些文献共同构成了对query drift识别与抑制的多维度理解。

## 2. 核心主题与证据

核心主题为：在多源学术检索中，query drift导致的主题偏移可通过多智能体协作、查询优化及输出监控等机制进行识别与抑制。

- **多智能体协作机制**：[1]提出基于信息 scent 的多智能体系统，通过查询日志挖掘中的聚类和HITS算法，识别相似信息需求的会话，从而抑制因小规模查询引发的主题偏移。[2]进一步提出智能体驱动的输出漂移检测框架，通过为每个站点分配漂移监控智能体，进行批次级输出分布比较，在乳腺癌响应预测中实现F1分数提升达10.3%，有效识别并抑制了跨站点分布偏移。[4]则构建了包含临床推理、证据检索和精炼智能体的多智能体医疗QA框架，通过证据增强和不确定性评分，将系统准确率提升至87%，同时降低了响应中的主题偏移风险。

- **查询优化与漂移抑制**：[6]发现ChatGPT能够生成高精度的布尔查询，尽管以牺牲召回率为代价，但通过精确查询可减少检索中的主题偏移。[7]提出自动MeSH术语建议方法，基于初始自由文本查询推荐有效索引词，显著提升系统综述查询的质量，从而抑制因术语不匹配导致的query drift。[5]中的URCA框架通过统一检索聚类增强，在证据提取任务中F1分数提升10.3%，其聚类机制有助于聚焦于相关证据，减少主题漂移。

- **输出监控与自适应调整**：[2]强调自适应、站点感知的智能体监控方案在缺乏站点特定参考时表现最佳，漂移检测F1达74.3%，严重性分类F1达83.7%。[8]提出的基于大语言模型智能体的生成式信息搜索框架，通过“意图感知+认知建构+内容生成”模式，支持人智协同的认知构建，从而动态适应查询意图，抑制主题偏移。

## 3. 证据支持的研究方向

基于上述证据，以下研究方向具有明确支持：

- **多智能体协作的漂移检测与抑制**：结合[1]、[2]和[4]的证据，开发自适应、站点感知的智能体框架，用于实时监控和纠正多源检索中的主题偏移。
- **查询优化与术语标准化**：利用[6]和[7]中的方法，通过大语言模型生成高精度布尔查询或自动建议MeSH术语，减少因查询表述模糊导致的漂移。
- **证据增强与聚类机制**：借鉴[5]中的URCA框架，通过聚类和检索增强生成，聚焦于相关证据，抑制无关信息的引入。
- **人智协同的认知构建**：基于[8]的技术框架，探索大语言模型智能体与用户意图的动态匹配，实现从被动响应到主动认知增益的服务转型。

## 4. 摘要级证据的局限

本合成仅基于摘要级证据，存在以下局限：首先，摘要信息可能省略了方法细节、实验设置和失败案例，例如[1]中信息 scent 的具体计算方式、[2]中漂移检测的阈值设定、以及[6]中ChatGPT生成查询的召回率损失程度均未详细说明。其次，部分文献（如[3]）虽涉及自然语言到查询语言的转换，但未直接讨论query drift问题，其相关性有限。此外，摘要级证据无法验证结果的统计显著性和可重复性，例如[4]中87%准确率的具体置信区间和[5]中F1提升的方差均未报告。最后，文献时间跨度较大（2018-2026），技术演进可能导致早期方法的适用性下降。

## 5. 谨慎结论

综合现有摘要级证据，多源学术检索中query drift引发的主题偏移可通过多智能体协作监控、查询优化及输出自适应调整等策略进行有效识别与抑制。具体而言，智能体驱动的输出漂移检测框架[2]和基于信息 scent 的查询日志挖掘[1]提供了可操作的识别机制；而大语言模型生成的精确布尔查询[6]和自动MeSH术语建议[7]则有助于从源头抑制漂移。然而，这些结论需谨慎对待：证据主要来自模拟环境或特定领域（如医学），其泛化性尚待验证；且摘要级证据缺乏对方法局限性和失败案例的深入剖析。未来研究应结合全文证据和跨领域实验，进一步验证这些策略的鲁棒性和实际部署效果。

## 参考文献
[1] Multi-Agent-Based Information Retrieval System Using Information Scent in Query Log Mining for Effective Web Search. Information Retrieval and Management. 2018.
[2] Agent-Based Output Drift Detection for Breast Cancer Response Prediction in a Multisite Clinical Decision Support System. arXiv Preprint. 2025.
[3] Converting Natural Language to Query Languages Using Large Language Models: A Systematic Literature Review. Brazilian Symposium on Multimedia and the Web. 2025.
[4] A Multi-Agent Framework for Medical AI: Leveraging Fine-Tuned GPT, LLaMA, and DeepSeek R1 for Evidence-Based and Bias-Aware Clinical Query Processing. arXiv Preprint. 2026.
[5] Query-driven Document-level Scientific Evidence Extraction from Biomedical Studies. arXiv Preprint. 2025.
[6] Can ChatGPT Write a Good Boolean Query for Systematic Review Literature Search?. arXiv Preprint. 2023.
[7] Automated MeSH Term Suggestion for Effective Query Formulation in Systematic Reviews Literature Search. arXiv Preprint. 2022.
[8] 生成式人工智能驱动下智慧图书馆信息搜索的技术框架及服务模式研究. 专栏:中国特色图书情报学. 2025.