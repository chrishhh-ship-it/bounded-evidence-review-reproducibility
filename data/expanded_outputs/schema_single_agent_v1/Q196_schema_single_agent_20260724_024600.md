1. 检索与筛选概览

本合成基于提供的八篇摘要级证据，这些文献涵盖了自动化系统在生物医学证据合成中的可靠性、性能基准以及实践应用。证据来源包括2023至2026年间发表的系统综述、研究方案和基准研究，涉及诊断数据提取、系统综述流程自动化、文献筛选、数据提取以及临床大语言模型评估等主题。所有证据均来自同行评审期刊或预印本平台，但均为摘要级信息，未提供完整的全文数据。

2. 核心主题与证据

现有证据表明，自动化系统在生物医学证据合成中的性能表现存在显著差异，且尚未有充分证据支持用单一自动化评审者完全取代双评审者共识模式。具体而言：

- **性能基准与可靠性**：一项针对诊断数据提取的基准研究方案（[1]）设定了95%的正确率阈值和5个百分点的非劣效性界值，旨在评估自动化系统的端到端可靠性，包括正确性、弃权行为、可重复性和运行效率。该研究强调需要保守且可重复的评估框架，但尚未报告最终结果。另一项系统综述（[5]）指出，自动化文献筛选的性能在不同系统综述主题间差异很大，且多数工具仅针对单一阶段，对整个流程的时间节省有限，实际效益仍不确定。

- **知识-实践差距**：一项涵盖39个医学大语言模型基准的系统综述（[6]）量化了显著的知识-实践差距：模型在知识型基准（如美国医师资格考试）上达到84%-90%的准确率，但在实践型基准上仅为45%-69%，安全评估准确率仅为40%-50%。该综述明确结论认为，自主部署目前不可行，所有基于证据的实施策略必须要求实践导向的验证和稳健的人机协同监督。

- **自动化工具的比较**：一项研究方案（[2]）计划评估EPPI-Reviewer和Copilot 365在系统综述更新中的准确性和效率，但尚未报告结果。另一项研究（[3]）展示了使用大语言模型识别行为干预措施的系统，其最佳配置F1分数为67.0%，高精度变体虽达到100%精确度但召回率仅为12%，表明存在可调的性能权衡。

- **其他领域的应用**：在输血医学（[4]）和慢性阻塞性肺疾病急性加重（[8]）的综述中，机器学习模型在预测任务上表现出潜力（如AUROC>0.8），但多数研究缺乏前瞻性验证，且逻辑回归在直接比较中常与机器学习表现相当甚至更优（[4]）。这些证据均未涉及用单一自动化评审者替代双评审者共识的基准。

3. 证据支持的研究方向

基于现有摘要级证据，以下研究方向可能有助于评估用单一自动化评审者替代双评审者共识的可行性：

- **建立实践导向的基准**：鉴于知识-实践差距的存在（[6]），应开发专门针对证据合成流程（如数据提取、质量评估）的实践型基准，而非仅依赖知识型测试。基准应包含正确性、弃权率、可重复性和安全性等维度（[1]）。

- **评估全流程自动化**：目前多数工具仅针对单一阶段（[5]），未来研究应评估端到端自动化系统在完整系统综述流程中的性能，包括搜索、筛选、数据提取和综合，并比较其与双评审者共识在敏感性和特异性上的差异。

- **探索可调的性能权衡**：如[3]所示，通过自一致性等策略可在精确度和召回率之间进行权衡。未来研究应确定在证据合成中可接受的最低性能阈值，并明确在哪些任务中自动化系统可以安全地替代人工评审。

- **关注安全与错误模式**：自动化系统在安全评估上的低准确率（[6]）提示需要系统性地分析其错误模式，特别是幻觉和错误弃权行为（[1]），以评估其对证据合成结论可靠性的影响。

4. 摘要级证据的局限

本合成基于摘要级证据，存在以下固有局限：

- **信息不完整**：摘要通常仅提供研究背景、方法和初步结论，缺乏详细的性能数据、统计结果和敏感性分析。例如，[1]和[2]仅报告了研究方案，未提供实际性能数据；[4]和[8]虽为完整综述，但摘要中仅呈现了概括性发现。

- **缺乏直接比较**：现有摘要未直接比较单一自动化评审者与双评审者共识在相同任务上的性能。多数研究评估的是自动化工具辅助人工评审，而非完全替代。

- **异质性高**：不同研究使用的基准、数据集、评估指标和任务类型差异较大，难以直接汇总或进行定量比较。例如，[3]使用F1分数和召回率，而[4]使用AUROC。

- **时效性与发表偏倚**：部分证据来自预印本（[3]）或研究方案（[1, 2]），尚未经过同行评审或完成数据收集。此外，可能未包含未发表的阴性结果。

5. 谨慎结论

基于现有摘要级证据，目前尚无充分、直接的性能基准支持用单一自动化评审者完全取代双评审者共识模式。尽管自动化系统在特定任务（如文献筛选、数据提取）上展现出潜力，但其性能存在显著的知识-实践差距（[6]），且在不同主题间差异较大（[5]）。现有证据强调，自动化系统更适合作为辅助工具而非替代品，特别是在安全关键的任务中，必须保持人机协同监督（[6]）。未来需要更多针对完整证据合成流程的实践型基准研究，并直接比较单一自动化评审者与双评审者共识在正确性、可靠性和安全性上的表现，才能为替代决策提供依据。

## 参考文献
[1] End-to-End Reliability of Automated Systems for Diagnostic Data Extraction: A Benchmark Study in Uro-Oncologic Evidence Synthesis. CrossRef. 2025.
[2] Study protocol for evaluating automation of systematic review processes with EPPI-Reviewer and Copilot 365 in updating the cataract evidence gap map. Systematic Reviews. 2026.
[3] Identifying Evidence-Based Nudges in Biomedical Literature with Large Language Models. arXiv Preprint. 2026.
[4] Machine learning in transfusion medicine: A scoping review. Transfusion. 2023.
[5] Automation of systematic reviews of biomedical literature: a scoping review of studies indexed in PubMed. Systematic Reviews. 2024.
[6] Knowledge-Practice Performance Gap in Clinical Large Language Models: Systematic Review of 39 Benchmarks. Journal of Medical Internet Research. 2025.
[7] Empathy in Social Entrepreneurship: Evidence from a Systematic Review with Structured Narrative Synthesis. CrossRef. 2025.
[8] Remote Patient Monitoring and Machine Learning in Acute Exacerbations of Chronic Obstructive Pulmonary Disease: Dual Systematic Literature Review and Narrative Synthesis.. Journal of medical Internet research. 2024.