## 1. 检索与筛选概览

本合成基于提供的8篇摘要级证据，聚焦于“benchmark跨领域扩展时，哪些query应保留为领域无关核心题型”这一研究问题。检索到的文献覆盖了医疗AI问答[1]、任务导向数据集搜索[2]、深度研究代理评估[3][4]、多机器人协作[5]、ASIC设计[6]、信息检索[7]以及网络安全蓝队能力[8]等多个领域。这些文献均涉及benchmark构建或query设计，但直接讨论“跨领域核心题型保留”的文献较少。筛选后，主要依据[3][4][8]中提出的benchmark设计原则和任务分类框架进行合成。

## 2. 核心主题与证据

现有benchmark研究揭示了若干可跨领域保留的领域无关核心题型特征。首先，**多步推理与跨文档综合**是深度研究（Deep Research）任务的核心能力，要求query具备概念广度、逻辑嵌套和探索性[3]。LiveResearchBench进一步强调，跨领域query应满足**用户中心性、动态性、无歧义性、多面性与搜索密集性**四大原则[4]。其次，**工具使用与自主协调**是评估多智能体系统的基础能力，Tool-RoCo通过集中式/去中心化协作、自组织等范式，考察智能体在工具调用中的自主性[5]。此外，**证据检索与事实一致性**在医疗QA[1]和数据集搜索[2]中被视为关键，要求query能触发对最新文献的检索和结构化解释。最后，**安全与偏见检测**作为跨领域通用需求，在医疗[1]和网络安全[8]benchmark中均有体现，涉及不确定性评分、偏见分析和蓝队操作能力评估。

## 3. 证据支持的研究方向

基于上述证据，可识别出以下应保留为领域无关核心题型的query方向：

- **多步推理与综合型query**：要求代理进行概念广度、逻辑嵌套和探索性操作，如ResearchRubrics中定义的复杂任务[3]。
- **动态信息检索型query**：需实时搜索并综合数百个网络来源，超越参数化知识，如LiveResearchBench中的任务[4]。
- **工具调用与自主协调型query**：评估代理在集中式/去中心化协作中的工具选择与激活能力，如Tool-RoCo中的协作工具使用[5]。
- **证据检索与事实核查型query**：要求代理检索并引用最新文献，如医疗QA中的PubMed检索[1]和数据集搜索中的知识图谱构建[2]。
- **安全与偏见检测型query**：涉及不确定性评估、偏见分析和蓝队操作，如医疗QA中的LIME/SHAP分析[1]和SOC-bench中的蓝队任务[8]。

这些题型在多个领域benchmark中均有对应，具备跨领域迁移潜力。

## 4. 摘要级证据的局限

本合成仅依赖摘要级证据，存在以下局限：首先，摘要信息有限，无法获取各benchmark的具体query示例、评估指标和任务分类细节，例如ResearchRubrics的复杂度框架[3]和LiveResearchBench的100个任务[4]的具体内容。其次，部分文献（如[6]）摘要缺失，无法提取有效信息。此外，摘要级证据未提供跨领域验证的实证结果，例如同一query在不同领域benchmark上的表现对比。最后，现有文献多聚焦于特定领域（医疗、机器人、网络安全），缺乏对通用核心题型的系统性归纳，本合成需基于间接证据进行推断。

## 5. 谨慎结论

综合现有证据，跨领域benchmark扩展时应保留的核心题型包括：多步推理与综合型query、动态信息检索型query、工具调用与自主协调型query、证据检索与事实核查型query，以及安全与偏见检测型query。这些题型在多个领域benchmark中均有体现，且符合用户中心性、动态性、无歧义性和多面性等通用设计原则[4]。然而，由于摘要级证据的局限，上述结论需通过全文本分析和跨领域实证研究进一步验证。未来工作应系统收集各benchmark的完整query集，并测试其在医疗、机器人、网络安全等领域的迁移效果。

## 参考文献
[1] A Multi-Agent Framework for Medical AI: Leveraging Fine-Tuned GPT, LLaMA, and DeepSeek R1 for Evidence-Based and Bias-Aware Clinical Query Processing. arXiv Preprint. 2026.
[2] Revisiting Task-Oriented Dataset Search in the Era of Large Language Models: Challenges, Benchmark, and Solution. arXiv.org. 2025.
[3] ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents. arXiv.org. 2025.
[4] LiveResearchBench: A Live Benchmark for User-Centric Deep Research in the Wild. arXiv.org. 2025.
[5] Tool-RoCo: An Agent-as-Tool Self-organization Large Language Model Benchmark in Multi-robot Cooperation. arXiv.org. 2025.
[6] ASIC-Agent: An Autonomous Multi-Agent System for ASIC Design with Benchmark Evaluation. 2025 IEEE International Conference on LLM-Aided Design (ICLAD). 2025.
[7] Multi-Agent-Based Information Retrieval System Using Information Scent in Query Log Mining for Effective Web Search. Information Retrieval and Management. 2018.
[8] Design Principles for the Construction of a Benchmark Evaluating Security Operation Capabilities of Multi-agent AI Systems. arXiv Preprint. 2026.