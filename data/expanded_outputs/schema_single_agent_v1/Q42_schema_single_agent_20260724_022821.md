## 检索与筛选概览

当检索结果不足时，系统面临的核心权衡在于：是优先扩展查询以获取更多候选结果，还是放宽筛选阈值以保留更多低分结果，抑或显式降级结论强度以反映证据不足。现有文献从多智能体系统、查询扩展技术、生成式模型应用等角度提供了相关证据，但直接针对这一具体决策问题的系统性研究仍较为有限。本合成基于E_q中的8条摘要级证据，梳理了不同策略的适用场景与潜在效果。

## 核心主题与证据

现有证据表明，查询扩展是应对检索结果不足的常用策略。多智能体系统可通过查询日志挖掘和信息嗅探（information scent）技术，对用户查询进行扩展与推荐，从而更有效地推断用户信息需求[1]。在医学系统综述领域，基于初始布尔查询自动建议MeSH术语的方法，能够显著提升检索质量，弥补仅使用自由文本术语的不足[6]。此外，大语言模型（如ChatGPT）已被证明能够生成高精度的布尔查询，尽管可能以牺牲召回率为代价，但在快速综述等时间受限场景中，这种权衡是可接受的[5]。

放宽筛选阈值方面，证据检索与不确定性估计的结合提供了另一种思路。在医学问答框架中，通过证据增强（evidence augmentation）可降低模型的不确定性（困惑度从基线降至4.13），同时保持较高的相关性（约0.80）[3]。这表明，在证据不足时，引入外部知识库（如PubMed）进行检索增强，可能比单纯放宽阈值更为有效。

显式降级结论强度则与不确定性信号和置信度校准相关。多智能体医学QA框架通过蒙特卡洛dropout和困惑度评分实现不确定性估计，并在高风险或高不确定性情况下触发人工验证路径[3]。这种机制本质上是对结论强度的显式降级，而非盲目追求更多结果。

## 证据支持的研究方向

基于现有证据，可识别出以下研究方向：

1. **自适应策略选择**：不同场景下，查询扩展、阈值放宽与结论降级的优先级可能不同。例如，在系统综述中，高精度查询生成[5]与MeSH术语建议[6]可能优先于阈值放宽；而在临床问答中，不确定性估计与人工验证[3]更为关键。未来研究可探索基于任务需求动态选择策略的框架。

2. **多智能体协作优化**：多智能体系统在信息检索中展现出潜力，通过智能体分工（如推理、证据检索、精炼）可提升结果可靠性[3]。自动生成协作拓扑的方法[8]进一步支持了根据任务需求动态配置智能体结构的可能性，这为应对检索结果不足提供了灵活的系统设计思路。

3. **生成式信息搜索范式**：生成式人工智能驱动的信息搜索正从“被动响应”转向“主动服务”，通过意图感知、认知建构与内容生成实现人智协同[7]。这一范式可能通过主动生成查询变体或合成证据来缓解检索结果不足的问题。

## 摘要级证据的局限

本合成基于摘要级证据，存在以下局限：首先，多数研究聚焦于特定领域（如医学、图书馆学），其结论的通用性有待验证。例如，医学系统综述中的查询扩展方法[5][6]可能不直接适用于其他领域。其次，摘要信息有限，无法获取实验细节（如数据集规模、基线对比、统计显著性），因此难以评估不同策略的相对效果。最后，部分证据来自预印本[3][4][5][6]，未经同行评审，其结论的稳健性需进一步确认。

## 谨慎结论

综合现有证据，当检索结果不足时，系统应优先考虑查询扩展策略，尤其是通过自动术语建议[6]或生成式模型优化查询[5]来提升检索质量。同时，引入外部证据检索与不确定性估计[3]可作为补充，而非简单放宽阈值。显式降级结论强度（如触发人工验证）应作为高风险场景下的安全机制[3]。然而，由于直接针对该决策问题的系统性研究不足，上述建议仍需在具体应用场景中验证。未来研究应关注多策略的动态组合与自适应选择，并探索生成式信息搜索范式[7]在缓解检索结果不足中的潜力。

## 参考文献
[1] Multi-Agent-Based Information Retrieval System Using Information Scent in Query Log Mining for Effective Web Search. Information Retrieval and Management. 2018.
[2] Converting Natural Language to Query Languages Using Large Language Models: A Systematic Literature Review. Brazilian Symposium on Multimedia and the Web. 2025.
[3] A Multi-Agent Framework for Medical AI: Leveraging Fine-Tuned GPT, LLaMA, and DeepSeek R1 for Evidence-Based and Bias-Aware Clinical Query Processing. arXiv Preprint. 2026.
[4] Query-driven Document-level Scientific Evidence Extraction from Biomedical Studies. arXiv Preprint. 2025.
[5] Can ChatGPT Write a Good Boolean Query for Systematic Review Literature Search?. arXiv Preprint. 2023.
[6] Automated MeSH Term Suggestion for Effective Query Formulation in Systematic Reviews Literature Search. arXiv Preprint. 2022.
[7] 生成式人工智能驱动下智慧图书馆信息搜索的技术框架及服务模式研究. 专栏:中国特色图书情报学. 2025.
[8] Assemble Your Crew: Automatic Multi-agent Communication Topology Design via Autoregressive Graph Generation. AAAI Conference on Artificial Intelligence. 2025.