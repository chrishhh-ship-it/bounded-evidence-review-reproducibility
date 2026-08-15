# 自动NLI评估GRADE证据体对综合主张支持度的构念效度局限

## 1. 检索与筛选概览

本合成基于所提供的8篇文献（[1]–[8]），涵盖2018年至2025年间发表的证据。这些文献包括定性证据综合（[1]、[4]）、方法论讨论（[2]）、系统综述与Meta分析（[3]、[5]、[8]）、临床指南（[7]）以及自动化系统基准研究方案（[6]）。文献来源涵盖临床试验、方法学期刊、临床营养、家庭暴力、人工智能预印本、皮肤病学及卫生技术评估等领域。其中，直接涉及自动化证据综合的文献为[5]和[6]，分别从系统综述视角和基准测试视角探讨了自动化Meta分析（AMA）及诊断数据提取系统的可靠性。其余文献提供了关于证据综合方法、GRADE应用及证据体评估的上下文背景。

## 2. 核心主题与证据

### 2.1 自动化证据综合的现状与局限

当前自动化Meta分析（AMA）研究主要聚焦于数据处理阶段的自动化（占57%），而仅有17%涉及高级综合阶段，仅有一项研究（2%）探索了初步的全流程自动化[5]。尽管大语言模型（LLMs）和先进AI取得了突破，其在统计建模、异质性评估和偏倚评价等高级综合任务中的整合仍不成熟，这限制了AMA实现完全自主Meta分析的潜力[5]。在诊断性系统综述领域，自动化系统的端到端可靠性、安全性和可重复性尚未得到充分表征，现有基准研究方案旨在通过整合正确性、弃权行为、可重复性和安全性来评估自动化工具[6]。

### 2.2 GRADE框架与证据体评估的复杂性

GRADE方法已被广泛应用于临床指南和系统综述中，用于评估证据体的质量（高、中、低、极低）[7][8]。在皮肤鳞状细胞癌指南中，GRADE被用于对每个临床问题的证据进行评级，并综合考虑利弊平衡、证据质量、患者价值观和偏好以及资源分配来确定推荐强度[7]。在睾酮替代疗法的证据综合中，研究者按照当前方法论标准进行了个体参与者数据Meta分析，并使用Cochrane偏倚风险评估工具[8]。然而，GRADE评估本身依赖于对证据体的整体判断，包括对效应估计的不确定性、不一致性、间接性、不精确性和发表偏倚的评估。

### 2.3 自动NLI评估“支持度”的构念效度挑战

自动自然语言推理（NLI）系统用于判断综合主张是否被证据体“支持”，面临多重构念效度挑战。首先，证据综合的本质涉及解释和判断，而非简单的数据汇总。方法论文献指出，系统综述与叙事综述并非层级关系，而是互补的学术形式，前者处理概率性真理，后者处理似然性真理[2]。叙事综述（包括诠释性综述、现实主义综述和元叙事综述）依赖于有见识的智慧、批判性反思和创造性判断，这些过程难以被自动化系统复制[2]。其次，GRADE评估本身包含对证据体质量的定性判断，如对效应估计的置信度评估，这要求理解研究设计、偏倚风险和临床背景[7][8]。自动NLI系统通常基于文本表面特征进行推理，难以捕捉这些深层次的方法学考量。

## 3. 证据支持的研究方向

### 3.1 自动化系统的可靠性基准测试

需要建立保守且可复现的评估框架，用于评价自动化系统在证据综合中的表现。现有基准研究方案提出了整合正确性、弃权行为（在不可推导场景中正确声明不可推导性）、可重复性和安全性的端到端评估方法[6]。该方案采用非劣效性设计，以95%的正确性阈值作为基准，通过多次独立运行来评估系统的稳定性[6]。

### 3.2 跨阶段自动化的整合

当前AMA研究的一个关键缺口是缺乏跨所有Meta分析阶段的自动化整合。未来研究应聚焦于弥合数据处理、统计建模和高级综合之间的自动化鸿沟，提高可解释性，并确保方法学稳健性[5]。这包括将LLMs和先进AI整合到异质性评估和偏倚评价等任务中。

