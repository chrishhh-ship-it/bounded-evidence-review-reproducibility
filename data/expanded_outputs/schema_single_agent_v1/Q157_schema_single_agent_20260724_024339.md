## 多智能体文献综合系统如何记录检索策略以满足PRISMA 2020报告要求：一项摘要级证据综合

### 1. 检索与筛选概览

本综合基于E_q中提供的8篇文献记录，这些记录均来自2022年至2026年间发表的学术文献，涵盖期刊论文、会议论文和预印本。文献来源包括Semantic Scholar、ACM、IEEE、arXiv以及多种学术期刊[1][2][3][4][5][6][7][8]。所有记录均为摘要级证据，未获取全文。在筛选过程中，我们识别出与“多智能体系统”和“文献综合”直接相关的记录共6篇[1][4][5][6][7][8]，另有2篇提供了方法论背景[2][3]。其中，[3]专门讨论了系统综述和范围综述的方法论要求，特别是PRISMA指南的应用，为评估检索策略报告提供了参照标准。

### 2. 核心主题与证据

**主题一：PRISMA 2020报告要求与检索策略记录**

PRISMA（系统综述和荟萃分析优先报告条目）指南要求系统综述详细记录检索策略，包括数据库名称、检索日期、完整的检索式以及筛选流程[3][8]。在E_q中，[8]明确声明其遵循PRISMA指南进行了系统检索，检索了PubMed、IEEE Xplore、Scopus和Web of Science四个数据库，共检索到150条记录，经去重和筛选后纳入32项研究[8]。该研究还报告了使用乔安娜布里格斯研究所（JBI）关键评估清单进行质量评估[8]。相比之下，[5]虽进行了文献综述和文献计量评估，但仅提及在三个学术数据库和Scopus中检索了39篇相关论文和587篇文献计量分析文档，未明确声明遵循PRISMA指南[5]。

**主题二：多智能体文献综合系统的检索策略实践**

当前多智能体文献综合系统在检索策略的记录和报告方面存在显著差异。[1]描述的ResearchPilot系统通过自然语言研究问题从Semantic Scholar和arXiv检索论文，但未详细说明检索式的构建过程、检索日期或筛选标准[1]。[4]介绍的M-Reason系统专注于生物医学证据综合，强调自动化证据检索、评估和综合，并提供了完整的可追溯性，从源证据到最终结论均可审计[4]。[6]的SimAgents系统为宇宙学文献参数提取构建了评估数据集，收集了来自arXiv和顶级期刊的40余篇模拟论文，但未报告系统化的检索策略[6]。[7]的ScholarGenie系统集成了论文检索、语义摘要和幻灯片生成，但同样缺乏对检索策略的详细记录[7]。

**主题三：方法论指导与现有差距**

[3]详细阐述了范围综述的方法论要求，指出构建全面检索策略的挑战，包括术语选择困难、主题定义不清等问题，并强调图书馆员在构建检索策略中的关键作用[3]。该文献还指出，系统综述需要至少两名独立评审者进行标题、摘要和全文筛选，并建议使用Rayyan或Covidence等工具记录纳入/排除决策[3]。然而，在E_q中的多智能体系统文献中，[1][4][6][7]均未报告使用双人独立筛选或记录筛选决策的过程，这不符合PRISMA 2020的透明性要求。

### 3. 证据支持的研究方向

基于现有证据，以下研究方向值得探索：

**方向一：开发符合PRISMA标准的自动化检索策略记录模块。** 现有系统如ResearchPilot[1]、M-Reason[4]和ScholarGenie[7]均缺乏对检索策略的完整记录。未来可设计专门代理，自动记录检索数据库、检索式、检索日期、筛选标准和筛选决策，并生成符合PRISMA 2020要求的报告。

**方向二：将PRISMA筛选流程嵌入多智能体工作流。** [3]强调双人独立筛选和决策记录的重要性，而[8]展示了在医疗领域遵循PRISMA的可行性。未来系统可集成双代理独立筛选机制，并自动记录纳入/排除理由，提高透明度和可重复性。

