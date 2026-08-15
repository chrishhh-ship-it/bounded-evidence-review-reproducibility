## 1. 检索与筛选概览

本合成基于提供的8条摘要级证据记录，围绕“为智慧情报服务设计 retrieval-evidence-writing 多阶段工作流”这一研究问题展开。所涉文献涵盖2024至2026年间的预印本、期刊论文及会议论文，来源包括arXiv、medRxiv、CrossRef及多个专业期刊。这些记录共同聚焦于检索增强生成（RAG）系统、多智能体架构、证据分级与验证机制，以及它们在事实核查、医学写作、临床决策支持等情报密集型任务中的应用。尽管部分记录（如[5]和[8]）仅提供标题或有限的摘要信息，但整体证据集仍为构建多阶段工作流提供了多角度的参考基础。

## 2. 核心主题与证据

多阶段工作流的核心理念在于将复杂的“检索-证据-写作”任务分解为若干可独立优化且相互衔接的子阶段。现有证据支持以下关键主题：

**（1）多智能体与模块化分解**：[3]提出了一种用于自动事实核查的多智能体系统，包含输入摄取代理（负责声明分解）、查询生成代理（制定子查询）、证据检索代理（获取可信证据）以及裁决预测代理（综合判断并生成可解释结论）。该系统在FEVEROUS等基准数据集上实现了12.3%的Macro F1分数提升，验证了将任务分解为多个专门化阶段的有效性。

**（2）证据分级与质量保障**：在医学情报领域，[6]开发的EBMChat系统整合了循证医学（EBM）工作流，通过Thought-Action-Observation（TAO）循环和记忆模块，实现了更优的证据层级（100%达到RCT级别或以上，对比基线仅17.5%）、更严格的证据时效性（5年内，对比基线可追溯至1980年代）以及更全面的检索量（中位数693条/问题，对比基线267条）。这表明多阶段工作流中应嵌入证据质量评估机制。

**（3）证据验证与隐私安全**：[4]提出的SEAL-Tag系统采用“验证后路由”（Verify-then-Route）范式，通过SEAL-Probe协议生成可验证的个人身份信息（PII）证据表（PET），并利用概率电路（PC）执行逻辑约束裁决。该系统在降低自适应泄露8倍以上的同时保持了语义效用，为写作阶段前的证据可信度检查提供了技术路径。

**（4）检索精度与时效性优化**：[7]的下一代证据（NGE）系统通过高精度文献检索过滤器，专门针对指南维护场景，在德国肿瘤学指南基准测试中展现出卓越的精确度，旨在缩短从研究发表到指南更新的平均延迟（当前为1.7-3.0年）。[1]的MedDiscover框架则强调通过广泛文献综述实现证据扎根的检索。

## 3. 证据支持的研究方向

基于现有证据，以下研究方向可为智慧情报服务的多阶段工作流设计提供支撑：

**方向一：多阶段流水线架构**。借鉴[3]的四代理分解模式，设计包含“查询分解→多源检索→证据筛选与分级→证据聚合→写作生成”的完整流水线。每个阶段可由专门模型或模块负责，并支持阶段间的反馈循环。

**方向二：证据质量与可信度评估模块**。整合[6]的EBM工作流原则（如证据层级、时效性、相关性）和[4]的验证协议（如PET表与概率电路），在检索与写作之间嵌入证据裁决环节，确保最终输出基于高质量、可验证的证据。

**方向三：多轮对话与上下文保持**。[6]的实验表明，EBMChat在45个多轮对话任务中成功率达93%，远超GPT-4.1插件的31%，这归因于其记忆模块和TAO循环。智慧情报服务常涉及迭代查询，因此工作流应支持跨轮次的状态维护与证据追溯。

**方向四：领域适配与隐私保护**。[1]强调领域特定RAG框架在代谢组学中的应用，[4]关注PII安全，[7]聚焦临床指南更新。这些案例提示工作流设计需考虑目标领域（如医学、金融、法律）的特定需求，包括术语体系、证据标准及合规要求。

## 4. 摘要级证据的局限

本合成完全依赖摘要级证据，存在以下固有局限：

- **细节缺失**：摘要无法提供完整的方法论细节（如检索算法参数、写作生成的具体策略、评估指标的计算方式），导致对工作流内部机制的推断受限。例如，[3]虽提及多智能体系统，但未说明代理间的通信协议或知识共享机制。
- **覆盖范围有限**：证据集仅包含8条记录，且部分记录（如[5]和[8]）仅提供标题或极简摘要，无法提取有效信息。这可能导致对某些关键主题（如写作阶段的文本生成策略）的支撑不足。
- **时效性与出版状态**：多数记录为2024-2026年的预印本（如[2]、[3]、[6]、[7]），尚未经过同行评审，其结论的稳健性和可复现性有待验证。
- **领域偏倚**：证据高度集中于医学/临床领域（[5]、[6]、[7]）和事实核查（[3]），对智慧情报服务在其他领域（如商业竞争情报、科技情报）的适用性讨论不足。

## 5. 谨慎结论

综合现有摘要级证据，为智慧情报服务设计 retrieval-evidence-writing 多阶段工作流具有明确的理论与实践基础。现有研究支持将任务分解为查询生成、多源检索、证据分级验证与写作生成等阶段，并强调嵌入证据质量评估、多轮对话保持及领域适配机制。然而，由于证据主要来自预印本且覆盖范围有限，上述结论应视为探索性假设而非确定性指南。未来研究需基于完整论文进行深入分析，并通过实证实验验证不同阶段组合与交互策略的有效性。建议在具体系统设计时，优先参考[3]的多智能体分解框架、[6]的EBM工作流原则以及[4]的验证协议，同时关注[7]在检索精度优化方面的经验。

## 参考文献
[1] MedDiscover: A Domain-Specific Retrieval-Augmented Generation Framework for Evidence-Grounded Knowledge Extraction in Metabolomics. Computational and Structural …. 2026.
[2] JARVIS: An Evidence-Grounded Retrieval System for Interpretable Deceptive Reviews Adjudication. arXiv preprint arXiv:2602.12941. 2026.
[3] Towards Robust Fact-Checking: A Multi-Agent System with Advanced Evidence Retrieval. arXiv Preprint. 2025.
[4] SEAL-Tag: Self-Tag Evidence Aggregation with Probabilistic Circuits for PII-Safe Retrieval-Augmented Generation. Semantic Scholar. 2026.
[5] Artificial Intelligence in Medical Writing: Is It an Exception to Evidence-Based Medicine?. JMA Journal. 2026.
[6] Augmenting Large Language Models and Retrieval-Augmented Generation with an Evidence-Based Medicine-Enabled Agent System. CrossRef. 2025.
[7] Next Generation Evidence: High-Precision Information Retrieval for Rapid Clinical Guideline Updates. medRxiv. 2024.
[8] HOW ARTIFICIAL INTELLIGENCE (AI) SUPPORTS UNDERGRADUATE STUDENTS’ ACADEMIC WRITING: EVIDENCE FROM INDONESIA. Prominent. 2024.