## 1. 检索与筛选概览

本合成基于提供的8篇摘要级证据文献，涵盖6G网络、ChatGPT、多智能体系统、产消者市场、AI聊天机器人及用户接受度等主题。这些文献发表于2016至2023年间，来源包括IEEE、Nature、Elsevier等权威数据库。然而，所提供证据集（E_q）与“冻结语料库边界对知识服务系统实用性评估的影响”这一核心问题存在显著主题偏差：多数文献聚焦于AI技术本身（如聊天机器人设计[5][6]、用户接受度[7]）或通信网络架构[1]，而非语料库管理或系统评估方法论。因此，本合成仅能基于现有证据进行有限推断，无法直接回答原始研究问题。

## 2. 核心主题与证据

尽管证据集未直接讨论“冻结语料库边界”，但可提取以下与知识服务系统实用性评估相关的间接主题：

- **AI系统依赖动态知识更新**：ChatGPT等AI语言模型面临数据偏差、伦理问题及局限性[2]，其性能高度依赖训练数据的时效性与覆盖面。若语料库边界被冻结（即不更新），系统可能无法适应新知识或纠正旧有偏差，从而影响实用性。
- **用户接受度与系统可信度**：用户对AI技术的接受受感知有用性、信任、努力期望等因素影响[7]。在知识服务场景中，若语料库冻结导致输出过时或错误，将损害用户信任，降低系统实用性。
- **代理系统与任务委派**：多智能体系统[3]及代理型信息系统[8]涉及将任务委派给AI。冻结语料库可能限制代理的决策能力，尤其在需要实时信息或领域知识更新的场景中（如医疗临床决策支持[8]）。
- **产消者市场的动态性**：在能源产消者市场中，系统需整合分布式资源并应对不确定性[4]。类似地，知识服务系统若语料库冻结，将无法反映用户需求或环境变化，导致评估结果偏离实际。

## 3. 证据支持的研究方向

基于现有证据，可识别以下与“冻结语料库边界”间接相关的研究方向：

- **AI系统的持续学习与更新机制**：鉴于ChatGPT等模型存在数据偏差和局限性[2]，未来研究需探索如何动态更新语料库以维持系统实用性。例如，结合区块链技术[1]或量子计算[1]实现安全、可追溯的知识更新。
- **用户信任与系统透明度**：用户对AI的信任是接受度的关键因素[7]。冻结语料库可能降低系统透明度（如无法解释输出来源），需研究如何通过设计（如拟人化线索[5]）或反馈机制缓解信任危机。
- **跨领域适应性评估**：不同场景（如旅游[6]、客户服务[5]）对语料库时效性要求不同。需建立评估框架，量化冻结语料库对特定领域（如医疗、法律）实用性的影响。
- **代理系统的鲁棒性**：在委派任务给AI代理时[8]，冻结语料库可能导致代理在未知情境下失效。需研究如何通过多智能体协作[3]或混合人机系统增强鲁棒性。

## 4. 摘要级证据的局限

本合成受限于以下证据缺陷：

- **主题不匹配**：所有8篇文献均未直接探讨“语料库边界冻结”或“知识服务系统实用性评估”。例如，[1]讨论6G网络架构，[4]聚焦能源市场，与核心问题无关。
- **证据粒度不足**：摘要级证据仅提供高层概述，缺乏方法论细节（如评估指标、实验设计）。例如，[7]虽综述AI接受度，但未涉及语料库管理对系统性能的影响。
- **时间与领域偏差**：文献集中于2016-2023年，且以AI技术为主，未覆盖传统知识服务系统（如图书馆、法律数据库）的评估实践。
- **缺乏对比基线**：无文献提供“冻结语料库”与“动态更新”系统的对比实证，无法直接推断边界效应。

## 5. 谨慎结论

基于现有证据，可得出以下有限结论：

- **间接关联**：冻结语料库边界可能通过影响AI系统的知识时效性、用户信任及代理决策能力，间接降低知识服务系统的实用性。这一推断主要来自对ChatGPT局限性[2]、用户接受度因素[7]及代理系统委派机制[8]的间接推理。
- **研究空白**：当前证据集无法支持对“冻结语料库边界如何影响实用性评估”的量化或机制性结论。需补充直接针对语料库管理策略（如更新频率、边界定义）与系统评估指标（如查全率、用户满意度）的实证研究。
- **方法论警示**：摘要级证据的局限性表明，未来研究需采用自然主义方法[7]或纵向实验，以捕捉语料库冻结对系统实际使用行为的影响。

综上，本合成仅能提供间接关联性推断，无法满足原始研究问题的严格回答。建议在后续工作中纳入专门讨论语料库管理、知识系统评估或信息检索的文献。

## 参考文献
[1] 6G Wireless Networks: Vision, Requirements, Architecture, and Key Technologies. IEEE Vehicular Technology Magazine. 2019.
[2] ChatGPT: A comprehensive review on background, applications, key challenges, bias, ethics, limitations and future scope. Internet of Things and Cyber-Physical Systems. 2023.
[3] Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
[4] Electricity market design for the prosumer era. Nature Energy. 2016.
[5] AI-based chatbots in customer service and their effects on user compliance. Electronic Markets. 2020.
[6] Adoption of AI-based chatbots for hospitality and tourism. International Journal of Contemporary Hospitality Management. 2020.
[7] What factors contribute to the acceptance of artificial intelligence? A systematic review. Telematics and Informatics. 2022.
[8] The next generation of research on IS use: A theoretical framework of delegation to and from agentic IS artifacts. A Baird, LM Maruping - MIS quarterly, 2021 - misq.umn.edu. 2021.