# 小规模基准下统计显著性检验方法的学术证据合成

## 1. 检索与筛选概览

本合成基于提供的8篇文献证据集（E_q），旨在回应“在n=30的小规模基准上，如何通过统计检验方法合理声称配置间的显著性差异”这一研究查询。所涉文献涵盖人工智能教育应用[1]、检索增强生成技术[2]、多智能体轨迹预测[3]、协同生产调度[4]、性别暴力决定因素[5]、电商搜索决策支持[6]、小语言模型农业决策[7]以及生物医学多智能体系统[8]等多个领域。这些文献均以摘要级证据形式呈现，未提供具体的统计检验方法或小样本推断技术细节。文献发表年份从2019年至2026年，其中[6]和[8]为2026年预印本，[7]为2025年预印本。

## 2. 核心主题与证据

经分析，证据集中与“小规模基准统计检验”相关的核心主题可归纳为以下三点：

**（1）小样本评估在多个领域普遍存在。** 文献[7]明确报告了“使用30个问题”对小型语言模型进行第二阶段评估的实践，指出在计算受限环境下，小规模基准测试是筛选模型可行性的常用手段[7]。文献[4]在10×10的工件-机器场景中进行了仿真实验，其样本规模同样属于小规模范畴[4]。这表明n=30量级的基准测试在AI系统评估中具有现实需求。

**（2）现有文献普遍缺乏对小样本统计推断方法的明确描述。** 在8篇文献中，没有任何一篇提供关于小样本下显著性检验的具体方法（如置换检验、Wilcoxon符号秩检验、Bootstrap置信区间等）的详细说明。文献[2]作为系统综述，指出由于设计和指标的异质性，其自身未进行元分析[2]，这间接反映了小样本统计推断方法在RAG评估领域的缺失。文献[1]虽指出定量方法是实证研究中最常用的方法[1]，但未涉及小样本场景下的统计检验策略。

**（3）效果比较多基于绝对数值而非统计显著性。** 多数文献报告性能提升时采用百分比差值，如文献[3]报告“超过30%”和“15%”的性能提升[3]，文献[6]报告“30%的转化率激增”[6]，文献[8]报告准确率从30.3%提升至87.2%[8]。这些报告方式均未提供置信区间或p值，表明当前实践倾向于使用点估计而非统计推断来声称差异。

## 3. 证据支持的研究方向

基于上述证据，可识别出以下值得探索的研究方向：

**（1）小样本统计检验方法的系统化应用。** 鉴于n=30基准在多个领域（如SLM评估[7]、生产调度仿真[4]）的实际使用，亟需建立适用于该样本量的统计检验协议。可借鉴文献[2]所倡导的“整体基准”理念[2]，将统计显著性检验纳入评估标准。

**（2）效应量与置信区间的标准化报告。** 当前文献普遍报告绝对性能提升[3][6][8]，但缺乏不确定性量化。未来研究应推动在小样本场景下报告效应量（如Cohen's d）及其Bootstrap置信区间，以替代简单的点估计比较。

**（3）置换检验与重抽样方法的推广。** 对于n=30的非参数场景，置换检验和Bootstrap方法无需正态性假设，适合作为默认统计推断工具。文献[7]中30个问题的评估设计[7]恰好满足置换检验的最小样本需求。

## 4. 摘要级证据的局限

本合成受限于摘要级证据的固有缺陷，需明确以下局限：

**（1）方法细节缺失。** 所有8篇文献的摘要均未提供统计检验的具体方法、假设条件或软件实现。例如，文献[7]虽使用30个问题评估模型[7]，但未说明是否进行了多重比较校正或效应量计算。文献[4]的仿真实验[4]也未报告结果的变异性度量。

**（2）领域异质性限制直接迁移。** 证据涵盖教育[1]、交通[3]、农业[7]、生物医学[8]等多个领域，各领域对小样本统计检验的惯例和标准存在差异。例如，文献[5]的性别暴力研究使用横断面调查[5]，其统计方法与AI系统评估的A/B测试[6]截然不同。

**（3）缺乏对统计检验效力的讨论。** 没有任何文献讨论n=30样本量下的统计检验力（power）问题。根据统计常识，该样本量下检测中等效应量（d=0.5）的检验力通常不足0.5，但摘要证据中未涉及这一关键考量。

## 5. 谨慎结论

基于现有摘要级证据，针对“在n=30的小规模基准上合理声称配置间显著性差异”的问题，可得出以下谨慎结论：

第一，n=30的小规模基准在AI系统评估中确实存在且具有实际应用价值，文献[7]和[4]提供了直接例证[7][4]。然而，当前文献普遍缺乏对小样本统计推断方法的明确使用和报告。

第二，为合理声称显著性差异，研究者应避免仅依赖点估计比较（如“提升30%”[3][6]），而应采用适用于小样本的非参数统计方法。具体建议包括：（1）使用置换检验或Wilcoxon符号秩检验进行配对比较；（2）报告Bootstrap百分位置信区间（建议2000次重抽样）；（3）计算并报告效应量（如Cohen's d或Cliff's delta）；（4）对多重比较进行Bonferroni或FDR校正。

第三，鉴于摘要级证据的方法论空白，本结论的可靠性受限于文献的抽象层级。建议未来研究在全文层面系统梳理小样本统计检验在AI评估中的应用现状，并制定领域特定的报告指南，正如文献[2]所呼吁的“整体基准”[2]和文献[1]所强调的“定量方法”[1]的规范化应用。

## 参考文献
[1] Systematic review of research on artificial intelligence applications in higher education – where are the educators?. International Journal of Educational Technology in Higher Education. 2019.
[2] A Systematic Literature Review of Retrieval-Augmented Generation: Techniques, Metrics, and Challenges. Big Data and Cognitive Computing. 2025.
[3] Knowledge-Informed Multi-Agent Trajectory Prediction at Signalized Intersections for Infrastructure-to-Everything. IEEE transactions on intelligent transportation systems (Print). 2025.
[4] A cross-enterprise collaborative production scheduling decision support algorithm with multi-agent support. Applied Mathematics and Nonlinear Sciences. 2024.
[5] Determinants of Gender-Based Violence in Nepal: A Review of Recent Evidence. NPRC Journal of Multidisciplinary Research. 2025.
[6] CogSearch: A Cognitive-Aligned Multi-Agent Framework for Proactive Decision Support in E-Commerce Search. arXiv Preprint. 2026.
[7] Evaluating Small Language Models for Agentic On-Farm Decision Support Systems. arXiv Preprint. 2025.
[8] A Review of Multi-Agent AI Systems for Biological and Clinical Data Analysis.. Methods and protocols. 2026.