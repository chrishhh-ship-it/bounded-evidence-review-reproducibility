## 1. 检索与筛选概览

本合成基于所提供的8篇文献证据，这些文献均来自公开的学术预印本或同行评审期刊，发表时间跨度为2023年至2026年。文献来源包括arXiv、Methods and Protocols、Environmental Evidence等。所涉研究主题聚焦于多智能体系统（MAS）在各类专业领域的应用，特别是其在信息筛选、文献审查与数据验证中的角色。在筛选过程中，所有文献均被纳入分析，未进行额外的质量排除，以确保对“screening agent”作用的全面覆盖。

## 2. 核心主题与证据

综合现有证据，“screening agent”（筛选智能体）在多智能协同情报服务中的核心作用主要体现在以下几个方面：

**（1）自动化文献与数据筛选，提升效率与规模**  
多智能体系统被广泛用于自动化执行传统上需要大量人工的筛选任务。例如，Manalyzer系统通过多智能体协作实现了元分析的端到端自动化，其流程包括文献检索、论文筛选和数据提取，显著减少了人工投入[2]。在医疗健康领域，多智能体框架在临床试验匹配中将临床医生的筛选效率提升了42.6%[4]。LatteReview框架则专门设计了由两个初级评审智能体（round A）和一个高级评审智能体（round B）组成的标题与摘要筛选工作流，实现了分阶段、分角色的自动化筛选[8]。

**（2）通过混合审查与交叉验证缓解“幻觉”问题**  
在自动化筛选过程中，大语言模型（LLM）常面临“幻觉”问题，即生成不准确或虚构的信息。多智能体系统通过引入混合审查、分层提取、自我证明和反馈检查等策略，显著缓解了这一问题[2]。例如，在生物医学领域，多智能体架构通过专业智能体团队分工协作、使用精确工具并交叉验证输出，将肿瘤学决策的准确率从30.3%提升至87.2%[4]。在材料科学领域，LitMOF框架通过直接从原始文献中验证晶体学信息并与数据库条目交叉验证，成功修复了8,771个无效条目，占最新CoRE MOF数据库中不可计算结构的65.3%[5]。

**（3）增强情报服务的可靠性与准确性**  
在需要高可靠性的领域，筛选智能体通过标准化操作流程（SOP）和知识图谱增强来减少错误。Chatlaw法律助手模拟真实律师事务所的工作流程，通过人工筛选与知识图谱结合构建高质量法律数据集，显著降低了法律服务中的错误和幻觉[1]。在系统综述中，多智能体系统被用于执行严格的筛选和偏倚风险评估，例如在关于Bti蚊虫控制对生态系统影响的系统综述中，筛选过程包括标题/摘要双重筛选和全文筛选，并由两名独立评审员进行批判性评估[7]。

**（4）发现传统方法忽略的关联与模式**  
部分多智能体系统被设计用于超越传统线性筛选逻辑，发现跨学科的收敛点和结构性研究空白。Rhizomatic Research Agent（V3）基于德勒兹过程关系本体论，通过12个专业智能体在七阶段架构中运行，能够揭示传统综述方法系统性忽略的横向联系和涌现模式[3]。LitMOF系统在修复数据库的同时，还发现了12,646个实验报道但未被现有资源收录的MOF结构，显著扩展了已知的实验设计空间[5]。

## 3. 证据支持的研究方向

基于现有证据，未来研究可聚焦于以下方向：

- **筛选智能体的幻觉缓解机制**：进一步研究混合审查、分层提取和反馈检查策略在不同领域（如法律、医疗、材料科学）中的泛化能力与优化方法[2][4][5]。
- **跨领域标准化筛选流程的构建**：借鉴Chatlaw中的SOP理念[1]和系统综述中的PRISMA指南[6]，开发适用于多学科情报服务的标准化多智能体筛选协议。
- **非线性与涌现性情报发现**：探索基于过程本体论的非线性筛选方法，以捕捉传统线性筛选无法识别的跨学科关联与研究空白[3]。
- **筛选智能体的临床与实地验证**：当前多数MAS模型缺乏临床验证[6]，未来需加强在真实世界环境中的部署与评估，特别是在医疗决策和生态监测领域[4][7]。
- **大规模数据库的自校正与持续更新**：借鉴LitMOF的范式，开发能够自动从文献中验证并修复数据库错误的多智能体系统，实现科学数据库的自我维护[5]。

