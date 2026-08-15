1. 检索与筛选概览

本合成基于给定的八篇摘要级证据记录（E_q），旨在探讨多智能体系统在处理包含过程导向与经验型气候模型、且具有不同不确定性结构的语料时，应如何管理引用。检索范围覆盖了2020年至2026年间发表的文献，涉及气候政策分析、多智能体系统设计、证据综合方法论以及社区适应评估等多个领域。筛选标准严格限定于E_q内提供的记录，未引入外部文献。最终纳入的八篇文献中，[2]、[3]、[4]、[6]、[7]直接探讨了多智能体系统的架构与应用，[1]、[5]、[8]则提供了气候政策、证据综合及社区适应方面的背景与框架。

2. 核心主题与证据

多智能体系统在处理复杂、异构信息源时展现出显著优势。例如，HACID-CSR系统通过监督智能体协调多个专业智能体，利用知识图谱检索增强生成（GraphRAG）来生成气候服务流程，从而提高了解决方案的多样性和可追溯性[2]。类似地，EBMChat系统整合了循证医学原则、记忆模块和思考-行动-观察循环，在临床问题回答中实现了89%的准确率，远超传统RAG方法[3]。AmpAgent系统则通过文献分析、数学推理和设备参数化三个智能体，成功将多级放大器的设计迭代次数减少了1.32至4倍[4]。这些案例表明，多智能体架构能够有效整合不同来源的知识，并处理结构化与非结构化数据。

然而，气候模型本身存在根本性的不确定性差异。过程导向模型（如CMIP系列）依赖于物理方程，而经验型模型则基于历史数据统计。现有文献指出，气候证据综合面临“证据金字塔”中层缺失的问题，即缺乏对气候解决方案在不同条件下有效性的严格综合[5]。此外，社区层面的适应评估强调分配公平、情境公平和程序公平，这要求多智能体系统在引用时不仅考虑模型的技术准确性，还需纳入社会脆弱性等非技术因素[8]。例如，纽约市的气候适应规划中，社区组织的参与和公平性考量是核心环节[8]，这与单纯依赖模型输出的过程导向方法形成对比。

3. 证据支持的研究方向

基于现有证据，未来研究可聚焦于以下方向：

- **不确定性感知的引用机制**：多智能体系统应能区分过程导向模型和经验型模型的不确定性结构。例如，在引用气候预测时，系统需明确标注模型类型及其置信度区间，类似于EBMChat中对证据时效性和等级的分类[3]。这要求系统具备元数据解析能力，以识别模型来源（如CORDEX、CMIP5）[2]。
- **公平性与情境化引用**：鉴于气候影响的不均匀分布[8]，多智能体系统在合成证据时需纳入社区层面的定性研究。例如，引用[8]中关于分配公平和程序公平的框架，确保引用不仅反映模型输出，还体现社会脆弱性指标。
- **跨领域证据整合**：现有系统如HACID-CSR已展示出整合知识图谱的能力[2]，但需进一步扩展至社会科学证据。例如，结合[5]中提出的定性证据综合方法，将政策文档（如[1]中提到的Overton数据）与模型输出进行交叉引用。

4. 摘要级证据的局限

本合成完全依赖摘要级证据，存在以下局限：首先，摘要可能省略了关键的方法论细节，例如多智能体系统如何处理模型间的冲突预测或不确定性传播。其次，部分文献（如[4]）专注于电路设计领域，其结论向气候模型合成的迁移性需谨慎验证。此外，[6]和[7]虽涉及多智能体系统，但未直接讨论气候模型的不确定性结构。最后，[8]的摘要存在文本不完整问题，可能遗漏了关于社区适应评估的关键结论。

5. 谨慎结论

多智能体系统在管理包含不同不确定性结构的气候模型语料时，具有通过分工协作提升证据综合质量的潜力。然而，现有文献尚未直接解决如何在同一系统中统一处理过程导向模型与经验型模型的引用问题。建议未来系统设计时，借鉴循证医学中的证据等级分类[3]和社区适应中的公平性框架[8]，开发专门的不确定性标注模块。同时，需警惕摘要级证据的局限性，并鼓励在完整文本层面进行验证。

## 参考文献
[1] How relevant is climate change research for climate change policy? An empirical analysis based on Overton data. arXiv Preprint. 2022.
[2] Climate Service Recipes: automatic multi-hazard climate information workflow generation using agentic Large Language Models (LLMs) and knowledge graphs. CrossRef. 2026.
[3] Augmenting Large Language Models and Retrieval-Augmented Generation with an Evidence-Based Medicine-Enabled Agent System. CrossRef. 2025.
[4] AmpAgent: An LLM-based Multi-Agent System for Multi-stage Amplifier Schematic Design from Literature for Process and Performance Porting. arXiv Preprint. 2024.
[5] Editorial: Evidence synthesis for accelerated learning on climate solutions. Campbell Systematic Reviews. 2020.
[6] Analysing the Role of Multi-Agent AI Models for Autonomous Business Decision Systems. Computing and Communication Workshop and Conference. 2026.
[7] A Dynamic and Adaptable Service Composition Architecture in the Cloud Based on a Multi-Agent System. International Journal of Information Technology and Web Engineering. 2018.
[8] New York City Panel on Climate Change 2019 Report Chapter 6: Community‐Based Assessments of Adaptation and Equity. Annals of the New York Academy of Sciences. 2019.