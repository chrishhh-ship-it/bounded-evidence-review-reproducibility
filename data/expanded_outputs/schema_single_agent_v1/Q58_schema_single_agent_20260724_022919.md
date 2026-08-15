## 人工评估子集应优先覆盖哪些高风险 query，才能最有效校验自动指标？

### 1. 检索与筛选概览

本合成基于提供的8篇文献证据，聚焦于“人工评估子集应优先覆盖哪些高风险 query，才能最有效校验自动指标”这一研究问题。证据来源涵盖多智能体信息检索系统、大语言模型（LLM）在查询语言转换与系统综述中的应用、医学证据提取框架、以及生成式人工智能驱动的信息搜索服务模式等方向。通过对这些文献的梳理，我们识别出高风险 query 的核心特征，并据此提出人工评估子集的优先覆盖策略。

### 2. 核心主题与证据

**高风险 query 的核心特征**：综合现有证据，高风险 query 主要出现在以下场景：一是涉及医学或临床决策的查询，因其结果直接影响患者健康与治疗方向[3][4]；二是系统综述中的复杂布尔查询，其质量直接影响证据检索的完整性与综述结论的可靠性[5][6]；三是用户信息需求模糊、查询规模小且难以推断意图的搜索场景，这类查询容易导致检索精度低下[1]。

**高风险 query 对自动指标校验的挑战**：现有研究表明，自动指标在评估高风险 query 时存在显著局限。例如，在系统综述文献检索中，ChatGPT 生成的布尔查询虽能实现高精度，但往往以牺牲召回率为代价[5]；在医学证据提取任务中，即使采用先进的检索增强生成框架（如 URCA），面对存在冲突证据的临床问题时，自动系统的表现仍面临复杂性挑战[4]。此外，多智能体医学问答框架的证据表明，即使经过微调的 LLM（如 DeepSeek R1）在自动指标（ROUGE、BLEU）上表现优异，其实际临床可靠性仍需通过人工验证来确保，尤其是在高风险或高不确定性场景下[3]。

**人工评估子集的优先覆盖策略**：基于上述证据，人工评估子集应优先覆盖以下类型的高风险 query：第一，涉及临床决策或医学证据综合的查询，特别是那些存在冲突证据或需要证据分级的问题[3][4]；第二，系统综述中的复杂布尔查询，因为这类查询的构建质量直接决定文献检索的全面性与准确性[5][6]；第三，用户信息需求不明确的小规模查询，这类查询在传统检索中精度低下，且自动指标难以有效反映其真实信息满足度[1]；第四，涉及多智能体协作或生成式信息搜索的查询，因为这类场景中自动指标可能无法捕捉人智协同过程中的认知增益效果[7][8]。

### 3. 证据支持的研究方向

**高风险 query 的识别与分类**：未来研究可借鉴多智能体框架中的不确定性估计方法（如 Monte Carlo dropout 和困惑度评分）[3]，以及基于信息 scent 的查询日志挖掘技术[1]，开发自动识别高风险 query 的机制。同时，可结合系统综述中 MeSH 术语建议方法[6]和布尔查询生成评估[5]的经验，建立高风险 query 的分类体系。

**人工评估与自动指标的协同校验**：现有证据表明，在医学多智能体框架中，对于高风险或高不确定性案例，系统会触发可选的人工验证路径[3]。这一设计思路可推广至更广泛的评估场景：人工评估子集应聚焦于自动指标表现不稳定或置信度较低的 query，从而实现对自动指标的有效校验与校准。

**生成式信息搜索中的人智协同评估**：随着生成式人工智能驱动的信息搜索服务从“工具型”向“协同型”转变[7]，以及多智能体通信拓扑的自动设计[8]，人工评估需要关注自动指标无法量化的认知增益、协作效率与用户满意度等维度。

### 4. 摘要级证据的局限

本合成所依据的均为摘要级证据，存在以下局限：首先，摘要信息可能省略了实验设计细节、数据集构成、统计显著性检验等关键方法学信息，导致对自动指标校验效果的推断不够精确。其次，部分文献（如[1][7]）的摘要未提供具体的评估指标数值或人工评估流程，限制了对其结论的量化验证。此外，不同文献的研究场景（医学、系统综述、通用搜索）差异较大，摘要级证据难以充分揭示这些场景下高风险 query 的共性特征与差异。最后，部分文献为预印本（如[3][4][5][6]），尚未经过同行评审，其结论的可靠性有待进一步确认。

### 5. 谨慎结论

基于现有摘要级证据，可以初步认为：人工评估子集应优先覆盖涉及临床决策、系统综述复杂布尔查询、用户意图模糊的小规模查询以及多智能体协作场景中的高风险 query，因为这些场景中自动指标（如 ROUGE、BLEU、精度、召回率）往往无法全面反映查询的实际效果与可靠性。然而，由于证据来源的局限性（主要为摘要级信息且部分为预印本），上述结论需谨慎对待。未来研究应基于全文级证据，通过系统实验验证不同风险类型 query 下自动指标与人工评估的一致性，并建立标准化的高风险 query 识别与评估框架。

## 参考文献
[1] Multi-Agent-Based Information Retrieval System Using Information Scent in Query Log Mining for Effective Web Search. Information Retrieval and Management. 2018.
[2] Converting Natural Language to Query Languages Using Large Language Models: A Systematic Literature Review. Brazilian Symposium on Multimedia and the Web. 2025.
[3] A Multi-Agent Framework for Medical AI: Leveraging Fine-Tuned GPT, LLaMA, and DeepSeek R1 for Evidence-Based and Bias-Aware Clinical Query Processing. arXiv Preprint. 2026.
[4] Query-driven Document-level Scientific Evidence Extraction from Biomedical Studies. arXiv Preprint. 2025.
[5] Can ChatGPT Write a Good Boolean Query for Systematic Review Literature Search?. arXiv Preprint. 2023.
[6] Automated MeSH Term Suggestion for Effective Query Formulation in Systematic Reviews Literature Search. arXiv Preprint. 2022.
[7] 生成式人工智能驱动下智慧图书馆信息搜索的技术框架及服务模式研究. 专栏:中国特色图书情报学. 2025.
[8] Assemble Your Crew: Automatic Multi-agent Communication Topology Design via Autoregressive Graph Generation. AAAI Conference on Artificial Intelligence. 2025.