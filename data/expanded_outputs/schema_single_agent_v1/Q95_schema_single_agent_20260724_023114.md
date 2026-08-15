# 多智能体协作中角色间信息传递格式对下游引用追踪准确性的影响：基于摘要级证据的初步合成

## 1. 检索与筛选概览

本合成基于给定的8篇摘要级证据记录（E_q），旨在探讨多智能体协作中角色间信息传递格式（如JSON/Markdown）如何影响下游引用追踪的准确性。然而，经初步筛选发现，所提供的证据集并未直接涉及“多智能体协作中信息传递格式”或“引用追踪准确性”这一核心研究问题。现有文献主要涵盖以下领域：基于大语言模型的生物医学文献证据提取系统[1]、6G无线网络架构[2]、ChatGPT的综合评述[3]、多智能体系统综述[4]、能源领域产消者市场设计[5]、AI客服聊天机器人用户依从性[6]、旅游行业聊天机器人采纳[7]以及AI技术接受度的系统综述[8]。其中，仅文献[1]和[4]与多智能体系统或结构化信息处理存在部分关联，但均未直接探讨信息传递格式对引用追踪的影响。

## 2. 核心主题与证据

尽管缺乏直接证据，但可从现有文献中提取与信息传递格式和引用追踪间接相关的主题：

**结构化信息提取与验证**：文献[1]描述了一个多阶段流水线系统，该系统使用OpenScholar（量化LLaMA 3.1 8B）对论文进行分类并提取结构化字段（如助推类型和目标行为），并通过JSON模式进行验证[1]。该研究在最佳配置下（标题/摘要/引言）实现了67.0%的F1分数和72.0%的召回率，而高精度变体（7次随机自一致性）实现了100%精度但仅12%召回率[1]。这表明结构化格式（JSON）在信息提取中可提供可调优的精度-召回权衡，但未涉及多智能体间的传递格式比较。

**多智能体系统挑战**：文献[4]指出多智能体学习系统面临增加采用学习系统复杂性的挑战[4]，但未具体说明信息传递格式的影响。

**AI系统用户交互**：文献[6]和[7]探讨了聊天机器人中的拟人化设计线索和用户依从性[6][7]，文献[8]系统综述了AI接受度因素[8]，但这些均聚焦于人机交互而非智能体间通信格式。

## 3. 证据支持的研究方向

基于现有证据，可识别以下与核心问题间接相关的研究方向：

- **结构化格式在单智能体信息提取中的有效性**：文献[1]表明JSON模式验证可提升信息提取的可靠性，但未在多智能体协作场景下验证[1]。
- **多智能体系统复杂性管理**：文献[4]提及学习系统复杂性挑战，暗示信息传递格式可能影响系统可扩展性[4]。
- **人机交互中的格式设计**：文献[6][7][8]显示交互设计（如拟人化）影响用户行为，但未涉及智能体间格式[6][7][8]。

## 4. 摘要级证据的局限

本合成面临显著局限性：

- **证据与问题不匹配**：所有8篇摘要均未直接研究“多智能体协作中角色间信息传递格式（JSON/Markdown）对下游引用追踪准确性的影响”。核心概念如“引用追踪准确性”在证据集中完全缺失。
- **摘要信息粒度不足**：摘要级证据仅提供高层概述，缺乏方法细节（如具体格式比较实验设计、引用追踪指标定义）[1][4]。
- **领域差异**：现有证据主要来自生物医学信息提取[1]、通信网络[2]、能源市场[5]和用户交互研究[6][7][8]，与多智能体协作信息传递格式的研究领域存在较大差距。
- **缺乏比较研究**：无任何文献比较JSON与Markdown或其他格式在智能体通信中的表现。

## 5. 谨慎结论

基于提供的摘要级证据集，无法得出关于“多智能体协作中角色间信息传递格式（JSON/Markdown）如何影响下游引用追踪准确性”的可靠结论。现有证据仅间接表明结构化格式（如JSON）在单智能体信息提取中具有潜在优势[1]，且多智能体系统面临复杂性挑战[4]，但缺乏直接比较或因果证据。建议未来研究应：1）设计专门实验比较JSON与Markdown等格式在多智能体引用追踪任务中的表现；2）开发引用追踪准确性的量化指标；3）在真实多智能体协作场景中验证格式影响。当前证据不足以支持任何实质性结论。

## 参考文献
[1] Identifying Evidence-Based Nudges in Biomedical Literature with Large Language Models. arXiv Preprint. 2026.
[2] 6G Wireless Networks: Vision, Requirements, Architecture, and Key Technologies. IEEE Vehicular Technology Magazine. 2019.
[3] ChatGPT: A comprehensive review on background, applications, key challenges, bias, ethics, limitations and future scope. Internet of Things and Cyber-Physical Systems. 2023.
[4] Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
[5] Electricity market design for the prosumer era. Nature Energy. 2016.
[6] AI-based chatbots in customer service and their effects on user compliance. Electronic Markets. 2020.
[7] Adoption of AI-based chatbots for hospitality and tourism. International Journal of Contemporary Hospitality Management. 2020.
[8] What factors contribute to the acceptance of artificial intelligence? A systematic review. Telematics and Informatics. 2022.