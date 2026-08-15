## 学术情报综合报告

### 1. 检索与筛选概览

本报告基于给定的8篇文献摘要证据，围绕“在冻结语料设置下，reranking agent应优先优化相关性、可引用性还是摘要质量”这一研究问题进行综合。所提供文献主要涵盖多智能体系统（MAS）在资源分配、调度优化、安全通信、协同控制等领域的应用，时间跨度为2016年至2025年，来源包括IEEE Access、IEEE Transactions系列及arXiv预印本。然而，这些文献均未直接涉及“冻结语料”、“reranking agent”或“摘要质量评估”等核心概念，因此本报告仅能从间接相关的多智能体系统优化目标与评估维度进行推断性分析。

### 2. 核心主题与证据

现有证据表明，多智能体系统的优化目标通常聚焦于任务完成效率、资源利用率和系统稳定性，而非文本相关性或摘要质量。具体而言：

- **任务完成效率与成本优化**：文献[3]指出，在多工作流调度中，多智能体强化学习旨在优化完成时间与用户成本，通过马尔可夫博弈模型寻求makespan与成本之间的相关均衡。文献[4]则针对车载边缘计算网络，以最小化系统处理延迟为目标，同时保障无线卸载过程的安全性。
- **资源分配与通信可靠性**：文献[8]提出联邦多智能体深度强化学习方案，联合优化信道选择与功率控制，以最大化蜂窝链路传输速率并满足V2V通信的可靠性与时延要求。文献[5]综述了多智能体云机器人中的资源分配与服务提供策略，强调资源效率与服务质量。
- **系统鲁棒性与安全性**：文献[6]关注异构非线性多智能体系统在拒绝服务攻击与执行器故障下的集群一致性控制，设计了事件触发自适应容错控制方案。文献[4]则利用物理层安全技术提升卸载过程的安全性。

此外，文献[7]虽涉及AI智能体协议，但其摘要仅提及将大语言模型作为“外部大脑”增强智能体知识，未涉及reranking或摘要质量评估。

### 3. 证据支持的研究方向

基于现有证据，可推断在类似多智能体系统的优化场景中，优先优化的维度应遵循以下方向：

- **相关性优先**：在多智能体协同任务中，智能体需要根据局部观测（如信道状态、队列积压）做出决策，其核心是选择与当前任务目标最相关的动作或资源[8]。类似地，在reranking场景中，相关性应是首要优化目标，以确保检索结果与用户查询意图匹配。
- **可引用性次之**：文献[3]和[4]中，智能体的奖励函数设计依赖于可量化的性能指标（如完成时间、成本、延迟），这些指标可视为“可引用”的客观证据。在学术检索中，可引用性（即来源的权威性与可验证性）可作为辅助优化目标，但现有证据未直接支持其优先性。
- **摘要质量未涉及**：所有文献均未提及摘要生成或质量评估。因此，在冻结语料设置下，摘要质量可能并非多智能体系统的直接优化目标，而是下游任务（如信息呈现）的独立环节。

### 4. 摘要级证据的局限

本报告存在以下显著局限：

- **主题不匹配**：所有8篇文献均聚焦于多智能体系统的工程应用（如调度、资源分配、安全控制），而非信息检索、reranking或摘要质量评估。因此，无法直接回答研究问题。
- **证据粒度不足**：摘要级证据仅提供研究目标、方法概述和主要结论，缺乏对优化目标优先级、评估指标设计或用户反馈机制的详细描述。例如，文献[3]虽提及“多目标优化”，但未说明各目标之间的权重分配或优先级排序。
- **缺乏冻结语料相关讨论**：无任何文献提及“冻结语料”这一设置，即固定训练或测试语料库不更新的场景。因此，无法推断在该特殊条件下reranking agent的优化策略。
- **时间与领域偏差**：文献多发表于2018-2023年，集中于通信、云计算和机器人领域，与自然语言处理中的reranking任务存在领域差异。文献[7]虽为2025年预印本，但内容仍为智能体协议综述，未涉及reranking。

### 5. 谨慎结论

基于现有摘要级证据，无法直接回答“在冻结语料设置下，reranking agent应优先优化相关性、可引用性还是摘要质量”这一问题。从间接类比的角度，多智能体系统在资源分配与任务调度中优先优化任务相关性（如延迟、成本、可靠性）[3][4][8]，其次考虑可量化的性能指标（可类比为可引用性），而摘要质量未被涉及。然而，这一推断高度依赖于领域类比，且缺乏直接证据支持。建议在后续研究中补充信息检索、reranking评估或冻结语料实验的相关文献，以获得更可靠的结论。

## 参考文献
[1] Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
[2] A multi-agent based system with big data processing for enhanced supply chain agility. M Giannakis, M Louis - Journal of Enterprise Information …, 2016 - emerald.com. 2016.
[3] Multi-Objective Workflow Scheduling With Deep-Q-Network-Based Multi-Agent Reinforcement Learning. IEEE Access. 2019.
[4] Joint Secure Offloading and Resource Allocation for Vehicular Edge Computing Network: A Multi-Agent Deep Reinforcement Learning Approach. IEEE Transactions on Intelligent Transportation Systems. 2023.
[5] Resource allocation and service provisioning in multi-agent cloud robotics: A comprehensive survey. M Afrin, J Jin, A Rahman, A Rahman… - … Surveys & Tutorials, 2021 - ieeexplore.ieee.org. 2021.
[6] Event-Triggered Adaptive Fault-Tolerant Pinning Control for Cluster Consensus of Heterogeneous Nonlinear Multi-Agent Systems Under Aperiodic DoS Attacks. IEEE Transactions on Network Science and Engineering. 2021.
[7] A survey of ai agent protocols. Y Yang, H Chai, Y Song, S Qi, M Wen, N Li… - arXiv preprint arXiv …, 2025 - arxiv.org. 2025.
[8] Federated Multi-Agent Deep Reinforcement Learning for Resource Allocation of Vehicle-to-Vehicle Communications. IEEE Transactions on Vehicular Technology. 2022.