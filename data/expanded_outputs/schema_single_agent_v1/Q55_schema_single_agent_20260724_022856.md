## 检索与筛选概览

本合成基于提供的8条摘要级证据记录，旨在回答“在API预算固定时，优先增加评审轮次还是优先扩大检索证据池更划算”这一研究问题。经检索，E_q中包含的证据记录主要涉及以下内容：一项关于LLM代理在API任务中性能评估的基准框架研究[1]；一项关于对抗性多代理系统用于系统文献综述中作者-评审工作流的研究[2]；一项关于利用EPPI-Reviewer和Copilot 365自动化系统综述过程的研究方案[3]；以及若干与蝙蝠群体涌现建模[4][5]、秀丽隐杆线虫成像[6][7]和TRPM亚家族冷却剂结合口袋[8]相关的评审意见。这些记录中，仅[1]、[2]和[3]与代理系统、评审流程或检索效率直接相关，其余记录[4]-[8]主题偏离，无法为研究问题提供直接证据。

## 核心主题与证据

现有证据主要围绕代理系统在API任务和文献综述中的性能优化展开，但缺乏直接比较“增加评审轮次”与“扩大检索证据池”成本效益的实证研究。

- **代理系统性能评估**：Agent-Diff框架[1]通过代码执行和状态差异评估，研究了LLM代理在真实企业API任务中的表现。该框架关注模型、工具访问、提示结构和代理框架对性能的影响，并指出基准测试需要在沙盒控制与生态效度之间权衡[1]。然而，该研究未涉及评审轮次或检索池规模的预算分配问题。

- **多代理评审工作流**：一项研究提出了对抗性多代理系统，用于系统文献综述中的作者-评审工作流，包含可验证证据和批评循环[2]。这暗示了增加评审轮次可能提升证据质量，但未提供与扩大检索池的成本比较。

- **自动化筛选阈值**：一项研究方案评估了EPPI-Reviewer中优先筛选（PS）的准确性，使用20%和40%的人工筛选阈值，并计算优先筛选所遗漏的相关引用比例[3]。这表明扩大检索池（即提高筛选阈值）可能增加召回率，但会带来遗漏风险，且未与增加评审轮次进行对比。

## 证据支持的研究方向

基于现有证据，可识别出以下潜在研究方向，但均需进一步实证验证：

1. **评审轮次与证据质量的权衡**：对抗性多代理系统中的批评循环[2]提示，增加评审轮次可能通过迭代验证提升证据可靠性，但其边际效益需与扩大检索池带来的召回率提升进行比较。

2. **检索池规模与遗漏风险**：EPPI-Reviewer的优先筛选实验[3]表明，扩大检索池（如从20%到40%阈值）可能减少遗漏，但会消耗更多预算。该研究未量化不同阈值下的成本效益比。

3. **代理系统在API任务中的资源分配**：Agent-Diff框架[1]强调基准测试中沙盒控制与生态效度的权衡，这间接提示在固定预算下，资源分配（如增加API调用轮次 vs. 扩大检索范围）可能影响任务成功率，但无直接证据。

## 摘要级证据的局限

本合成面临显著局限：

- **主题相关性不足**：E_q中多数记录[4]-[8]与代理系统或文献综述无关，无法为研究问题提供任何证据。这些记录涉及蝙蝠行为建模、线虫成像和蛋白质结构，属于完全不同的领域。

- **缺乏直接比较数据**：即使相关记录[1][2][3]，也未直接比较“增加评审轮次”与“扩大检索证据池”的成本效益。证据仅提供孤立视角，如代理性能评估[1]、评审工作流设计[2]或筛选阈值设定[3]，但未在同一框架下进行预算分配实验。

- **摘要级信息深度有限**：所有证据均为摘要级，缺乏方法细节、定量结果或成本数据。例如，[3]仅描述研究方案，未报告实际成本或效率指标；[2]未说明批评循环的具体轮次与资源消耗。

## 谨慎结论

基于当前E_q中的摘要级证据，无法得出关于“固定API预算下优先增加评审轮次还是优先扩大检索证据池更划算”的明确结论。现有证据仅间接提示：增加评审轮次可能通过迭代验证提升证据可靠性[2]，而扩大检索池可能减少遗漏但增加成本[3]。然而，这些发现来自不同研究背景，缺乏直接比较。在获得更具体的实证数据（如同一任务下不同预算分配的边际效益实验）之前，任何关于“更划算”的判断均属推测。建议未来研究在统一框架（如Agent-Diff[1]）中系统比较这两种策略的成本效益。

## 参考文献
[1] Agent-Diff: Benchmarking LLM Agents on Enterprise API Tasks via Code Execution with State-Diff-Based Evaluation. arXiv Preprint. 2026.
[2] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[3] Study protocol for evaluating automation of systematic review processes with EPPI-Reviewer and Copilot 365 in updating the cataract evidence gap map. Systematic Reviews. 2026.
[4] Reviewer #2 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[5] Reviewer #1 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[6] Reviewer #2 (Public review): SICKO: Systematic Imaging of Caenorhabditis Killing Organisms. CrossRef. 2025.
[7] Reviewer #1 (Public review): SICKO: Systematic Imaging of Caenorhabditis Killing Organisms. CrossRef. 2025.
[8] Reviewer #1 (Public Review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.