## 1. 检索与筛选概览

本合成基于给定的八篇文献证据集（E_q），旨在探讨数字人文（DH）文献综合系统中，校准自动评估指标所需的最小人工评估样本量。检索范围涵盖2020年至2026年间发表的文献，涉及医疗健康、数字人文、对话系统、能源法律及文献综合自动化等多个领域。筛选过程遵循严格的证据边界，仅使用提供的八篇文献作为分析依据。这些文献在主题上虽不完全聚焦于数字人文文献综合，但提供了关于人工评估方法、自动文本标注、系统可靠性评估及文献综合流程的间接或部分相关证据。

## 2. 核心主题与证据

现有证据表明，人工评估样本量的确定在多个相关领域均缺乏统一标准。在医疗健康领域，针对大语言模型（LLM）的人工评估实践存在可靠性、泛化性和适用性方面的显著差距，文献综述涵盖的142项研究未能提供明确的样本量指导[1]。在自动文献筛选领域，研究协议指出不同算法报告的结果差异很大，但未涉及人工评估样本量的校准问题[3]。在数字人文领域，自动文本标注系统的评估采用了准实验设计，比较了两种系统的阅读效果和技术接受度，但样本量仅基于实验设计需求，未讨论最小样本量的确定方法[4]。在对话系统评估中，ChatPLUG同时采用了自动评估和人工评估，但未说明人工评估的具体样本量[5]。在文献综合自动化系统方面，ResearchPilot通过自动化测试和端到端本地运行进行评估，完全未涉及人工评估[7]。在诊断数据提取系统的可靠性基准研究中，协议设定了20次独立运行（共320次数据集-运行观察），但这是针对系统自动运行次数，而非人工评估样本量[8]。此外，热浪定义的综合研究采用了11个问题的简短调查，但样本量取决于调查回收情况，未讨论最小样本量问题[2]。能源转型领域的文献则完全不涉及评估样本量问题[6]。

## 3. 证据支持的研究方向

基于现有证据，可以识别出以下与最小人工评估样本量相关的研究方向：第一，建立人工评估的标准化框架。QUEST框架提出了五个评估原则（信息质量、理解与推理、表达风格与人格、安全与危害、信任与信心），但未明确每个维度所需的最小评估样本量[1]。未来研究可探索基于这些维度的样本量计算方法。第二，开发适用于数字人文领域的自动评估校准方法。自动文本标注系统的评估表明，技术接受度可以显著区分不同系统，但阅读效果差异未达到统计显著性[4]，这提示自动评估指标可能需要更大样本量才能检测到细微差异。第三，借鉴医疗领域诊断数据提取系统的可靠性评估方法，将正确率、弃权行为、可重复性和安全性整合到端到端评估中[8]，这种多维度评估框架可能为确定最小样本量提供更稳健的基础。第四，探索自动评估与人工评估的协同机制。ChatPLUG同时采用两种评估方式[5]，ResearchPilot则完全依赖自动化测试[7]，比较这两种策略在数字人文文献综合中的效果差异，可能揭示人工评估的必要样本量边界。

## 4. 摘要级证据的局限

本合成完全依赖摘要级证据，存在以下显著局限：首先，多数文献的摘要未提供关于人工评估样本量的具体数值或计算方法。例如，关于人工评估框架的文献虽然提出了评估原则，但摘要中未包含样本量建议[1]；自动文本标注系统的评估虽然描述了实验设计，但未报告样本量确定依据[4]。其次，摘要可能省略了关键的方法学细节。诊断数据提取系统的协议虽然详细描述了运行次数，但这是针对系统自动运行而非人工评估[8]；ResearchPilot的摘要明确说明其评估仅限于自动化测试和本地运行[7]。第三，部分文献的主题与数字人文文献综合系统的人工评估样本量问题仅有间接关联。例如，热浪定义调查[2]和能源转型文献[6]完全不涉及评估方法学。第四，摘要级证据无法提供关于效应量、统计功效或置信区间等关键统计信息，而这些信息对于确定最小样本量至关重要。最后，所有文献均未直接回答“数字人文文献综合系统中校准自动指标所需的最小人工评估样本量”这一具体问题，因此本合成只能提供间接推断。

## 5. 谨慎结论

基于现有摘要级证据，无法确定数字人文文献综合系统校准自动评估指标所需的最小人工评估样本量。现有研究在人工评估样本量方面存在显著的方法学空白：医疗健康领域的人工评估实践缺乏标准化样本量指导[1]；数字人文领域的系统评估主要依赖实验设计而非统计功效分析[4]；对话系统评估同时采用自动和人工评估但未报告样本量[5]；文献综合自动化系统则完全依赖自动评估[7]。建议未来研究：第一，开展专门针对数字人文文献综合系统的人工评估样本量实验，采用统计功效分析方法确定最小样本量；第二，借鉴QUEST框架的评估原则[1]和诊断数据提取系统的多维度评估方法[8]，开发适用于数字人文领域的样本量计算指南；第三，探索自动评估指标与人工评估结果之间的校准关系，通过系统性的样本量递增实验确定校准所需的临界样本量。在获得更充分的证据之前，研究者应参考类似领域（如医疗健康）的实践，并采用保守的样本量策略。

## 参考文献
[1] A framework for human evaluation of large language models in healthcare derived from literature review. npj Digital Medicine. 2024.
[2] What is a heat wave: A survey and literature synthesis of heat wave definitions across the United States. PLOS Climate. 2024.
[3] A Research Protocol for a Systematic Review of Automatic Literature Screening in Medical Evidence Synthesis. CrossRef. 2020.
[4] Development and evaluation of an automatic text annotation system for supporting digital humanities research. Library hi tech. 2019.
[5] ChatPLUG: Open-Domain Generative Dialogue System with Internet-Augmented Instruction Tuning for Digital Human. arXiv Preprint. 2023.
[6] Just energy business needed! How to achieve a just energy transition by engaging energy companies in reaching climate neutrality: (re)conceptualising energy law for energy corporations. Journal of Energy & Natural Resources Law. 2023.
[7] ResearchPilot: A Local-First Multi-Agent System for Literature Synthesis and Related Work Drafting. Semantic Scholar. 2026.
[8] End-to-End Reliability of Automated Systems for Diagnostic Data Extraction: A Benchmark Study in Uro-Oncologic Evidence Synthesis. CrossRef. 2025.