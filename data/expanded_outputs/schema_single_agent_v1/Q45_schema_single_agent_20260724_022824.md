# 摘要证据与全文证据冲突时，reviewer agent 应如何进行冲突处理与风险提示

## 1. 检索与筛选概览

本合成基于提供的8条摘要级证据记录，涵盖多智能体系统在文献综述自动化、空间文本到SQL转换、以及生物行为建模等领域的应用。其中，[1]和[8]直接涉及系统文献综述的多智能体工作流设计，[7]展示了多智能体框架在空间查询任务中的审校机制，而[2]-[6]则提供了审稿人视角下的公共评审证据。所有证据均来自摘要层面，未提供全文内容，这构成了本合成的主要信息边界。

## 2. 核心主题与证据

多智能体系统中的审校（reviewer）机制是当前研究的核心主题。[1]提出了一个对抗性多智能体系统，用于系统文献综述的“作者-审稿人”工作流，强调可验证证据和批评循环。该框架通过审稿人智能体对作者智能体生成的证据进行批判性审查，形成迭代改进机制。[8]则描述了LatteReview框架，采用两轮筛选流程：第一轮由两名初级审稿人智能体进行标题和摘要筛选，第二轮由更高级的审稿人智能体进行概念提取。这两个框架均体现了审稿人智能体在证据质量控制和信息提炼中的关键作用。

在空间查询领域，[7]展示了一个多智能体框架，包含“执行基础审校”阶段，通过审校环节将准确率从76.7%提升至87.7%。该研究明确表明，分解任务为专门但紧密耦合的智能体，并通过审校阶段进行纠错，能够显著提升系统鲁棒性，尤其对于空间敏感查询。

## 3. 证据支持的研究方向

基于现有摘要证据，可识别以下研究方向：

**方向一：多级审校工作流设计。** [8]提出的两轮审校机制（初级+高级审稿人）与[1]的对抗性批评循环形成互补。前者侧重筛选效率，后者侧重证据深度验证。两者结合可能构成更完整的冲突处理框架。

**方向二：审校阶段的纠错机制。** [7]的实验数据表明，审校阶段能够系统性地纠正错误，将准确率提升11个百分点。这一机制可类比于摘要证据与全文证据冲突时的风险识别与修正过程。

**方向三：审稿人智能体的层级分工。** [2]-[6]虽然来自不同领域，但均以“审稿人”身份提供公共评审，暗示了审稿人智能体可能承担从初步筛选到深度验证的多层次角色。

## 4. 摘要级证据的局限

本合成面临的核心局限在于所有证据均来自摘要层面，缺乏全文证据支持。具体表现为：

第一，[1]和[8]虽然描述了审稿人工作流，但未提供冲突处理的具体算法或决策规则。摘要中未说明当摘要证据与全文证据不一致时，审稿人智能体应如何判定优先级、如何量化冲突程度、以及如何生成风险提示。

第二，[7]的审校机制虽然展示了准确率提升，但未披露审校过程中如何处理证据层级冲突（如摘要与全文结论矛盾）的具体案例。

第三，[2]-[6]作为公共评审记录，其本身即为“审稿人”产出的摘要级证据，但未提供这些评审意见与原始全文证据之间的冲突案例或处理策略。

第四，所有证据均未涉及“风险提示”的具体形式——是概率性标注、置信度评分、还是人工复核标记？这些细节在摘要层面不可得。

## 5. 谨慎结论

基于现有摘要级证据，可以初步推断：多智能体系统中的审稿人智能体在处理证据冲突时，可能采用迭代批评循环[1]、多级筛选机制[8]和审校纠错阶段[7]等策略。然而，由于缺乏全文证据，关于冲突处理的具体规则（如证据优先级判定、冲突类型分类、风险量化方法）和风险提示的实现方式（如置信度阈值、人工复核触发条件）仍属未知。

建议未来的研究在全文层面明确以下内容：当摘要证据与全文证据冲突时，审稿人智能体应首先建立证据层级（如全文优于摘要、最新优于旧版），其次设计冲突检测算法（如语义相似度阈值、逻辑一致性校验），最后生成结构化风险提示（如“摘要声称X但全文显示Y，置信度降低至Z%”）。当前摘要级证据仅提供了框架雏形，尚不足以支撑具体的冲突处理协议设计。

## 参考文献
[1] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[2] Reviewer #2 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[3] Reviewer #1 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[4] Reviewer #1 (Public Review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[5] Reviewer #2 (Public review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[6] Reviewer #3 (Public Review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[7] From Questions to Queries: An AI-powered Multi-Agent Framework for Spatial Text-to-SQL. arXiv.org. 2025.
[8] LatteReview: a multi-agent framework for systematic review automation using large language models. arXiv preprint arXiv …. 2025.