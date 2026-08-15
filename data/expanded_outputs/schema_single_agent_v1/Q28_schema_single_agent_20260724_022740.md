# 人工标注在智慧情报服务 benchmark 中应优先覆盖哪些维度？

## 1. 检索与筛选概览

本合成基于提供的8篇文献证据集（E_q），围绕“人工标注在智慧情报服务 benchmark 中应优先覆盖的维度”这一研究问题展开。证据集涵盖2025—2026年间发表的关于大语言模型（LLM）与多智能体系统评估的基准研究，涉及深度研究（Deep Research）智能体、多智能体协作、安全运营、博弈环境等多个领域。通过对这些文献的摘要级证据进行提取与整合，本报告聚焦于人工标注在构建智慧情报服务基准时应优先关注的评估维度，包括事实依据、推理合理性、用户中心性、动态性、多面性、协作能力、失败归因等。

## 2. 核心主题与证据

现有基准研究揭示了人工标注在智慧情报服务评估中应覆盖的多个关键维度，可归纳为以下核心主题：

**（1）事实依据与推理合理性**：ResearchRubrics基准强调，深度研究智能体的评估需要关注“事实依据（factual grounding）、推理合理性（reasoning soundness）和清晰度（clarity）”，并通过2500多条专家编写的细粒度评分标准（rubrics）进行人工标注[1]。该研究发现，即使是领先的深度研究系统，在评分标准上的平均合规率也低于68%，主要问题在于“遗漏隐含上下文”和“对检索信息的推理不充分”[1]。

**（2）用户中心性与动态性**：LiveResearchBench提出了评估深度研究能力的四项原则：任务应具有“用户中心性（user-centric）、动态性（dynamic）、无歧义性（unambiguous）、多面性与搜索密集性（multi-faceted and search-intensive）”[2]。该基准通过1500小时的人工劳动构建了100个专家策划的任务，覆盖日常生活、企业和学术领域，要求进行实时网络搜索与综合[2]。

**（3）内容与报告层面的综合质量**：LiveResearchBench引入了DeepEval评估套件，涵盖“覆盖率、呈现方式、引文准确性与关联性、一致性、分析深度”等内容与报告层面的质量指标，并整合了四种互补的评估协议以确保与人类判断的高度一致性[2]。

**（4）多智能体协作与自主性**：Tool-RoCo基准关注多智能体协作中的“工具使用”与“自主组织”能力，通过四种LLM范式（集中式协作、集中式自组织、去中心化协作、自组织）评估智能体的协作行为[3]。该研究发现，协作工具仅占所有工具的7.09%，表明LLM智能体很少主动调用其他智能体作为助手[3]。

**（5）失败归因的多视角性**：MP-Bench基准提出了“多视角失败归因（multi-perspective failure attribution）”范式，认为多智能体系统的失败往往存在多种合理的归因，人工标注应覆盖“复杂的智能体间依赖关系”和“模糊的执行轨迹”[8]。

**（6）安全运营中的蓝队能力**：SOC-bench设计原则指出，现有基准多聚焦于红队能力，而智慧情报服务需要评估“蓝队操作”能力，包括“大规模勒索软件攻击事件响应”中的五项蓝队任务[5]。

**（7）非传递性环境与种群依赖性**：在非传递性博弈环境中，智能体性能“依赖于对手种群”，排名仅相对于特定对手池和协议有意义[6]。这提示人工标注需考虑评估环境的种群依赖性。

**（8）不完美信息与长期决策**：OpenGuanDan基准提出了“不完美信息、大规模信息集与动作空间、合作与竞争的混合学习目标、长期决策、可变动作空间、动态团队组成”等挑战[7]，这些维度对于智慧情报服务中的复杂决策评估具有参考价值。

## 3. 证据支持的研究方向

基于上述核心主题，人工标注在智慧情报服务benchmark中应优先覆盖以下研究方向：

**方向一：事实依据与推理深度的标注**。应建立细粒度的评分标准，覆盖事实准确性、隐含上下文识别、跨文档综合推理等维度[1][2]。

**方向二：用户需求导向的任务设计**。标注任务应反映真实用户的信息需求，具有动态性（需实时信息）、无歧义性和多面性[2]。

**方向三：报告质量的多维评估**。包括内容覆盖率、呈现方式、引文准确性、分析深度和一致性等[2]。

**方向四：多智能体协作行为的标注**。需评估智能体间的工具调用、自主激活与停用、协作效率等[3][8]。

**方向五：失败归因的多视角标注**。承认失败归因的模糊性，标注应覆盖多种可能的根因[8]。

**方向六：安全运营中的蓝队能力**。针对防御性操作（如事件响应、威胁检测）进行标注[5]。

**方向七：环境依赖性与种群效应**。评估时需考虑对手种群、环境动态性对智能体性能的影响[6]。

**方向八：不完美信息与长期决策**。覆盖信息不完全、动作空间可变、团队动态组成等复杂决策场景[7]。

## 4. 摘要级证据的局限

本合成基于摘要级证据，存在以下局限：

第一，部分文献（如[4]）的摘要内容缺失，无法提取有效证据，限制了相关维度的覆盖。

第二，摘要级信息无法提供具体的标注方法、评分标准细节或人工标注的可靠性数据（如标注者间一致性），仅能反映研究者的主张而非实证结果。

第三，证据集主要来自arXiv预印本（2025—2026年），尚未经过严格的同行评审，其结论的稳健性有待验证。

第四，现有基准多聚焦于通用深度研究或特定领域（如游戏、机器人协作），直接针对“智慧情报服务”这一特定场景的标注维度研究尚不充分，需进一步领域适配。

## 5. 谨慎结论

综合现有证据，人工标注在智慧情报服务benchmark中应优先覆盖以下维度：事实依据与推理合理性、用户中心性与动态性、报告质量的多维指标、多智能体协作行为、失败归因的多视角性、安全运营中的蓝队能力、环境依赖性与种群效应、以及不完美信息下的长期决策能力。然而，这些维度主要源自通用深度研究或多智能体基准，其针对智慧情报服务的适用性需通过领域专家参与的任务设计和标注实验进一步验证。建议未来研究在构建智慧情报服务基准时，借鉴ResearchRubrics的细粒度评分标准方法[1]和LiveResearchBench的用户中心设计原则[2]，同时纳入多智能体协作[3][8]与安全运营[5]等特色维度，并通过大规模人工标注（如2800+小时[1]或1500+小时[2]）确保标注质量。

## 参考文献
[1] ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents. arXiv.org. 2025.
[2] LiveResearchBench: A Live Benchmark for User-Centric Deep Research in the Wild. arXiv.org. 2025.
[3] Tool-RoCo: An Agent-as-Tool Self-organization Large Language Model Benchmark in Multi-robot Cooperation. arXiv.org. 2025.
[4] ASIC-Agent: An Autonomous Multi-Agent System for ASIC Design with Benchmark Evaluation. 2025 IEEE International Conference on LLM-Aided Design (ICLAD). 2025.
[5] Design Principles for the Construction of a Benchmark Evaluating Security Operation Capabilities of Multi-agent AI Systems. arXiv Preprint. 2026.
[6] Population-dependent agent performance in non-transitive games: a multi-agent Rock--Paper--Scissors benchmark. CrossRef. 2026.
[7] OpenGuanDan: A Large-Scale Imperfect Information Game Benchmark. arXiv.org. 2026.
[8] Rethinking Failure Attribution in Multi-Agent Systems: A Multi-Perspective Benchmark and Evaluation. arXiv Preprint. 2026.