## 人工标注在智慧情报服务 benchmark 中应优先覆盖哪些维度？

### 1. 检索与筛选概览

本合成基于提供的8篇文献证据集（E_q），旨在回答“人工标注在智慧情报服务 benchmark 中应优先覆盖哪些维度”这一研究问题。所检索的文献涵盖2025—2026年间发表的多个benchmark研究，涉及深度研究（Deep Research）智能体评估、多智能体系统基准构建、以及特定领域（如安全运营、芯片设计、博弈游戏）的智能体能力测试。经过筛选，其中[1]、[2]、[5]、[8]直接讨论了人工标注在benchmark设计中的角色与维度要求，[3]、[6]、[7]虽涉及多智能体评估但未聚焦人工标注维度，[4]摘要信息不足。因此，本合成主要依据[1]、[2]、[5]、[8]展开分析。

### 2. 核心主题与证据

现有研究表明，人工标注在智慧情报服务benchmark中应优先覆盖以下核心维度：

**（1）事实依据与推理正确性（Factual Grounding & Reasoning Soundness）**  
[1]指出，在评估深度研究智能体时，人工标注需重点覆盖“事实依据（factual grounding）、推理正确性（reasoning soundness）和清晰度（clarity）”，并为此构建了2500余条专家编写的细粒度评分规则（rubrics）。[2]进一步强调，人工标注应涵盖“引文准确性与关联性（citation accuracy and association）”，以确保生成报告中的每个主张都有可靠的来源支撑。

**（2）覆盖度与呈现质量（Coverage & Presentation）**  
[2]提出，人工标注需评估报告在“覆盖度（coverage）、呈现质量（presentation）、一致性与分析深度（consistency and depth of analysis）”等方面的表现。这要求标注人员判断智能体是否全面覆盖了用户需求中的关键信息点，以及信息组织是否清晰、逻辑连贯。

**（3）用户中心性与任务明确性（User-Centricity & Unambiguity）**  
[2]明确提出了benchmark设计的四项原则，其中“用户中心性（user-centric）”和“无歧义性（unambiguous）”直接关联人工标注维度：标注需确保任务反映真实用户的信息需求，且任务描述在不同标注者之间具有一致的解读。这要求标注指南必须清晰定义任务边界和评估标准。

**（4）多视角归因与失败分析（Multi-Perspective Failure Attribution）**  
[8]引入“多视角失败归因（multi-perspective failure attribution）”概念，指出人工标注不应假设单一确定性根因，而应承认多智能体系统中失败原因的模糊性。该研究提出MP-Bench，要求标注人员从多个合理视角标注失败原因，这为智慧情报服务中复杂错误模式的标注提供了新维度。

**（5）动态性与搜索密集性（Dynamicity & Search-Intensiveness）**  
[2]强调，人工标注需覆盖任务对“动态信息（dynamic information）”和“大量网络搜索（search-intensive）”的要求。这意味着标注人员需判断智能体是否有效利用了实时信息源，以及是否进行了足够深入的多源信息检索与综合。

**（6）安全操作与蓝队能力（Security Operations & Blue Team Capabilities）**  
[5]针对安全运营中心（SOC）场景，提出人工标注应覆盖“蓝队任务（blue team tasks）”的多个维度，包括事件响应中的协调能力、多任务执行能力等。该研究虽未提供完整标注维度列表，但指出了现有benchmark在蓝队能力评估上的空白，暗示人工标注需优先覆盖此类实际应用场景。

### 3. 证据支持的研究方向

基于上述证据，人工标注在智慧情报服务benchmark中应优先覆盖以下研究方向：

- **细粒度评分规则构建**：如[1]所示，开发覆盖事实依据、推理正确性、清晰度的专家级rubrics，并确保其可操作性和一致性。
- **多维度质量评估框架**：整合[2]提出的覆盖度、呈现质量、引文准确性、分析深度等维度，形成系统化的标注协议。
- **动态信息处理能力标注**：针对[2]强调的“动态性”要求，设计标注任务以评估智能体对实时信息的获取与整合能力。
- **多视角失败归因标注**：借鉴[8]的方法，在标注指南中明确允许并鼓励标注者从多个合理视角解释失败原因，避免单一归因偏差。
- **领域特定能力标注**：如[5]所示，针对安全运营、芯片设计等垂直领域，开发专门的人工标注维度，覆盖领域特有的能力要求（如蓝队协调、工具调用等）。

### 4. 摘要级证据的局限

本合成所依赖的均为摘要级证据，存在以下局限：

- **细节缺失**：摘要无法提供完整的标注维度定义、评分标准示例或标注者间一致性数据。例如[1]虽提及“2500+条rubrics”，但未展示具体条目；[2]的“DeepEval”协议细节在摘要中不可见。
- **领域覆盖偏差**：现有证据集中于“深度研究”和“多智能体系统”领域，[3]、[6]、[7]分别涉及机器人协作、博弈游戏等场景，其标注维度可能不直接适用于智慧情报服务。
- **时效性与验证不足**：部分文献为预印本（如[5]、[8]），尚未经过同行评审；[4]的摘要信息过少，无法提取有效证据。
- **缺乏对比数据**：摘要未提供不同标注维度在实际评估中的效果对比（如哪些维度对最终评分影响最大），限制了优先级排序的依据。

### 5. 谨慎结论

综合现有摘要级证据，人工标注在智慧情报服务benchmark中应优先覆盖以下维度：**事实依据与推理正确性、覆盖度与呈现质量、用户中心性与任务明确性、多视角失败归因、动态性与搜索密集性、以及领域特定能力（如安全操作）**。这些维度分别来自[1]、[2]、[8]和[5]的研究，共同构成了评估智能体情报服务能力的核心框架。

然而，由于证据的摘要性质，上述结论需谨慎对待。实际标注维度的优先级可能因具体应用场景（如实时情报分析 vs. 历史报告生成）而显著不同。建议未来研究在完整文献基础上，通过实证比较不同维度对评估效度的影响，并开发统一的标注协议以提升跨benchmark的可比性。

## 参考文献
[1] ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents. arXiv.org. 2025.
[2] LiveResearchBench: A Live Benchmark for User-Centric Deep Research in the Wild. arXiv.org. 2025.
[3] Tool-RoCo: An Agent-as-Tool Self-organization Large Language Model Benchmark in Multi-robot Cooperation. arXiv.org. 2025.
[4] ASIC-Agent: An Autonomous Multi-Agent System for ASIC Design with Benchmark Evaluation. 2025 IEEE International Conference on LLM-Aided Design (ICLAD). 2025.
[5] Design Principles for the Construction of a Benchmark Evaluating Security Operation Capabilities of Multi-agent AI Systems. arXiv Preprint. 2026.
[6] Population-dependent agent performance in non-transitive games: a multi-agent Rock--Paper--Scissors benchmark. CrossRef. 2026.
[7] OpenGuanDan: A Large-Scale Imperfect Information Game Benchmark. arXiv.org. 2026.
[8] Rethinking Failure Attribution in Multi-Agent Systems: A Multi-Perspective Benchmark and Evaluation. arXiv Preprint. 2026.