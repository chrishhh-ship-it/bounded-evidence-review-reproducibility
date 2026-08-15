## 1. 检索与筛选概览

本合成基于给定的8篇摘要级证据文献，旨在回应“在扩展到n≥200查询时，如何设计分层抽样策略以确保覆盖不同语料覆盖率等级的查询”这一研究问题。经检索，所提供文献主要聚焦于多智能体系统、知识图谱、协作感知、强化学习、教育评估及健康传播等领域，未发现任何文献直接涉及分层抽样策略或语料覆盖率等级的设计方法。因此，本合成将基于现有证据，从间接相关的研究设计、样本规模及方法论启示等角度进行推断性分析。

## 2. 核心主题与证据

所提供证据的核心主题集中于多智能体系统的应用与评估，以及AI在特定领域（如教育、健康）的接受度研究。其中，多项研究采用了n≥200的样本规模或实验设置，为理解大规模查询场景下的方法论挑战提供了间接参考。例如，[1]在1200篇PubMed文章上验证了多智能体框架KARMA的知识图谱富集效果，识别出多达38230个新实体，表明大规模语料处理中需要系统化的覆盖策略。[5]在包含200个车辆智能体和10000个乘车请求的模拟系统中研究了多智能体迁移学习，直接涉及n=200的智能体规模。[6]对200名印尼职前英语教师进行了问卷调查，[7]对200名匈牙利成年人进行了健康传播感知调查，[8]使用了200项肿瘤学随机对照试验进行生物医学文本处理评估。这些研究均表明，当样本或查询规模达到200及以上时，研究者需关注数据覆盖的全面性与代表性。

## 3. 证据支持的研究方向

基于现有证据，可推断出以下与分层抽样策略设计相关的研究方向：

**（1）基于信息增益的自适应采样策略**：[4]提出了信息驱动的多智能体路径规划方法，通过最大化信息增益来避免冗余观测，并在有限通信条件下形成通信子组独立规划。该思路可类比于分层抽样中的层内优化——在n≥200查询时，可依据语料覆盖率等级（如高、中、低覆盖率层）设计自适应采样权重，优先覆盖信息增益最大的层。

**（2）多智能体协作与知识共享机制**：[2]指出多机器人舰队中的协作感知可将感知能力提升200%以上，[5]探讨了多智能体间的迁移学习参数（如置信度阈值、样本量）对系统性能的影响。这些机制提示，在分层抽样中可引入智能体间的协作策略，例如让不同覆盖率等级的查询智能体共享抽样经验，动态调整各层的采样比例。

**（3）大规模环境下的基准测试与验证**：[3]介绍了EnEnv 1.0基准测试环境，包含IEEE 33、Illinois 200等标准测试系统，用于评估多智能体强化学习算法。该工作表明，针对n≥200的查询规模，需构建覆盖不同语料覆盖率等级的标准化测试集，以验证分层抽样策略的有效性。

## 4. 摘要级证据的局限

本合成存在显著局限：所有证据均为摘要级信息，缺乏对分层抽样方法、语料覆盖率定义及具体抽样策略的直接描述。例如，[1]虽涉及大规模知识图谱富集，但未说明其实体发现过程中的抽样方法；[5]虽使用200个智能体，但聚焦于迁移学习而非抽样设计；[8]虽使用200项试验，但关注的是证据引用验证而非覆盖率分层。此外，摘要级证据无法提供方法细节（如层间方差估计、样本量分配公式），限制了直接应用的可能性。因此，本合成仅能提供间接推断，而非确凿的方法论指导。

## 5. 谨慎结论

基于现有摘要级证据，当查询规模扩展到n≥200时，设计分层抽样策略以确保覆盖不同语料覆盖率等级，可考虑以下原则：（1）借鉴信息驱动方法[4]，依据语料覆盖率等级（如高、中、低）划分层，并采用信息增益最大化原则动态调整各层采样权重；（2）引入多智能体协作机制[2][5]，允许不同覆盖率等级的查询智能体共享抽样经验，减少冗余覆盖；（3）构建标准化基准测试环境[3]，验证不同分层策略在n≥200规模下的覆盖效果与效率。然而，上述结论高度依赖间接推断，且缺乏直接证据支持。建议未来研究在具体语料库（如PubMed文献集[1]或生物医学文本[8]）中开展实证实验，明确分层变量（如文档主题、时间跨度、引用频次）与覆盖率等级的关系，并评估不同抽样比例（如按比例分配、最优分配）对查询结果代表性的影响。

## 参考文献
[1] KARMA: Leveraging Multi-Agent LLMs for Automated Knowledge Graph Enrichment. arXiv.org. 2025.
[2] Multi-agent Collaborative Perception for Robotic Fleet: A Systematic Review. ECCV Workshops. 2024.
[3] EnEnv 1.0: Energy Grid Environment for Multi-Agent Reinforcement Learning Benchmarking. Adaptive Agents and Multi-Agent Systems. 2025.
[4] Multi-Agent Vulcan: An Information-Driven Multi-Agent Path Finding Approach. arXiv Preprint. 2024.
[5] Multi-Agent Transfer Learning in Reinforcement Learning-Based Ride-Sharing Systems. arXiv Preprint. 2021.
[6] Are Pre-Service EFL Teachers Ready for AI-Assisted Assessment? The Role of Assessment Literacy in the Digital Era. PANYONARA: Journal of English Education. 2025.
[7] Perception of AI-assisted health communication via ChatGPT in Hungary. Asian Education and Development Studies. 2026.
[8] Show Your Work: Verbatim Evidence Requirements and Automated Assessment for Large Language Models in Biomedical Text Processing. CrossRef. 2026.