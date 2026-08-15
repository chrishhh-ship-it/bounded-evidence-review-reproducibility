## 检索与筛选概览

本合成基于提供的8条摘要级证据记录，旨在探讨在API预算固定的条件下，优先增加评审（reviewer）轮次还是优先扩大检索证据池更划算。经筛选，与查询直接相关的证据包括[1]关于LLM代理在API任务中评估框架的研究、[2]关于对抗性多代理系统用于系统文献综述的论文、以及[3]关于自动化系统评价流程（含EPPI-Reviewer和Copilot 365）的研究方案。其余记录[4][5][6][7][8]涉及蝙蝠群体涌现建模、秀丽隐杆线虫成像及TRPM亚家族冷却剂结合口袋等不相关主题，未纳入核心分析。

## 核心主题与证据

现有证据并未直接比较“增加评审轮次”与“扩大检索证据池”的成本效益，但提供了相关框架与流程的间接信息。[1]提出了Agent-Diff基准框架，用于评估LLM代理在企业API任务中的表现，该框架通过状态差异合约和容器化API副本实现可控评估，并指出代理性能受模型、工具访问、提示结构和代理框架差异的影响。该研究通过消融实验评估了API文档访问对基准性能的贡献，暗示了证据池（如文档）对代理任务成功的重要性。[2]描述了对抗性多代理系统，其中包含作者-评审者工作流与可验证证据和批评循环，表明多轮评审机制在系统文献综述中具有结构化作用。[3]则聚焦于自动化系统评价流程，比较了EPPI-Reviewer的优先筛选（PS）与Copilot 365在不同阶段的准确性和效率，其中PS使用了20%和40%的人工筛选阈值，并计算了优先排序的相关参考文献比例及遗漏的相关引文数量，这直接涉及检索证据池规模（筛选阈值）对结果的影响。

## 证据支持的研究方向

基于现有证据，可识别以下研究方向：第一，[1]中Agent-Diff框架的消融实验表明，API文档（证据池的一部分）的访问对代理性能有贡献，但未量化其与评审轮次（如多轮反馈）的边际效益对比。第二，[3]中关于优先筛选阈值的实验（20% vs 40%）提供了证据池规模对遗漏率影响的初步数据，但未涉及评审轮次变量。第三，[2]中的对抗性多代理系统暗示了多轮评审可能提升证据质量，但缺乏与扩大检索范围的直接比较。因此，未来研究需设计对照实验，在固定API预算下，系统性地变化评审轮次（如1轮 vs 3轮）和检索证据池规模（如不同筛选阈值或文档数量），并测量任务成功率、时间成本及资源消耗。

## 摘要级证据的局限

本合成所依赖的摘要级证据存在显著局限。首先，所有记录均为摘要或简短描述，缺乏完整的方法学细节、定量结果和成本数据，无法直接计算“划算”程度。例如，[1]虽提及消融实验，但未报告具体性能差异数值；[3]虽描述了筛选阈值，但未提供最终准确率或时间节省的完整数据。其次，[2][4][5][6][7][8]的摘要内容过于简略，甚至仅包含标题，无法提取有效证据。最后，证据来源多样（arXiv预印本、CrossRef、期刊），但缺乏对预算约束下资源分配策略的直接实证研究，导致结论需高度谨慎。

## 谨慎结论

在现有摘要级证据基础上，无法得出关于“优先增加评审轮次还是优先扩大检索证据池更划算”的明确结论。间接证据表明：扩大检索证据池（如提高筛选阈值或增加API文档访问）可能提升任务覆盖率[1][3]，而增加评审轮次（如对抗性多代理系统中的批评循环）可能增强证据验证[2]。然而，由于缺乏直接比较实验和成本效益数据，任何推荐均属推测。建议在固定API预算下开展实证研究，系统评估两种策略的边际收益，并考虑任务类型（如简单API调用 vs 复杂文献综述）的调节作用。

## 参考文献
[1] Agent-Diff: Benchmarking LLM Agents on Enterprise API Tasks via Code Execution with State-Diff-Based Evaluation. arXiv Preprint. 2026.
[2] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[3] Study protocol for evaluating automation of systematic review processes with EPPI-Reviewer and Copilot 365 in updating the cataract evidence gap map. Systematic Reviews. 2026.
[4] Reviewer #2 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[5] Reviewer #1 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[6] Reviewer #2 (Public review): SICKO: Systematic Imaging of Caenorhabditis Killing Organisms. CrossRef. 2025.
[7] Reviewer #1 (Public review): SICKO: Systematic Imaging of Caenorhabditis Killing Organisms. CrossRef. 2025.
[8] Reviewer #1 (Public Review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.