### 3.3 证据综合方法论的多元化

证据综合不应局限于单一方法论。系统综述和叙事综述各有其适用场景和优势：系统综述适用于回答狭窄、明确的研究问题，而叙事综述（包括诠释性、现实主义和元叙事方法）适用于需要澄清和洞察的复杂情境[2]。在评估自动NLI系统时，需要认识到不同综合方法产生不同类型的真理，自动系统可能只适用于特定类型的综合任务。

## 4. 摘要级证据的局限

本合成基于摘要级证据，存在以下局限：

1. **信息粒度不足**：摘要通常仅提供研究的高层概述，缺乏方法学细节、效应估计的精确数值和偏倚评估的完整信息。例如，[7]的摘要虽提及GRADE应用，但无法获取具体的GRADE证据概况和LETR表格内容。

2. **方法论细节缺失**：自动NLI系统的具体架构、训练数据和推理机制在摘要中无法体现。[5]和[6]的摘要提供了研究目标和设计概览，但未详细说明所使用的NLI模型类型、评估指标的计算方式或基准测试的具体实施细节。

3. **结果报告不完整**：摘要可能选择性报告主要发现，而忽略阴性结果或亚组分析。[8]的摘要报告了睾酮替代疗法对心血管事件无显著差异，但未详细说明不同亚组的结果或敏感性分析。

4. **时效性限制**：部分文献发表于2025年（[5]、[6]），代表了最新进展，但自动化NLI技术仍在快速发展，摘要级证据可能无法反映最新技术状态。

5. **语境依赖性**：GRADE评估和证据综合的质量高度依赖于具体的研究问题和临床背景，摘要无法提供这些语境信息。

## 5. 谨慎结论

基于现有摘要级证据，自动NLI系统用于评估GRADE评级证据体对综合主张的支持度，面临显著的构念效度局限。这些局限源于：（1）证据综合本身涉及解释性判断和创造性思维，难以被自动化系统完全捕捉[2]；（2）GRADE评估包含对证据体质量的定性判断，需要理解研究设计、偏倚风险和临床背景[7][8]；（3）当前自动化系统主要聚焦于数据处理阶段，高级综合阶段的自动化仍不成熟[5]；（4）自动化系统的可靠性和可重复性尚未得到充分验证[6]。

因此，在缺乏对自动化系统进行严格端到端基准测试（包括正确性、弃权行为、可重复性和安全性评估）的情况下，将自动NLI输出作为判断综合主张是否被GRADE评级证据体“支持”的唯一或主要依据，可能产生误导性结论。未来研究应优先开发能够整合方法学判断和语境理解的自动化框架，并建立保守的评估标准，以确保自动化工具在证据综合中的有效性和安全性。

## 参考文献
[1] Understanding the perspectives of recruiters is key to improving randomised controlled trial enrolment: a qualitative evidence synthesis. Trials. 2022.
[2] Time to challenge the spurious hierarchy of systematic over narrative reviews?. European Journal of Clinical Investigation. 2018.
[3] What is the efficacy of dietary, nutraceutical, and probiotic interventions for the management of gastroesophageal reflux disease symptoms? A systematic literature review and meta-analysis.. Clinical nutrition ESPEN. 2022.
[4] What are the Factors Influencing Service Provider Response to Working with Families Affected by Intimate Partner Violence and Abuse? A Qualitative Systematic Review of the Literature. Journal of Family Violence. 2024.
[5] Transforming Evidence Synthesis: A Systematic Review of the Evolution of Automated Meta-Analysis in the Age of AI. arXiv.org. 2025.
[6] End-to-End Reliability of Automated Systems for Diagnostic Data Extraction: A Benchmark Study in Uro-Oncologic Evidence Synthesis. CrossRef. 2025.
[7] British Association of Dermatologists guidelines for the management of people with cutaneous squamous cell carcinoma 2020*. British Journal of Dermatology. 2020.
[8] The effects and safety of testosterone replacement therapy for men with hypogonadism: the TestES evidence synthesis and economic evaluation.. Health Technology Assessment. 2024.