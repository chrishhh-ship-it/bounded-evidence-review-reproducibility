# 中文智能综合报告：数字工具与大型语言模型在分析结果冲突时的引用与比较方法

## 1. 检索与筛选概览

本综合基于提供的八篇摘要级证据文献，涵盖2023至2025年间发表的研究。这些文献涉及大型语言模型（LLMs）在医学信息检索、学术出版、供应链管理中的应用[1][2][3]，数字人文工具的发展[5]，系统综述与叙述性综述的方法论比较[8]，以及网络可访问性评估工具的系统综述[7]。此外，还包括两项与核心主题间接相关的实证研究：蚊虫控制对生态系统影响的系统综述[4]和尼罗河三角洲古景观的GIS分析[6]。所有文献均来自同行评审期刊或国际会议论文集。

## 2. 核心主题与证据

**2.1 数字工具与LLMs的局限性**

多项证据表明，当前LLMs（如ChatGPT）在生成准确、可验证的信息方面存在显著局限。ChatGPT倾向于生成“听起来可信但虚构的回应”，即所谓的“幻觉”现象，且无法忠实引用来源以供验证[1]。其使用的数据仅更新至2021年，对于依赖最新进展的领域存在“一年以上的信息差距”[2]。在医学研究中，ChatGPT生成的摘要仅有68%能被人类评审者正确识别为AI生成[2]，这增加了识别虚假信息的难度。

**2.2 工具比较的方法论挑战**

在数字人文和文本分析领域，不同工具可能对同一语料产生冲突的分析结果。系统综述[7]指出，传统自动化工具如WAVE和AChecker在解决语义和结构可访问性问题方面仍占主导地位但存在不足，而LLMs在增强上下文分析和语义解释方面显示出潜力，但尚处于早期阶段。这暗示了工具间结果冲突的普遍性。

**2.3 系统综述与叙述性综述的层级争议**

文献[8]挑战了“系统综述优于叙述性综述”的假设层级，指出系统综述的“系统性”并不等同于“高质量”。系统综述侧重于“概率性真理”，通过严格的方法论流程提取和汇总数据；而叙述性综述处理的是“似然真理”，依赖专家判断和解释性理解[8]。两者应被视为互补而非竞争关系，因为不同问题类型需要不同的综述方法。

**2.4 LLMs在特定领域的应用潜力与风险**

在制药供应链管理中，LLMs可用于知识管理、数据分析、流程自动化和文本摘要，但其预测能力受限于历史数据，无法预测“黑天鹅事件”（如战争、自然灾害）[3]。LLMs的输出质量高度依赖于提示词（prompt）的设计，且存在数据隐私、模型可靠性、幻觉和伦理问题等挑战[3]。

## 3. 证据支持的研究方向

**3.1 检索-摘要-验证范式**

文献[1]提出将LLMs与传统文献搜索引擎结合的“检索、摘要、验证”范式，以利用LLMs的摘要能力同时降低使用虚假信息的风险。这一范式可推广至数字工具的比较研究：当不同工具产生冲突结果时，研究者应首先检索原始数据，然后利用工具进行摘要分析，最后通过人工或自动化方法验证结果。

**3.2 混合评估框架**

针对网络可访问性评估，文献[7]呼吁开发“AI集成、包容性强、上下文感知的框架”，以弥合技术合规性与实际可用性之间的差距。类似地，在比较Voyant、NLTK和spaCy等文本分析工具时，应采用结合自动化工具、专家评审和用户参与的混合方法，以获得更全面的见解。

**3.3 方法论透明性与批判性反思**

文献[8]强调，无论采用何种综述方法，研究者都应透明地报告其选择过程、视角和解释方法。在引用和比较产生冲突结果的工具时，研究者应明确说明每个工具的技术假设、适用场景和局限性，避免将某一工具的结果视为绝对真理。

**3.4 人机协作与持续验证**

多项证据强调人类监督的重要性。LLMs应被视为“副驾驶”而非替代品[3]，其输出必须经过验证[1]。在学术研究中，AI工具可用于编辑和校对，但涉及专业知识或创新思想的任务仍需人类参与[2]。

## 4. 摘要级证据的局限

本综合仅基于摘要级证据，存在以下局限：

- **信息深度不足**：摘要无法提供方法细节、数据来源和完整结果，例如文献[4]和[6]与核心主题的关联性较弱，其摘要未直接涉及数字工具比较。
- **时效性差异**：文献[1][2]发表于2023年，而LLM技术发展迅速，部分结论可能已过时。
- **领域特异性**：多数证据来自医学领域[1][2][3][8]，其结论向数字人文工具比较的推广需谨慎。
- **缺乏直接证据**：现有摘要未直接讨论Voyant、NLTK和spaCy等具体工具的比较方法，本综合需基于间接证据进行推断。

## 5. 谨慎结论

基于现有摘要级证据，研究者应遵循以下原则引用和比较产生冲突结果的数字工具：

1. **透明报告工具选择与假设**：明确说明每个工具的技术基础（如NLTK基于规则、spaCy基于统计模型、Voyant基于可视化分析）及其对分析结果的可能影响。

2. **采用混合验证方法**：结合自动化工具、专家评审和用户测试，避免依赖单一工具的结果[7][8]。

3. **区分概率性真理与解释性真理**：对于需要精确量化的任务（如词频统计），优先使用系统综述式的方法；对于需要解释性理解的任务（如主题建模），采用叙述性综述式的批判性分析[8]。

4. **实施“检索-摘要-验证”流程**：首先检索原始语料和工具文档，然后利用工具生成摘要分析，最后通过人工或第三方工具验证结果的一致性[1]。

5. **保持人类监督**：将AI工具视为辅助而非替代，确保最终分析结论由研究者负责[1][2][3]。

总之，当不同工具产生冲突结果时，这本身可能反映了工具的技术差异、语料特性或分析目标的不同，而非某一工具的错误。研究者应将这些冲突视为深入理解工具特性和分析对象的契机，而非简单判定孰优孰劣。

## 参考文献
[1] Retrieve, Summarize, and Verify: How Will ChatGPT Affect Information Seeking from the Medical Literature?. Journal of the American Society of Nephrology. 2023.
[2] The future of ChatGPT in academic research and publishing: A commentary for <i>clinical and translational medicine</i>. Clinical and Translational Medicine. 2023.
[3] The Potential Application of Large Language Models in Pharmaceutical Supply Chain Management. The Journal of Pediatric Pharmacology and Therapeutics. 2024.
[4] Effects of mosquito control using the microbial agent Bacillus thuringiensis israelensis (Bti) on aquatic and terrestrial ecosystems: a systematic review. Environmental Evidence. 2023.
[5] A New Field:<i>History of Humanities</i>. History of Humanities. 2016.
[6] Preliminary results on the paleo-landscape of Tell Basta /Bubastis (eastern Nile delta): An integrated approach combining GIS-Based spatial analysis, geophysical and archaeological investigations. Quaternary International. 2019.
[7] Web Accessibility Evaluation in the AI Era: A Systematic Review on Conventional Tools and the Emerging Use of Large Language Models (LLMs). 2025 10th International Conference on Information Technology and Digital Application (ICITDA). 2025.
[8] Time to challenge the spurious hierarchy of systematic over narrative reviews?. European Journal of Clinical Investigation. 2018.