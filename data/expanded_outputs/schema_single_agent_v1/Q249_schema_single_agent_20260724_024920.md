## 1. 检索与筛选概览

本合成基于所提供的八篇摘要级证据文献，涵盖人工智能在证据综合中的应用、特定领域的证据综合实践以及证据综合方法论等主题。这些文献来源包括医学期刊、预印本平台及跨学科期刊，发表时间跨度为2020年至2025年。所涉研究采用了系统综述、定性证据综合、框架分析及人工智能辅助分析等多种方法。由于本合成仅依赖提供的摘要信息，未进行独立的全文检索与筛选，因此检索范围受限于给定的文献集合。

## 2. 核心主题与证据

本证据集的核心主题可归纳为以下三个方面：

**（1）人工智能在证据综合中的能力与局限**

多项研究探讨了大型语言模型（LLM）在证据综合任务中的表现。ChatGPT在生成医学文献摘要时存在“幻觉”问题，会编造看似可信但虚假的参考文献，且无法忠实引用来源[1]。GPT-4虽然承认无法生成参考文献，但将验证任务完全留给用户[1]。检索增强生成（RAG）系统结合GPT-3.5在脑-心互联组学的系统综述中表现优于GPT-4，但该系统仍处于开发阶段[2]。GPT-4o在气候变化证据综合中，低专业知识任务（如地理位置识别）准确率高，但中高专业知识任务（如利益相关者识别、适应深度评估）可靠性不足[4]。这些发现一致表明，当前LLM在证据综合中尚不能完全替代人工专家。

**（2）特定领域的证据综合实践**

多个研究展示了不同领域的证据综合成果。关于中东地区间性人（khunthā）的定性证据综合揭示了社会文化态度对父母和医生决策的深刻影响[3]。医疗环境中心理安全感的证据综合纳入了62篇论文，发现心理安全感水平存在异质性，且与患者安全和团队结果相关[5]。城市绿化效果的更新系统综述纳入308项研究，证实绿地具有降温效应，但不同植被类型效果存在差异[6]。

**（3）证据综合的方法论进展**

开放科学原则在证据综合中的应用（即“开放综合”）被强调为提升研究透明度、可重复性和协作性的关键[7]。COVID-19疫情期间，加拿大魁北克省的证据综合团队通过调整方法、采用新技术工具和加强协作来应对快速决策需求，但平衡严谨性与速度仍是主要挑战[8]。

## 3. 证据支持的研究方向

基于现有证据，以下研究方向值得关注：

- **提升LLM在证据综合中的可靠性**：需要开发自动验证工具，确保LLM生成的摘要忠实于输入来源[1]；同时应设计利用LLM优势（如文本总结）同时改进其弱点的评估工作流[4]。
- **优化检索增强生成系统**：将LLM与传统文献搜索引擎或专业数据库API结合，有望减少幻觉并提高综合质量[1][2]。
- **完善特定领域的证据综合方法**：例如，城市绿化研究中需平衡日间遮阳与夜间降温，并考虑树种选择对污染物去除和挥发性有机物排放的影响[6]。
- **推广开放综合实践**：包括开放获取、开放数据、开放方法和开放教育资源，以应对人道主义危机中的知识需求[7]。
- **加强证据综合的快速响应能力**：明确决策者需求、改善沟通循环、制定方法学基准，以提高快速响应的实用性和可信度[8]。

## 4. 摘要级证据的局限

本合成完全依赖摘要级信息，存在以下固有局限：

- **信息不完整**：摘要无法提供研究方法的全部细节、数据来源的完整性评估以及结果的全面呈现。例如，关于ChatGPT的研究[1]详细描述了其幻觉问题，但摘要未包含所有实验设置和完整结果数据。
- **无法验证原始研究质量**：摘要未提供纳入研究的质量评价信息，如偏倚风险评估、样本代表性等，这限制了证据强度的判断。
- **缺乏矛盾证据的呈现**：摘要通常突出主要发现，可能省略了研究间的矛盾结果或未预期的发现。例如，心理安全感研究[5]提到异质性，但未详细说明具体矛盾点。
- **时效性与覆盖范围限制**：部分文献为预印本[2][4]，尚未经过同行评审；文献覆盖领域有限，无法代表证据综合领域的全貌。

## 5. 谨慎结论

基于所提供的摘要级证据，可以得出以下谨慎结论：

第一，人工智能工具（特别是大型语言模型）在证据综合中展现出潜力，尤其在文本总结和低专业知识任务中，但其当前可靠性不足以独立用于临床或政策决策，必须辅以人工验证[1][4]。

第二，证据综合的方法论正在快速发展，开放科学原则的应用[7]和快速响应机制的建立[8]有助于提升证据综合的效率、透明度和时效性，但平衡速度与严谨性仍是核心挑战。

第三，特定领域的证据综合已产生有价值的见解，如城市绿化的降温效应[6]、心理安全感对医疗质量的影响[5]等，但这些结论的推广需考虑研究背景和异质性。

第四，本合成的结论受限于摘要级证据的固有局限，建议在获取全文并进行严格质量评估后，对上述结论进行验证和细化。未来研究应致力于开发更可靠的AI辅助证据综合工具，并推动开放综合实践的标准化。

## 参考文献
[1] Retrieve, Summarize, and Verify: How Will ChatGPT Affect Information Seeking from the Medical Literature?. Journal of the American Society of Nephrology. 2023.
[2] An AI-Driven Live Systematic Reviews in the Brain-Heart Interconnectome: Minimizing Research Waste and Advancing Evidence Synthesis. arXiv.org. 2025.
[3] Intersex people or khunthā in the Middle East – How they are perceived, accepted, & treated: qualitative evidence synthesis & framework analysis. Psychology &amp; Sexuality. 2024.
[4] Assessing the Effectiveness of GPT-4o in Climate Change Evidence Synthesis and Systematic Assessments: Preliminary Insights. CLIMATENLP. 2024.
[5] The presence and potential impact of psychological safety in the healthcare setting: an evidence synthesis. BMC Health Services Research. 2021.
[6] How effective is ‘greening’ of urban areas in reducing human exposure to ground-level ozone concentrations, UV exposure and the ‘urban heat island effect’? An updated systematic review. Environmental Evidence. 2021.
[7] Open synthesis and the coronavirus pandemic in 2020. Journal of Clinical Epidemiology. 2020.
[8] Production and use of rapid responses during the COVID-19 pandemic in Quebec (Canada): perspectives from evidence synthesis producers and decision makers. Health Research Policy and Systems. 2024.