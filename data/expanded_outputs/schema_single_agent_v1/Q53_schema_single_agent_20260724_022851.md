## 智能合成报告：Planner Agent 在写作前约束 Claim-Evidence 边界的必要性

### 1. 检索与筛选概览

本报告基于给定的8篇文献摘要级证据，围绕“planner agent 是否有必要独立存在，用于在写作前约束 claim-evidence 边界”这一研究问题展开合成。检索范围涵盖2025-2026年的多智能体系统相关研究，包括事实核查、代码生成、文献综述等应用场景。筛选标准聚焦于涉及智能体角色分工、规划-执行流程、以及证据与主张映射关系的文献。最终纳入的证据集中，[1][3][5][6][7][8]直接涉及多智能体系统中的规划、证据检索或主张验证功能，[2][4]虽涉及多智能体决策支持但与核心问题关联较弱，仅作为背景参考。

### 2. 核心主题与证据

**主题一：多智能体系统中规划角色的独立价值**

现有研究表明，在多智能体系统中设置独立的规划智能体（planner agent）能够显著提升系统性能与鲁棒性。[1]提出的事实核查系统包含专门的“Query Generation Agent”用于生成子查询，该角色实质承担了规划功能，将复杂主张分解为可检索的子问题，使系统在FEVEROUS等基准测试中实现12.3%的Macro F1-score提升。[3]则直接揭示了“planner-coder gap”问题，指出规划智能体将需求分解为不充分的计划，导致75.3%的代码生成失败，并证明通过多提示生成和监控智能体弥合这一鸿沟，可解决40.0%-88.9%的失败案例。这从反面论证了独立规划角色的必要性——若规划环节缺失或薄弱，将直接导致下游任务失败。

**主题二：规划角色在约束 claim-evidence 边界中的核心作用**

在证据与主张的映射过程中，规划智能体承担着关键的中介功能。[5]提出的FactReview系统将“claim extraction”与“literature positioning”相结合，通过规划环节明确主张与文献证据的对应关系。[6]指出当前科学主张验证系统“缺乏合成主张与证据之间的精确映射”，暗示需要专门的规划机制来建立这种映射。[7]提出的对抗性多智能体文献综述系统通过“author–reviewer workflows with verifiable evidence and critique loops”，实质上利用规划智能体在写作前设定证据边界，并通过批评循环持续约束。这些证据共同表明，独立的规划角色有助于在写作前明确哪些证据可以支持哪些主张，从而避免事后证据拼凑。

### 3. 证据支持的研究方向

基于上述证据，以下研究方向具有明确的文献支持：

**方向一：规划智能体的鲁棒性增强机制**

[3]的研究表明，规划智能体输出的不充分计划是系统失败的主因。未来可探索如何通过多提示生成、监控智能体反馈、或对抗性训练等方式提升规划质量，从而更有效地约束claim-evidence边界。

**方向二：证据-主张映射的形式化建模**

[5][6]均指出当前系统缺乏精确的映射机制。可借鉴[1]中的子查询生成方法，将复杂主张分解为可验证的子主张，并为每个子主张指定明确的证据检索策略，形成结构化的claim-evidence约束框架。

**方向三：规划与执行的协同优化**

[3]揭示的“planner-coder gap”表明，规划与执行之间的信息损失是系统性缺陷。可研究如何通过迭代规划、中间表示共享、或联合训练等方式，使规划智能体更好地理解下游执行能力，从而设定更合理的证据边界。

**方向四：面向文献综述的规划智能体设计**

[7][8]展示了规划智能体在文献综述中的应用潜力。[7]的对抗性工作流和[8]的提纲式摘要方法，为设计专门用于约束claim-evidence边界的规划智能体提供了具体范式。

### 4. 摘要级证据的局限

本合成基于摘要级证据，存在以下固有局限：

1. **信息粒度不足**：摘要无法提供具体的方法细节、实验设置和定量结果。例如[1]声称12.3%的提升，但无法判断其规划智能体与其他组件的具体交互机制；[3]虽揭示了75.3%的失败率，但无法获取其突变测试的具体操作定义。

2. **领域覆盖偏差**：现有证据主要来自事实核查（[1][5][6]）和代码生成（[3]）领域，缺乏直接针对学术写作场景的实证研究。将代码生成中的“planner-coder gap”类比到写作中的“planner-writer gap”需要谨慎验证。

3. **时间窗口限制**：证据集中于2025-2026年，可能遗漏更早的基础性研究。例如[2]（2016年）和[4]（2023年）虽涉及多智能体决策支持，但未直接讨论规划角色的必要性。

4. **摘要级证据的可靠性**：部分文献来自arXiv预印本（[1][5]）或未提供完整摘要（[2][4]），其结论可能未经同行评审验证。例如[1]的代码虽公开，但无法从摘要确认其方法的可复现性。

### 5. 谨慎结论

基于现有摘要级证据，可以得出以下谨慎结论：

1. **独立规划智能体具有必要性**：[1][3]的证据表明，在多智能体系统中设置专门的规划角色能够显著提升系统性能，而规划环节的薄弱直接导致下游任务失败。这一结论在事实核查和代码生成领域得到初步验证。

2. **规划智能体有助于约束 claim-evidence 边界**：[5][6][7]的证据显示，通过规划环节明确主张与证据的映射关系，可以避免事后证据拼凑，提升验证的精确性和可解释性。

3. **现有证据尚不充分**：由于领域覆盖偏差和摘要级信息的限制，无法断言在学术写作场景中独立规划智能体是绝对必要的。代码生成中的“planner-coder gap”与写作中的“claim-evidence mapping”虽有相似性，但本质差异（代码执行的可验证性 vs. 论证逻辑的主观性）需要进一步研究。

4. **建议研究方向**：未来应开展针对学术写作场景的实证研究，设计包含独立规划智能体的多智能体写作系统，并系统评估其对claim-evidence边界约束的有效性。同时，应借鉴[3]的鲁棒性测试方法，评估规划智能体在不同输入条件下的稳定性。

综上，现有证据初步支持“独立规划智能体在写作前约束claim-evidence边界具有必要性”这一假设，但需更多领域特定和全文级别的证据加以确认。

## 参考文献
[1] Towards Robust Fact-Checking: A Multi-Agent System with Advanced Evidence Retrieval. arXiv Preprint. 2025.
[2] A multi-agent system to support evidence based medicine and clinical decision making via data sharing and data privacy. Decision Support Systems. 2016.
[3] Understanding and Bridging the Planner-Coder Gap: A Systematic Study on the Robustness of Multi-Agent Systems for Code Generation. Semantic Scholar. 2025.
[4] Decision Support for Regeneration Mode of Old Community Under Multi-Agent Interaction: Evidence from China. CrossRef. 2023.
[5] FactReview: Evidence-Grounded Reviews with Literature Positioning and Execution-Based Claim Verification. arXiv preprint arXiv …. 2026.
[6] SciTrue: Evidence-Grounded Claim Verification in Science. Proceedings of the 19th Conference of …. 2026.
[7] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[8] ADMP-LS: Agent-Based Dialogue and Mining Platform for Evidence-Grounded QA, Extraction, and Literature Review in Life Science. … Conference on Data …. 2025.