**方向三：跨领域验证多智能体系统的检索策略报告质量。** 现有系统覆盖了生物医学[4]、宇宙学[6]、能源[5]和通用学术[1][7]等领域，但检索策略报告的详细程度差异显著。未来研究可系统评估不同领域多智能体系统对PRISMA要求的符合程度。

### 4. 摘要级证据的局限

本综合完全依赖摘要级证据，存在以下固有局限：

**信息不完整。** 摘要通常仅提供研究的高层次概述，无法获取检索策略的完整细节。例如，[1]的摘要未说明检索式的具体构建方式，[4]虽强调可审计性但摘要未提供检索策略的具体参数，[6]和[7]同样缺乏检索策略的详细描述。这些信息可能存在于全文但无法从摘要获取。

**方法学细节缺失。** [3]指出系统综述需要报告筛选流程、质量评估工具和数据分析方法，但摘要级证据无法提供这些关键方法学细节。例如，[8]虽声明遵循PRISMA，但摘要无法展示其完整的筛选流程图或质量评估结果。

**时效性和覆盖范围限制。** E_q中的文献发表于2022-2026年，但多智能体系统领域发展迅速，可能已有更新方法或系统未被收录。此外，摘要级证据无法验证文献中声称的检索数据库是否全面，或检索策略是否真正符合PRISMA标准。

### 5. 谨慎结论

基于现有摘要级证据，可以得出以下谨慎结论：

第一，当前多智能体文献综合系统在检索策略记录方面普遍不符合PRISMA 2020的完整报告要求。虽然[8]明确声明遵循PRISMA指南并报告了数据库来源和筛选数量，但[1][4][6][7]等系统均未在摘要层面提供足够的检索策略细节，包括检索式、检索日期、筛选标准和决策记录。

第二，PRISMA指南为系统综述提供了明确的报告框架，包括数据库选择、检索式构建、筛选流程和质量评估[3][8]。多智能体系统若要在学术文献综合中发挥可靠作用，必须集成这些报告要求，而不仅仅是实现检索和综合的自动化。

第三，摘要级证据的局限性意味着本综合的结论应被视为初步发现。未来研究应获取全文，系统评估多智能体系统在检索策略记录方面的实际表现，并开发能够自动生成符合PRISMA标准报告的工具。

第四，多智能体系统在提高文献综合效率方面展现出潜力，如[7]报告处理时间减少高达80%，[4]强调效率提升和输出一致性。然而，效率提升不应以牺牲报告透明性和可重复性为代价。建议未来系统设计将PRISMA合规性作为核心功能要求，而非事后补充。

## 参考文献
[1] ResearchPilot: A Local-First Multi-Agent System for Literature Synthesis and Related Work Drafting. Semantic Scholar. 2026.
[2] Hybridization of Metaheuristic and Multi-Agent System for solving the tourist trip design problem : A literature review. Proceedings of the 1st ACM SIGSPATIAL International Workshop on Generative and Agentic AI for Multi-Modality Space-Time Intelligence. 2025.
[3] An Introduction to Scoping Reviews. Journal of Graduate Medical Education. 2022.
[4] Biomedical reasoning in action: Multi-agent System for Auditable Biomedical Evidence Synthesis. arXiv Preprint. 2025.
[5] Multi-agent system implementation in demand response: A literature review and bibliometric evaluation. AIMS energy. 2023.
[6] Bridging Literature and the Universe Via A Multi-Agent Large Language Model System. arXiv Preprint. 2025.
[7] ScholarGenie: A Multi-Agentic System for Automated Literature Summarization and Presentation Generation. 2025 International Conference on Advances in Next-Gen Computer Science (ICANCS). 2025.
[8] Multi-Agent AI Systems in Healthcare: Systematic Evidence Synthesis Via PRISMA of Clinical Decision Support Systems, Robotic Interventions, and Critical Care. International Journal of Latest Technology in Engineering Management &amp; Applied Science. 2025.