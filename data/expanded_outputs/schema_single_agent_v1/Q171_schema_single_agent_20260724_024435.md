## 1. 检索与筛选概览

本合成基于提供的8篇文献，这些文献涵盖了自动化元分析（AMA）、传统元分析方法学以及特定领域的证据合成研究。其中，[1]对2006至2024年间978篇AMA相关论文进行了系统综述，最终纳入54项研究，发现57%的工作聚焦于数据处理的自动化，仅17%涉及高级合成阶段，且仅有一项研究（2%）探索了初步的全流程自动化。[2]则展示了一个基于BERT的文献筛选工作流，从6496条初始记录中筛选出23项研究用于下游元分析。[4]提出的EligMeta框架从4044项候选试验中通过规则筛选出39项临床相关研究，并恢复了所有13项指南引用的试验。[5]和[6]分别提供了定量和定性证据合成的协议或方法框架。[7]和[8]则展示了传统元分析和证据合成在具体临床或管理领域的应用。整体而言，这些文献反映了从传统方法到AI辅助自动化合成的演进趋势，但全流程自动化仍面临显著挑战[1]。

## 2. 核心主题与证据

关于固定效应与随机效应模型的选择，核心证据来自对异质性的量化评估。[2]在其元分析中报告了纳入研究存在显著异质性（I² = 86.85%），并据此明确支持使用随机效应模型进行结果合并。[5]在其协议中明确指出，元分析将根据异质性程度选择固定或随机效应模型，并使用I²统计量评估异质性。此外，[4]提出的EligMeta框架引入了一种基于人群对齐的加权方法，其敏感性分析显示，当纳入临床兼容性权重后，合并风险比从传统Mantel-Haenszel估计的2.18（95% CI: 1.71-2.79）变为1.97（95% CI: 1.76-2.20），这表明模型选择不仅取决于统计异质性，还应考虑研究间临床特征的兼容性。[7]在其实证元分析中，针对不同结局（如住院率、急诊就诊率、依从性）分别进行了合并，并报告了相应的异质性指标（如I²或通过敏感性分析验证结果稳健性），但未明确说明模型选择的具体统计阈值。

## 3. 证据支持的研究方向

基于现有证据，以下研究方向值得关注：第一，开发能够自动检测异质性并据此推荐模型（固定或随机效应）的算法。[1]指出，尽管AI在数据处理方面取得进展，但在异质性评估等高级合成阶段的整合仍不充分。第二，将临床兼容性纳入模型选择框架。[4]的EligMeta框架展示了通过计算目标试验与比较试验之间人群对齐的相似性权重来调整合并结果的可能性，这为超越单纯统计异质性的模型选择提供了新思路。第三，探索模型选择对下游决策的影响。[7]和[8]表明，不同的模型假设可能影响对治疗效应或组织因素的推断，因此需要建立模型选择的透明报告标准。第四，在自动化工作流中集成异质性诊断工具。[2]的BERT辅助工作流已实现了文献筛选的自动化，未来可扩展至异质性评估和模型选择的自动化。

## 4. 摘要级证据的局限

本合成基于摘要级证据，存在以下局限：首先，[1]作为系统综述，其关于AMA发展阶段的分类和比例数据可能依赖于对全文的详细编码，摘要中仅提供了概括性结论，缺乏对具体自动化异质性评估方法的描述。其次，[2]和[4]虽然报告了异质性指标（I²）或模型比较结果，但未在摘要中详细说明模型选择的具体统计准则（如I²阈值、Q检验的p值）或敏感性分析的全部细节。第三，[5]作为研究协议，其方法学描述是前瞻性的，实际执行中可能因数据特征而调整模型选择策略。第四，[6]和[8]分别采用定性证据合成和主题分析方法，其研究范式与定量元分析不同，不涉及固定/随机效应模型的选择问题，因此对核心问题的直接贡献有限。最后，所有摘要均未提供关于固定效应与随机效应模型选择的形式化决策规则或自动化实现细节。

## 5. 谨慎结论

综合现有摘要级证据，可以得出以下谨慎结论：在自动化元分析中，固定效应与随机效应模型的选择应主要基于对纳入研究异质性的量化评估，其中I²统计量是常用的决策指标[2][5]。当检测到显著异质性（如I² > 50%或更高）时，倾向于使用随机效应模型[2]。然而，模型选择不应仅依赖统计异质性，还应考虑研究间临床特征的兼容性，如人群基线特征、干预措施差异等[4]。当前自动化元分析在异质性评估和模型选择环节的自动化程度仍然有限[1]，未来需要开发能够整合统计异质性和临床兼容性的智能决策框架。鉴于现有证据主要来自摘要，建议在应用这些发现时参考原始全文以获取完整的模型选择细节和敏感性分析结果。

## 参考文献
[1] Transforming Evidence Synthesis: A Systematic Review of the Evolution of Automated Meta-Analysis in the Age of AI. arXiv.org. 2025.
[2] Accelerating Evidence Synthesis: A BERT-Assisted Workflow for Meta-Analyses of Radiotherapy Complications in Nasopharyngeal Carcinoma. Reports. 2026.
[3] Model‐Based Network Meta‐Analysis: A Framework for Evidence Synthesis of Clinical Trial Data. CPT: Pharmacometrics & Systems Pharmacology. 2016.
[4] Eligibility-Aware Evidence Synthesis: An Agentic Framework for Clinical Trial Meta-Analysis. arXiv Preprint. 2026.
[5] Effects of antioxidant consumption on physical rehabilitation variables and quality of life in people with osteoarthritis: Protocol for a systematic review with meta-analysis. F1000Research. 2025.
[6] Intersex people or khunthā in the Middle East – How they are perceived, accepted, & treated: qualitative evidence synthesis & framework analysis. Psychology &amp; Sexuality. 2024.
[7] Real-World Evidence of the Clinical and Economic Impact of Long-Acting Injectable Versus Oral Antipsychotics Among Patients with Schizophrenia in the United States: A Systematic Review and Meta-Analysis.. CNS drugs. 2021.
[8] The presence and potential impact of psychological safety in the healthcare setting: an evidence synthesis. BMC Health Services Research. 2021.