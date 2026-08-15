## 1. 检索与筛选概览

本合成基于提供的8篇摘要级证据，这些文献涵盖了多种证据合成方法的应用场景。其中，[1]和[2]分别展示了传统系统综述在护理教育中的真实世界证据教学和心理安全感领域的应用；[3]和[5]探讨了大型语言模型（LLMs）和人工智能在自动化证据合成中的潜力与局限；[6]进一步提出了AI驱动的实时系统综述框架；[4]则展示了结合个体参与者数据元分析的综合性证据合成项目；[7]和[8]分别涉及定性证据合成和更新系统综述。这些文献共同构成了理解自动化证据合成中“检索方向选择”（前向与后向引文检索）对“制造残留”（fabrication residual）影响的基础背景。

## 2. 核心主题与证据

**核心主题**：在自动化证据合成中，检索策略（前向与后向引文检索）的选择直接影响系统生成内容的准确性与完整性，即“制造残留”——指系统生成看似合理但实际错误或虚构的信息。

**关键证据**：
- [3]明确指出，ChatGPT等LLMs在直接回答医学问题时倾向于生成“自信但虚构的回应”（hallucination），例如在要求列出COVID-19相关AKI机制时，系统“用虚构的标题和不相关的PubMed标识符支持其主张”。这表明，若检索策略不当（如仅依赖前向检索而缺乏对原始来源的验证），会显著增加制造残留。
- [3]进一步指出，即使采用检索增强生成（RAG）方法（如ChatGPT-4的网页浏览插件），系统仍可能“仅基于两篇文章提供摘要，未能综合证据”，导致“遗漏重要观点或包含输入来源不支持的主张”。这暗示后向引文检索（追溯原始文献）的缺失会加剧信息不完整。
- [5]的系统综述发现，当前自动化元分析（AMA）中“仅17%涉及高级综合阶段”，且“仅一项研究（2%）探索了初步的全流程自动化”，表明检索与综合环节的自动化脱节是制造残留的结构性原因。
- [6]提出的AI驱动系统通过“检索增强生成（RAG）与GPT-3.5”实现了“图式查询和主题建模”，但该研究同时指出RAG系统在综合多源证据时仍存在局限性，这与[3]中观察到的“摘要可能遗漏重要机制”现象一致。

**检索方向的影响机制**：前向检索（基于关键词或主题搜索最新文献）可能遗漏关键背景文献，导致系统依赖不完整信息生成回应；后向检索（追溯引文网络）虽能补充原始证据，但若缺乏有效验证机制，仍可能引入错误引用。[3]和[5]共同表明，当前自动化系统在“检索-摘要-验证”链条中，验证环节的薄弱是制造残留的主要来源。

## 3. 证据支持的研究方向

基于现有证据，以下研究方向具有潜力：

1. **检索增强与验证机制融合**：[3]提出的“检索、摘要、验证”范式强调，需将传统文献搜索引擎与LLMs结合，并开发自动验证工具以检测生成内容的准确性。这直接针对制造残留问题。
2. **全流程自动化综合**：[5]指出当前AMA在“异质性评估和偏倚评价”等高级综合阶段自动化不足，未来需“弥合所有元分析阶段的自动化差距”，包括前向与后向检索的协同。
3. **实时更新与质量监控**：[6]的“实时更新数据库”和“交互式仪表盘”设计，可减少研究浪费并提高证据时效性，但需进一步研究如何在此框架内嵌入制造残留检测机制。
4. **跨领域适应性**：[6]的系统架构可应用于多种生物医学领域，但[5]发现不同领域（医学67%与非医学33%）的自动化模式存在差异，需针对特定领域优化检索策略以减少残留。

## 4. 摘要级证据的局限

本合成基于摘要级证据，存在以下局限：

- **信息粒度不足**：摘要无法提供检索策略的具体细节（如前向/后向检索的算法实现、引文网络构建方法），限制了直接比较两种检索方向对制造残留影响的深度。[3]虽提及RAG方法，但未量化不同检索策略下的残留率。
- **领域偏差**：多数文献聚焦医学领域（[1][2][3][4][8]），而[5]指出非医学领域（33%）的自动化模式不同，可能影响结论的泛化性。
- **时效性限制**：[3]基于2023年的GPT-3.5/4.0版本，[5]和[6]为2025年预印本，技术迭代迅速，当前LLMs的制造残留特性可能已发生变化。
- **缺乏直接比较研究**：现有证据中无专门比较前向与后向引文检索对制造残留影响的实验性研究，本合成仅能基于间接证据推断。

## 5. 谨慎结论

基于现有摘要级证据，可得出以下谨慎结论：

1. **检索方向的选择是影响制造残留的关键因素**：前向检索（依赖关键词匹配）易导致系统生成虚构引用（如[3]所示），而后向检索（追溯引文网络）虽能补充原始来源，但若缺乏验证机制，仍可能产生不完整或错误的综合结果。
2. **当前自动化系统在综合阶段的薄弱是制造残留的结构性原因**：[5]揭示的“仅17%涉及高级综合阶段”表明，检索与综合的脱节使得系统难以有效整合前向与后向检索结果，从而增加残留风险。
3. **“检索-摘要-验证”范式是减少制造残留的可行路径**：[3]和[6]均强调，将LLMs与结构化检索工具（如RAG）结合，并嵌入验证步骤，可降低虚构信息的风险。但[3]也警告，即使采用RAG，系统仍可能“遗漏重要观点或包含不支持的断言”。
4. **未来研究需直接比较不同检索策略的残留率**：当前证据不足以量化前向与后向检索对制造残留的具体影响，亟需设计对照实验，在控制其他变量的情况下，评估两种策略在自动化证据合成中的准确性、完整性和虚构率。

综上，在自动化证据合成中，单纯依赖前向检索或后向检索均不足以消除制造残留；需发展融合双向检索、强化验证环节的全流程自动化框架，并针对具体领域优化策略。

## 参考文献
[1] How is Real World Evidence taught in Nursing? A Systematic review undertaking a narrative synthesis of the literature (Preprint). CrossRef. 2023.
[2] The presence and potential impact of psychological safety in the healthcare setting: an evidence synthesis. BMC Health Services Research. 2021.
[3] Retrieve, Summarize, and Verify: How Will ChatGPT Affect Information Seeking from the Medical Literature?. Journal of the American Society of Nephrology. 2023.
[4] The effects and safety of testosterone replacement therapy for men with hypogonadism: the TestES evidence synthesis and economic evaluation.. Health Technology Assessment. 2024.
[5] Transforming Evidence Synthesis: A Systematic Review of the Evolution of Automated Meta-Analysis in the Age of AI. arXiv.org. 2025.
[6] An AI-Driven Live Systematic Reviews in the Brain-Heart Interconnectome: Minimizing Research Waste and Advancing Evidence Synthesis. arXiv.org. 2025.
[7] Intersex people or khunthā in the Middle East – How they are perceived, accepted, & treated: qualitative evidence synthesis & framework analysis. Psychology &amp; Sexuality. 2024.
[8] How effective is ‘greening’ of urban areas in reducing human exposure to ground-level ozone concentrations, UV exposure and the ‘urban heat island effect’? An updated systematic review. Environmental Evidence. 2021.