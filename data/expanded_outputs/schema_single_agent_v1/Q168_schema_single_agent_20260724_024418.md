1. 检索与筛选概览

文献综合系统在处理网络荟萃分析中直接与间接证据冲突时，需依赖严谨的检索与筛选流程。系统综述的核心在于通过多步骤方法确保证据的完整性，包括明确问题、制定方案、系统检索、独立筛选、偏倚风险评估及定量综合[1]。当前，人工智能技术正被用于加速这一过程：例如，基于BERT的自动化筛选工作流可在保持可接受分类性能（AUC 0.77）的同时显著提升效率[7]；而A4SLR框架通过大语言模型驱动的智能体，实现了从检索到证据合成的全流程自动化，在文献筛选（F1分数0.917-0.977）和偏倚风险评估（Cohen's kappa 0.8442-0.9064）中表现出高准确性[8]。此外，众包平台如Cochrane Crowd通过结构化微任务（如识别随机对照试验和PICO要素）辅助筛选，有助于在文献激增时维持高召回率[5]。开放科学原则（如开放数据、开放方法）进一步促进了证据合成的透明性和可重复性，尤其在应对突发公共卫生事件（如COVID-19大流行）时，开放合成资源可支持快速、协调的证据汇总[6]。

2. 核心主题与证据

当网络荟萃分析中直接与间接证据冲突时，系统需优先评估证据的质量与一致性。系统综述的黄金标准要求对纳入研究进行严格的偏倚风险评估，并通过定量合成（如meta分析）处理异质性[1]。例如，在移动健康干预的伞状综述中，研究者采用Fusar-Poli和Radua方法评估证据强度，发现部分效果（如糖化血红蛋白降低）具有说服力，但42%的效果不显著，且存在发表偏倚和调节变量报告不足等问题[2]。这表明，冲突证据的出现可能源于原始研究的质量差异或方法学缺陷。此外，大语言模型（如ChatGPT）在证据综合中可能产生“幻觉”或遗漏矛盾信息，例如在总结COVID-19相关机制时，模型未能提及相互矛盾的证据，且部分引用不准确[3]。因此，系统需结合检索、总结与验证的范式，利用传统搜索引擎增强LLM的可靠性，同时保留用户对证据来源的控制[3]。

3. 证据支持的研究方向

基于现有证据，未来研究方向应聚焦于以下方面：首先，开发自动化、动态且交互式的证据合成方法，以应对直接与间接证据冲突的复杂场景[4]。其次，推广开放合成实践，通过共享数据、代码和方法论，提高证据综合的透明度和可验证性，从而减少研究浪费并增强决策支持[6]。第三，进一步优化AI辅助工具的性能，例如通过微调BERT模型或集成多智能体框架（如A4SLR），在保持高准确率的同时处理异质性证据[7,8]。此外，需加强证据强度的标准化评估，如采用GRADE框架，以明确冲突证据的优先级[6]。最后，应鼓励众包平台（如Cochrane Crowd）的参与，通过分布式人工筛查补充自动化流程，确保对矛盾证据的全面识别[5]。

4. 摘要级证据的局限

本合成基于摘要级证据，存在显著局限。首先，摘要可能省略关键方法学细节，如网络荟萃分析中直接与间接证据冲突的具体处理策略（如节点拆分法或一致性模型），导致无法深入评估冲突来源[1]。其次，部分记录仅提供初步结论，例如关于LLM在证据综合中的应用，摘要未详细说明其处理矛盾证据的机制[3,4]。第三，摘要级证据可能受发表偏倚影响，如移动健康干预综述中42%的非显著效果未得到充分讨论[2]。此外，开放合成原则虽被提倡，但摘要未提供具体实施案例或量化其解决冲突证据的效果[6]。因此，本合成的结论应视为初步探索，需结合全文分析以验证其可靠性。

5. 谨慎结论

文献综合系统在处理网络荟萃分析中直接与间接证据冲突时，应优先采用结构化、透明的方法学框架，结合自动化工具（如BERT、A4SLR）与人工验证，以平衡效率与准确性[1,7,8]。同时，需警惕LLM在证据综合中的“幻觉”风险，并坚持“检索-总结-验证”的闭环流程[3]。开放合成原则和众包机制可增强证据的可追溯性和全面性，但需注意摘要级证据的固有局限[5,6]。未来应推动动态、交互式证据合成系统的发展，以更有效地应对冲突证据，支持临床决策[4]。

## 参考文献
[1] How to Conduct and Interpret Systematic Reviews and Meta-Analyses. Clinical and Translational Gastroenterology. 2017.
[2] Mobile phone interventions to improve health outcomes among patients with chronic diseases: an umbrella review and evidence synthesis from 34 meta-analyses. The Lancet Digital Health. 2024.
[3] Retrieve, Summarize, and Verify: How Will ChatGPT Affect Information Seeking from the Medical Literature?. Journal of the American Society of Nephrology. 2023.
[4] Future of evidence synthesis: Automated, living, and interactive systematic reviews and meta-analyses. Mayo Clinic Proceedings: Digital …. 2024.
[5] How I contributed to Cochrane Crowd and why it matters for evidence synthesis. International Journal of Risk &amp; Safety in Medicine. 2026.
[6] Open synthesis and the coronavirus pandemic in 2020. Journal of Clinical Epidemiology. 2020.
[7] Accelerating Evidence Synthesis: A BERT-Assisted Workflow for Meta-Analyses of Radiotherapy Complications in Nasopharyngeal Carcinoma. Reports. 2026.
[8] A4SLR: An Agentic Artificial Intelligence-Assisted Systematic Literature Review Framework to Augment Evidence Synthesis for Health Economics and Outcomes Research and Health Technology Assessment.. Value in health : the journal of the International Society for Pharmacoeconomics and Outcomes Research. 2025.