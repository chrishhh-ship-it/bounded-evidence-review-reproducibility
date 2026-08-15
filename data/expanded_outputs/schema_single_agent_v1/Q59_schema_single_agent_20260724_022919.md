## 检索与筛选概览

本合成基于提供的8条摘要级证据记录，旨在探讨负样本测试的设计方法，以检验reviewer agent识别错误引用的能力。检索到的证据涵盖多智能体系统在学术评审中的应用，包括对抗性作者-评审者工作流[1]、空间文本到SQL的多智能体框架[7]以及系统综述自动化中的评审智能体设计[8]。此外，部分证据涉及生物领域的评审意见[2][3][4][5][6]，但与负样本测试设计的直接相关性有限。筛选后，核心证据集中于[1]、[7]和[8]，它们提供了评审智能体工作流程和验证机制的相关描述。

## 核心主题与证据

核心主题是负样本测试的设计策略，以评估reviewer agent对错误引用的检测能力。证据[1]描述了对抗性多智能体系统，其中作者与评审者工作流包含可验证证据和批评循环，暗示负样本可通过引入故意错误的引用并观察评审者的反馈来设计。证据[7]展示了多智能体框架在空间文本到SQL任务中的应用，其中包含执行后评审阶段，该阶段通过对比生成结果与预期结果来纠正错误，准确率从76.7%提升至87.7%[7]，表明基于执行结果的验证可作为负样本测试的参考。证据[8]提出了LatteReview框架，采用两级评审流程：初级评审者进行标题和摘要筛选，高级评审者进行概念提取[8]，这提示负样本测试可针对不同评审层级设计，例如在摘要筛选阶段插入错误引用，检验初级评审者的识别能力。

## 证据支持的研究方向

基于现有证据，负样本测试设计可沿以下方向展开：第一，利用对抗性工作流[1]构建包含错误引用的测试集，通过评审循环验证检测效果。第二，借鉴执行后评审机制[7]，在测试中引入引用错误并评估评审者能否通过逻辑或事实核查发现不一致。第三，参考多级评审架构[8]，设计分层负样本，例如在初级筛选阶段使用明显错误引用，在高级提取阶段使用隐蔽错误引用，以测试不同评审智能体的敏感度。

## 摘要级证据的局限

所有证据均为摘要级，缺乏具体实验细节、错误引用类型定义或测试指标。例如，[1]未说明对抗性测试的具体设计方法；[7]虽提及评审阶段提升准确率，但未明确错误引用场景；[8]未提供负样本测试的实证数据。此外，部分证据[2][3][4][5][6]与负样本测试主题无关，仅提供评审意见的通用描述。这些局限限制了直接推导负样本测试设计的具体参数。

## 谨慎结论

现有摘要级证据表明，负样本测试设计应结合对抗性工作流[1]、执行后验证[7]和多级评审架构[8]，通过系统性地插入错误引用并评估评审智能体的反馈来检验其识别能力。然而，由于缺乏具体实验数据和错误类型分类，当前结论需谨慎对待。未来研究应基于完整论文，设计包含不同隐蔽程度的错误引用测试集，并量化评审者的检测准确率与误报率。

## 参考文献
[1] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[2] Reviewer #2 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[3] Reviewer #1 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[4] Reviewer #1 (Public Review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[5] Reviewer #2 (Public review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[6] Reviewer #3 (Public Review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[7] From Questions to Queries: An AI-powered Multi-Agent Framework for Spatial Text-to-SQL. arXiv.org. 2025.
[8] LatteReview: a multi-agent framework for systematic review automation using large language models. arXiv preprint arXiv …. 2025.