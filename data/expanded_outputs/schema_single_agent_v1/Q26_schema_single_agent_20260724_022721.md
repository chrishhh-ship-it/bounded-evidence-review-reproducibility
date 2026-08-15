### 1. 检索与筛选概览

本次检索围绕“增加 agent 数量是否总能带来质量提升”这一核心问题展开，从提供的证据集 E_q 中筛选出 8 篇相关文献。这些文献涵盖了多智能体系统的综述、具体应用（如云计算工作流调度、车联网边缘计算、云机器人资源分配）以及控制理论（如容错控制、集群共识）等领域。证据集主要基于摘要级信息，未提供全文细节，因此分析将严格限定在摘要所揭示的范围内。

### 2. 核心主题与证据

现有证据表明，增加 agent 数量并不总能带来质量提升，其效果高度依赖于任务特性、系统架构和协调机制。

- **正面证据：多智能体协作可提升性能**。在车联网边缘计算中，多智能体深度强化学习方案通过协作优化，能够降低系统处理时延并提升安全概率 [4]。类似地，在车辆通信资源分配中，联邦多智能体强化学习通过多个 V2V 智能体的协同训练，提高了蜂窝链路的总速率和 V2V 数据包投递率 [8]。这些案例说明，在动态、复杂的分布式环境中，适当增加 agent 数量并配合有效的协作机制（如联邦学习、惩罚机制）可以带来性能提升。

- **负面与条件性证据：增加 agent 带来挑战**。多智能体系统的综述明确指出，采用学习系统会增加复杂性，面临一系列挑战 [1]。例如，在异构非线性多智能体系统中，即使采用事件触发控制以节省网络资源，仍需应对网络攻击（如 DoS 攻击）和执行器故障等复杂问题，增加 agent 数量会加剧通信拓扑和协调的难度 [6]。此外，在云机器人资源分配中，多智能体环境下的资源分配和服务供给策略本身就是一个需要专门研究的问题，暗示着 agent 数量增加会带来新的优化难题 [5]。

- **中性证据：性能取决于具体设计**。在多目标工作流调度中，基于深度 Q 网络的多智能体强化学习方法虽然优于传统算法，但其性能依赖于马尔可夫博弈模型的设计，包括状态输入（工作流数量、虚拟机数量）和奖励函数（完成时间、成本）的设定 [3]。这表明，增加 agent 数量本身不是关键，关键在于如何设计智能体之间的交互与学习机制。同样，在供应链敏捷性研究中，多智能体系统与大数据处理的结合需要特定的信息系统支持，才能实现 e-business 的效益 [2]。

### 3. 证据支持的研究方向

基于现有摘要级证据，以下研究方向值得关注：

- **多智能体系统的可扩展性与协调机制**：研究如何设计轻量级、去中心化的协调协议（如事件触发机制 [6]、联邦学习 [8]），以应对 agent 数量增加带来的通信和计算开销。
- **动态环境下的鲁棒性与安全性**：在车联网 [4] 和网络攻击 [6] 等动态场景中，探索如何通过多智能体强化学习或容错控制，保证系统在 agent 数量变化时的稳定性和安全性。
- **任务与资源异构性下的优化**：针对云工作流 [3]、云机器人 [5] 等异构任务，研究如何自适应地分配计算和通信资源，避免因 agent 数量过多导致资源竞争和性能下降。
- **多智能体学习的收敛性与稳定性**：如文献 [3] 和 [8] 所示，需要进一步研究多智能体强化学习在非平稳环境下的收敛条件，以及如何通过联邦学习等范式缓解训练不稳定性。

### 4. 摘要级证据的局限

本合成完全依赖摘要级证据，存在以下明显局限：

- **缺乏实验细节与定量结果**：摘要仅提及“仿真结果优于基线”[3][4][8]，但未提供具体的性能指标（如时延降低百分比、成功率提升幅度），无法量化 agent 数量增加对质量的边际影响。
- **未区分“质量”的具体维度**：不同文献对“质量”的定义不同，包括调度最优性 [3]、系统时延 [4]、数据包投递率 [8]、集群共识达成 [6] 等。摘要未说明这些质量指标是否随 agent 数量单调变化。
- **缺乏负面或失败案例**：证据集主要报告成功案例，未包含增加 agent 导致性能下降的实证研究，可能产生“幸存者偏差”。
- **上下文依赖性**：各研究针对特定领域（车联网、云计算、机器人），其结论难以直接泛化到通用多智能体系统。

### 5. 谨慎结论

基于现有摘要级证据，**增加 agent 数量并不总能带来质量提升**。其效果取决于三个关键因素：**任务是否可分解**（如分布式资源分配任务适合多智能体协作 [4][8]）、**协调机制是否有效**（如联邦学习 [8] 或事件触发控制 [6] 可缓解通信压力）、**系统是否具备鲁棒性**（如针对网络攻击的容错设计 [6]）。在缺乏有效协调和资源管理的情况下，增加 agent 数量可能引入通信开销、训练不稳定性和安全风险，反而导致性能下降。因此，研究者应关注“如何设计多智能体系统”而非“是否增加 agent 数量”，并需通过更全面的实验（包括负样本）来验证结论的普适性。

## 参考文献
[1] Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
[2] A multi-agent based system with big data processing for enhanced supply chain agility. M Giannakis, M Louis - Journal of Enterprise Information …, 2016 - emerald.com. 2016.
[3] Multi-Objective Workflow Scheduling With Deep-Q-Network-Based Multi-Agent Reinforcement Learning. IEEE Access. 2019.
[4] Joint Secure Offloading and Resource Allocation for Vehicular Edge Computing Network: A Multi-Agent Deep Reinforcement Learning Approach. IEEE Transactions on Intelligent Transportation Systems. 2023.
[5] Resource allocation and service provisioning in multi-agent cloud robotics: A comprehensive survey. M Afrin, J Jin, A Rahman, A Rahman… - … Surveys & Tutorials, 2021 - ieeexplore.ieee.org. 2021.
[6] Event-Triggered Adaptive Fault-Tolerant Pinning Control for Cluster Consensus of Heterogeneous Nonlinear Multi-Agent Systems Under Aperiodic DoS Attacks. IEEE Transactions on Network Science and Engineering. 2021.
[7] A survey of ai agent protocols. Y Yang, H Chai, Y Song, S Qi, M Wen, N Li… - arXiv preprint arXiv …, 2025 - arxiv.org. 2025.
[8] Federated Multi-Agent Deep Reinforcement Learning for Resource Allocation of Vehicle-to-Vehicle Communications. IEEE Transactions on Vehicular Technology. 2022.