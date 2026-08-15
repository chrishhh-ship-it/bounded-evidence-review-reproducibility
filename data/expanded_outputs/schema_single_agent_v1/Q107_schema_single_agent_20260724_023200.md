## 学术情报综合

### 1. 检索与筛选概览

本综合基于一个受控的、固定边界的语料库（E_q）进行，该语料库包含8篇文献摘要。这些文献覆盖了人工智能（AI）聊天机器人、多智能体系统、6G网络、电力市场设计以及信息系统使用等多个领域。文献来源包括《IEEE Vehicular Technology Magazine》、《Nature Energy》、《MIS Quarterly》等权威期刊，发表时间跨度为2016年至2023年。由于语料库边界固定，本综合仅能基于这8篇摘要级证据进行分析，无法引入外部文献或进行全文检索。

### 2. 核心主题与证据

在给定的语料库中，与“知识服务场景”和“系统实用性评估”直接相关的核心主题是**AI聊天机器人的用户接受度与合规性**。具体证据如下：

- **用户接受度的影响因素**：多项研究指出，感知有用性、感知易用性、信任、感知智能和拟人化是影响用户采纳AI聊天机器人的关键因素[6][7]。其中，信任和拟人化设计能显著提升用户对聊天机器人请求的合规性[5]。
- **人类接触的不可替代性**：尽管AI技术被广泛接受，但在某些文化场景下，人类接触的需求无法被AI复制或替代，无论其感知有用性或易用性如何[7]。这暗示了在知识服务中，完全冻结语料库（即仅依赖AI系统）可能无法满足用户对“人性化”交互的需求。
- **多智能体系统的复杂性**：多智能体学习系统面临增加复杂性的挑战[3]，这提示在知识服务中引入多智能体协作时，系统边界（即语料库范围）的固定可能加剧协调与学习的难度。
- **代理权委托的理论框架**：研究关注用户向信息系统委托权利与责任的现象[8]，例如医生依赖临床决策支持系统。在知识服务中，冻结语料库意味着用户必须将信息检索与知识生成的任务完全委托给系统，这直接影响用户对系统实用性的信任与依赖。

### 3. 证据支持的研究方向

基于上述证据，以下研究方向值得关注：

- **拟人化设计与用户信任**：研究如何通过拟人化设计（如语言风格、交互方式）在固定语料库的AI系统中维持或增强用户信任，从而提升系统实用性[5][6]。
- **文化差异与人类接触需求**：探索不同文化背景下，用户对“人类接触”的需求如何影响对冻结语料库AI系统的接受度[7]。
- **多智能体协作与语料库边界**：研究在知识服务中，多智能体系统如何应对固定语料库带来的学习与协调挑战[3]。
- **委托-代理框架下的实用性评估**：借鉴委托理论[8]，建立评估用户向固定语料库AI系统委托知识任务时的信任、风险与实用性指标。

### 4. 摘要级证据的局限

本综合完全依赖摘要级证据，存在以下局限：

- **缺乏方法细节**：摘要未提供研究的具体方法、样本量、实验设计等，无法评估证据的可靠性与可重复性[2][5][6]。
- **领域覆盖有限**：语料库主要聚焦于AI聊天机器人、6G网络和能源市场，与“知识服务场景”的直接关联较弱，且缺乏对信息检索、知识图谱等核心知识服务技术的专门研究。
- **未涉及查全率与系统边界**：所有摘要均未直接讨论“查全率要求严格”或“冻结语料库边界”对系统实用性评估的影响，因此本综合的推论属于间接推断。
- **时效性与完整性**：语料库仅包含2016-2023年的文献，且部分文献（如[4]）发表于2016年，可能无法反映最新技术进展。

### 5. 谨慎结论

在查全率要求严格的知识服务场景中，冻结语料库的边界可能通过以下机制影响系统实用性评估：

1. **用户信任与合规性**：固定语料库限制了AI系统的知识范围，可能降低用户对系统“全面性”的信任，进而影响用户对系统建议的合规性[5][7]。
2. **人类接触的替代性**：若系统无法提供人类专家式的灵活交互（如解释、追问），用户可能因“人类接触需求”未被满足而降低实用性评价[7]。
3. **多智能体协调难度**：在需要多智能体协作的知识服务中，固定语料库可能加剧学习与协调的复杂性，影响系统整体效率[3]。
4. **委托风险感知**：用户向固定语料库系统委托知识任务时，可能因担心信息遗漏或过时而产生更高的风险感知，从而降低系统实用性[8]。

然而，由于语料库证据的间接性与局限性，上述结论需谨慎对待。未来研究应直接针对知识服务场景，设计包含查全率与语料库边界变量的实证实验，以验证这些假设。

## 参考文献
[1] 6G Wireless Networks: Vision, Requirements, Architecture, and Key Technologies. IEEE Vehicular Technology Magazine. 2019.
[2] ChatGPT: A comprehensive review on background, applications, key challenges, bias, ethics, limitations and future scope. Internet of Things and Cyber-Physical Systems. 2023.
[3] Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
[4] Electricity market design for the prosumer era. Nature Energy. 2016.
[5] AI-based chatbots in customer service and their effects on user compliance. Electronic Markets. 2020.
[6] Adoption of AI-based chatbots for hospitality and tourism. International Journal of Contemporary Hospitality Management. 2020.
[7] What factors contribute to the acceptance of artificial intelligence? A systematic review. Telematics and Informatics. 2022.
[8] The next generation of research on IS use: A theoretical framework of delegation to and from agentic IS artifacts. A Baird, LM Maruping - MIS quarterly, 2021 - misq.umn.edu. 2021.