## 4. 摘要级证据的局限

本合成完全依赖于文献摘要级证据，存在以下固有局限：

- **细节缺失**：摘要无法提供筛选智能体具体的技术实现细节（如算法架构、训练数据规模、超参数设置）、实验设计（如对照组设置、样本量计算）以及完整的性能指标（如精确率、召回率、F1分数）。例如，Manalyzer的“混合审查”策略具体如何运作[2]，或LatteReview中初级与高级智能体的具体模型配置[8]，均无法从摘要获知。
- **偏倚风险不可评估**：摘要通常不报告研究的方法学偏倚风险，如随机化、盲法、选择性报告等。例如，关于Bti影响的系统综述虽然提及了偏倚评估[7]，但摘要未提供评估结果的具体分布。多数MAS研究被指出缺乏临床验证[6]，但摘要无法揭示其内部效度。
- **结果泛化性不确定**：摘要中报告的性能提升（如准确率从30.3%提升至87.2%[4]）可能基于特定数据集或场景，其在不同领域、不同语言、不同数据质量下的泛化能力未知。
- **时效性与出版偏倚**：部分文献为预印本（如arXiv），尚未经过正式同行评审[1][2][3][5][8]，其结论可能随后续修订而变化。同时，摘要级证据可能倾向于报告正面结果，存在出版偏倚风险。

## 5. 谨慎结论

基于现有摘要级证据，可以谨慎得出以下结论：在多智能协同情报服务中，筛选智能体（screening agent）的核心作用在于**自动化执行大规模、多阶段的文献与数据筛选任务，并通过多智能体间的分工协作、交叉验证与标准化流程，显著提升筛选效率、缓解大语言模型的幻觉问题，并增强情报产品的可靠性与准确性**。部分先进系统还展现出发现传统线性筛选方法所忽略的跨学科关联与研究空白的能力[3][5]。

然而，上述结论的强度受到摘要级证据固有局限的制约。当前多数研究仍处于概念验证或实验室阶段，缺乏充分的临床或实地验证[6]，且技术细节与偏倚风险信息不足。因此，在将筛选智能体部署于高风险决策场景（如法律咨询、临床诊断）之前，亟需开展更严格的方法学研究、大规模实证评估以及伦理与法律框架的构建。未来研究应优先关注筛选智能体的可重复性、鲁棒性及其在不同情报服务场景中的实际效用边界。

## 参考文献
[1] Chatlaw: A Multi-Agent Collaborative Legal Assistant with Knowledge Graph Enhanced Mixture-of-Experts Large Language Model. arXiv (Cornell University). 2023.
[2] Manalyzer: End-to-end Automated Meta-analysis with Multi-agent System. arXiv.org. 2025.
[3] A Multi-Agent Rhizomatic Pipeline for Non-Linear Literature Analysis. arXiv Preprint. 2026.
[4] A Review of Multi-Agent AI Systems for Biological and Clinical Data Analysis.. Methods and protocols. 2026.
[5] LitMOF: An LLM Multi-Agent for Literature-Validated Metal-Organic Frameworks Database Correction and Expansion. arXiv Preprint. 2025.
[6] Multi-Agent AI Systems in Healthcare: Systematic Evidence Synthesis Via PRISMA of Clinical Decision Support Systems, Robotic Interventions, and Critical Care. International Journal of Latest Technology in Engineering Management &amp; Applied Science. 2025.
[7] Effects of mosquito control using the microbial agent Bacillus thuringiensis israelensis (Bti) on aquatic and terrestrial ecosystems: a systematic review. Environmental Evidence. 2023.
[8] LatteReview: a multi-agent framework for systematic review automation using large language models. arXiv preprint arXiv …. 2025.