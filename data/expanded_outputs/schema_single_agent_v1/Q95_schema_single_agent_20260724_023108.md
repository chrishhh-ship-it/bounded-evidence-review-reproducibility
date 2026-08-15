# 多智能体协作中角色间信息传递格式对下游引用追踪准确性的影响：基于摘要级证据的合成分析

## 1. 检索与筛选概览

本合成基于给定的八篇摘要级证据记录（[1]–[8]），旨在探讨多智能体协作中角色间信息传递格式（JSON/Markdown）如何影响下游引用追踪的准确性。然而，经审查发现，所提供的证据集中没有任何一篇直接研究信息传递格式与引用追踪准确性的关系。证据覆盖的主题包括：基于大语言模型的生物医学文献证据提取系统[1]、6G无线网络架构[2]、ChatGPT的综合评述[3]、多智能体系统综述[4]、产消者电力市场设计[5]、AI聊天机器人用户依从性[6]、旅游行业聊天机器人采纳[7]以及AI技术接受因素的系统综述[8]。其中，[1]和[4]与多智能体协作或结构化信息处理存在部分关联，但均未涉及引用追踪准确性的量化评估。

## 2. 核心主题与证据

尽管缺乏直接证据，但可从相关文献中提取间接线索。首先，[1]描述了一个多阶段管道系统，该系统使用OpenScholar（量化LLaMA 3.1 8B）对论文进行分类并提取结构化字段（如助推类型和目标行为），且验证过程基于JSON模式[1]。该研究评估了四种配置，最佳配置（标题/摘要/引言）达到67.0%的F1分数和72.0%的召回率，而高精度变体（7次随机自一致性）实现了100%的精确度但召回率仅为12%[1]。这表明结构化格式（JSON）在信息提取中可提供可调的性能权衡，但该研究未追踪引用来源的准确性。

其次，[4]指出多智能体学习系统面临增加复杂性的挑战，但未具体讨论信息传递格式[4]。其他文献涉及AI系统与用户交互的格式问题：[6]探讨了聊天机器人中语言拟人化设计线索对用户依从性的影响，发现拟人化和社会存在感显著提高依从可能性[6]；[7]则指出感知智能和拟人化是聊天机器人采纳意向的预测因子[7]。这些研究暗示信息呈现格式可能影响下游任务效果，但未涉及引用追踪。

## 3. 证据支持的研究方向

基于现有证据，可识别以下潜在研究方向：

（1）**结构化格式与信息提取性能的关系**：[1]中JSON模式验证的成功表明，结构化格式可能提升信息提取的一致性和可验证性，但该研究未将其与引用追踪准确性直接关联。

（2）**多智能体系统中的通信挑战**：[4]提及多智能体学习系统的复杂性，暗示信息传递格式可能是影响系统性能的关键因素之一，但缺乏实证支持。

（3）**用户对AI系统输出格式的响应**：[6][7][8]表明信息呈现方式（如拟人化程度、界面设计）显著影响用户行为，这间接提示格式选择可能影响下游任务（包括引用追踪）的准确性。

## 4. 摘要级证据的局限

本合成面临显著的方法论局限。首先，所有证据均来自摘要级别，缺乏全文细节，无法确认各研究是否涉及信息传递格式与引用追踪的因果分析。其次，证据集存在主题不匹配：核心研究问题涉及多智能体协作、信息传递格式（JSON/Markdown）和引用追踪准确性三个要素，但现有证据仅覆盖其中部分要素的碎片化信息。例如，[1]虽涉及JSON格式和系统评估，但评估指标（F1、召回率、精确度）针对的是助推类型识别而非引用追踪；[4]虽讨论多智能体系统，但未涉及具体格式或追踪指标。第三，证据来源时间跨度大（2016–2026），且包含非同行评审预印本[1]，证据质量参差不齐。

## 5. 谨慎结论

基于现有摘要级证据，无法得出关于“多智能体协作中角色间信息传递格式（JSON/Markdown）如何影响下游引用追踪准确性”的可靠结论。现有证据仅提供间接线索：结构化格式（如JSON）在信息提取任务中表现出可调的性能权衡[1]，多智能体系统面临通信复杂性挑战[4]，以及信息呈现格式影响用户行为[6][7][8]。然而，这些发现均未直接验证信息传递格式与引用追踪准确性的因果关系。要回答该研究问题，需要设计专门实验，比较JSON与Markdown格式在多智能体协作场景下对引用来源识别、归因和追踪准确性的影响，并控制任务复杂度、智能体数量等变量。当前证据不足以支持任何方向性的结论。

## 参考文献
[1] Identifying Evidence-Based Nudges in Biomedical Literature with Large Language Models. arXiv Preprint. 2026.
[2] 6G Wireless Networks: Vision, Requirements, Architecture, and Key Technologies. IEEE Vehicular Technology Magazine. 2019.
[3] ChatGPT: A comprehensive review on background, applications, key challenges, bias, ethics, limitations and future scope. Internet of Things and Cyber-Physical Systems. 2023.
[4] Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
[5] Electricity market design for the prosumer era. Nature Energy. 2016.
[6] AI-based chatbots in customer service and their effects on user compliance. Electronic Markets. 2020.
[7] Adoption of AI-based chatbots for hospitality and tourism. International Journal of Contemporary Hospitality Management. 2020.
[8] What factors contribute to the acceptance of artificial intelligence? A systematic review. Telematics and Informatics. 2022.