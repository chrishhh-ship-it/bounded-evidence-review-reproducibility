## 检索与筛选概览

本合成针对“自动化筛选决策替代人类双审者共识所需的最低审者间一致性阈值”这一研究问题，基于提供的8条摘要级证据进行单次综合。所涉文献涵盖2020至2026年间发表的研究，包括预印本、研究方案、数据分析和综述，主要聚焦于大型语言模型（LLMs）在系统综述筛选中的可靠性评估。其中，[1]、[3]、[4]直接报告了LLMs与人类审者间的一致性指标；[2]为评估自动化工具准确性的研究方案；[5]、[6]、[7]、[8]虽涉及共识方法或筛选流程，但未直接提供与自动化替代阈值相关的定量证据。

## 核心主题与证据

现有证据表明，LLMs在系统综述筛选中的表现尚不足以完全替代人类双审者共识，且尚未建立统一的替代阈值标准。

- **一致性阈值探索**：[1]提出以cGPT与人类共识的Cohen's kappa值落入人类-人类配对kappa的置信区间作为“实用阈值”，结果显示cGPT作为第二审者助理时kappa为0.733（95% CI: 0.607–0.859），落入人类-人类kappa范围0.713–0.784的置信区间内，但作为自主审者或第一审者助理时未达标。该研究同时指出，排除原因分类的kappa值（0.632）低于人类配对范围，且需要更多研究来建立标准化阈值[1]。

- **性能波动与条件依赖**：[4]采用“人不在回路”方法评估GPT-4，发现其准确性在高度平衡的数据集（约1:1）中表现极低，而在不平衡数据集（约1:3）中达到中等水平；全文本筛选在高度可靠提示下可达到“类人”水平，但总体建议谨慎使用[4]。类似地，[3]报告GPT-4在标题/摘要筛选中准确率为0.91，但强调其应作为辅助而非替代工具[3]。

- **研究方案中的阈值设定**：[2]计划在EPPI-Reviewer中采用20%和40%人工筛选阈值来评估优先排序筛选的准确性，但未预先定义可接受的替代阈值，且指出“最优准确性阈值仍不明确”[2]。

- **不相关证据**：[5]、[6]、[7]、[8]分别涉及创伤性脑损伤管理协议、ChatGPT教育影响、儿童乳突炎治疗及气候适应筛选协议，均未提供与自动化筛选替代阈值直接相关的定量数据。

## 证据支持的研究方向

基于现有摘要级证据，以下研究方向具有证据支持：

1. **建立标准化阈值框架**：[1]明确呼吁“需要更多研究来建立实用标准化阈值”，其提出的“kappa落入人类-人类置信区间”标准可作为初步框架，但需在不同数据集和任务中验证[1]。

2. **区分筛选阶段与角色**：证据表明LLMs在不同角色（自主审者、助理）和阶段（标题/摘要、全文本）表现差异显著[1][4]，未来研究应针对特定角色和任务定义阈值。

3. **平衡数据集与提示工程的影响**：[4]指出数据集平衡性和提示可靠性显著影响性能，阈值设定需考虑这些调节变量[4]。

4. **效率与准确性的权衡**：[1]报告cGPT可节省10.1–84.4小时，但准确性未达替代标准[1]；[3]强调效率提升的同时需保持“辅助而非替代”定位[3]。阈值应同时纳入时间成本与误筛风险。

## 摘要级证据的局限

本合成基于摘要级证据，存在以下固有局限：

- **缺乏全文本细节**：摘要未报告完整的混淆矩阵、灵敏度/特异度、或不同阈值下的操作特征曲线，无法精确界定“最低阈值”的具体数值[1][3][4]。
- **研究异质性**：各研究使用不同LLM版本（GPT-4、cGPT）、不同任务（标题/摘要 vs. 全文本）和不同一致性指标（kappa、准确率），难以直接比较[1][3][4]。
- **方案与结果混淆**：[2]为研究方案，尚未产生结果数据；[5]–[8]与核心问题无关，无法提供有效证据。
- **发表偏倚风险**：摘要可能选择性报告有利结果，如[3]报告高准确率但未提及假阴性率。

## 谨慎结论

基于现有摘要级证据，**目前尚无充分证据确定一个可普遍接受的、用于替代人类双审者共识的最低审者间一致性阈值**。现有研究提示，LLMs在特定角色（如第二审者助理）和条件下（如不平衡数据集、高度可靠提示）可达到与人类配对重叠的一致性水平（kappa约0.73），但作为自主替代工具时性能不足[1][4]。阈值设定需综合考虑筛选阶段、角色、数据集特征和效率需求，且标准化框架尚未建立[1][2]。因此，在获得更全面的全文本证据和验证性研究之前，自动化筛选决策应被视为人类审者的辅助手段，而非替代方案。

## 参考文献
[1] Evaluating the Reliability of a Custom GPT in Full-Text Screening of a Systematic Review. medRxiv. 2025.
[2] Study protocol for evaluating automation of systematic review processes with EPPI-Reviewer and Copilot 365 in updating the cataract evidence gap map. Systematic Reviews. 2026.
[3] Automated Paper Screening for Clinical Reviews Using Large Language Models: Data Analysis Study.. Journal of medical Internet research. 2024.
[4] Can large language models replace humans in systematic reviews? Evaluating GPT-4's efficacy in screening and extracting data from peer-reviewed and grey literature in multiple languages.. Research synthesis methods. 2024.
[5] Consensus-Based Management Protocol (CREVICE Protocol) for the Treatment of Severe Traumatic Brain Injury Based on Imaging and Clinical Examination for Use When Intracranial Pressure Monitoring Is Not Employed.. Journal of neurotrauma. 2020.
[6] What Is the Impact of ChatGPT on Education? A Rapid Review of the Literature. Education Sciences. 2023.
[7] A scoping review of the management of acute mastoiditis in children: What is the best approach?. The Turkish journal of pediatrics. 2023.
[8] The Global Adaptation Mapping Initiative (GAMI): Part 2 – Screening protocol. OpenAlex. 2021.