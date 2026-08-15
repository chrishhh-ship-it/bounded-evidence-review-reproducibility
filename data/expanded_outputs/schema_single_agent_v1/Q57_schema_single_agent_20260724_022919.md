## 学术智能综合报告

### 1. 检索与筛选概览

本报告基于提供的8篇文献证据，围绕“区分 citation discipline（引文纪律/引用准确性）与 semantic faithfulness（语义忠实度）两类能力的最佳 query 类型”这一研究问题展开分析。所检索的文献覆盖了生物医学文献检索、引文推荐、多智能体系统、语义变量应用等多个领域，时间跨度从2016年至2025年。经过筛选，其中[1]、[2]、[3]三篇文献直接涉及引文准确性与语义对齐能力的评估，构成了本报告的核心证据基础；其余文献[4]-[8]虽涉及语义或多智能体相关主题，但与核心研究问题的直接关联性较弱，仅作为背景或对比参考。

### 2. 核心主题与证据

现有证据表明，区分“引文纪律”与“语义忠实度”两类能力的关键在于 query 的设计特征。具体而言：

- **需要高精度引文验证的 query** 最能暴露引文纪律的缺陷。例如，[2]中LITERAS系统在生物医学文献检索任务中，通过要求系统提供可确认的真实出版物引用（而非虚构或灰色文献），实现了99.82%的引文准确率，显著优于对比系统在非学术来源上的表现（Sonar含35.60%非学术来源，p<0.01）。这表明，要求系统提供可验证的、来自高影响力期刊的引文，是测试引文纪律的有效 query 类型。

- **涉及复杂、新兴或跨学科领域的 query** 最能挑战语义忠实度。[1]中CASPER系统在颅面外科领域的评估显示，在“Le Fort III禁忌症”（语义相似度0.81）和“面部女性化规划”（0.81）等复杂或新兴领域，语义对齐得分显著低于儿科气道（0.93）等成熟领域。这表明，需要跨学科知识整合或缺乏充足训练数据的 query，会显著降低系统的语义忠实度。

- **同时要求引文准确性与语义对齐的 query** 能够同时区分两种能力。[3]中ILCiteR系统提出的“证据基础本地引文推荐”任务，要求系统不仅推荐相关论文，还需提供与 query 语义相似的证据片段，从而同时评估引文纪律（推荐论文的真实性）和语义忠实度（证据片段与 query 的对齐程度）。这种双重要求的 query 设计，能够更全面地揭示系统在两种能力上的表现差异。

### 3. 证据支持的研究方向

基于上述证据，以下研究方向具有明确的证据支持：

- **设计多维度评估 query 集**：结合[1]和[2]的发现，应构建包含“高引文验证要求”与“复杂语义对齐要求”两类 query 的评估集，以系统性地分离两种能力。例如，在生物医学领域，可设计既要求引用特定临床试验（高引文纪律）又要求解释其与罕见病例的语义关联（高语义忠实度）的 query。

- **开发可解释的引文推荐系统**：[3]提出的证据基础推荐框架，通过将推荐结果与可验证的证据片段绑定，为同时提升引文纪律和语义忠实度提供了可行路径。未来研究可探索如何将这种机制扩展到更多领域。

- **领域特异性分析**：[1]和[2]均显示，不同医学子领域（如肿瘤学 vs. 儿科气道）在两种能力上的表现存在显著差异。这提示，query 的领域特异性（如罕见病 vs. 常见病）可能是调节两种能力相对重要性的关键变量。

### 4. 摘要级证据的局限

本报告所依赖的证据均为摘要级信息，存在以下固有局限：

- **方法细节缺失**：例如[1]中CASPER系统的“语义相似度（SEM-eval）”具体计算方式未在摘要中说明，无法判断其是否真正反映了语义忠实度而非简单的词汇重叠。[2]中LITERAS的“引文准确率”定义（是否匹配真实出版物）虽较清晰，但未说明如何处理部分匹配或版本差异。

- **评估范围有限**：所有核心证据均来自生物医学领域，[1]仅涉及颅面外科，[2]覆盖五个医学领域但未包括非医学领域。因此，关于 query 类型与能力区分关系的结论可能无法直接推广到其他学科（如工程学、社会科学）。

- **缺乏对比基准**：[3]虽提出了新颖的任务框架，但摘要未提供与现有引文推荐系统的定量对比，无法判断其方法在区分两种能力上的实际增益。

- **潜在的选择性报告**：摘要可能仅报告了有利结果。例如[1]中CASPER在复杂领域的低分（0.81）被提及，但未说明这些低分是否源于引文纪律问题还是语义理解问题。

### 5. 谨慎结论

综合现有摘要级证据，可以初步推断：**要求系统提供可验证的、来自高影响力期刊的引文，并同时要求其输出与 query 在语义上紧密对齐的证据片段，是设计区分“引文纪律”与“语义忠实度”两类能力的最有效 query 类型**。具体而言，涉及复杂、新兴或跨学科领域的 query 最能暴露语义忠实度的不足，而需要精确引文验证的 query 则最能揭示引文纪律的缺陷。然而，由于证据主要来自生物医学领域且均为摘要级信息，上述结论应被视为初步假设而非定论。未来研究需在更多学科、使用完整论文信息、并采用标准化评估指标（如引文准确率与语义相似度的联合指标）来验证和细化这一发现。

## 参考文献
[1] Specialty-Specific Citation-Enabled AI Clinical Decision Support System for Craniofacial Surgery: Development of CASPER.. The Journal of craniofacial surgery. .
[2] LITERAS: Biomedical literature review and citation retrieval agents. Comput. Biol. Medicine. 2025.
[3] ILCiteR: Evidence-grounded Interpretable Local Citation Recommendation. arXiv Preprint. 2024.
[4] Using semantic components to represent dynamics of an interdisciplinary healthcare team in a multi-agent decision support system. S Wilk, M Kezadri-Hamiaz, D Rosu… - Journal of medical …, 2016 - Springer. 2016.
[5] Multi-agent semantic interoperability in complex energy systems simulation and decision support. G Santos, T Pinto, Z Vale… - … Conference on Intelligent …, 2019 - ieeexplore.ieee.org. 2019.
[6] Parrot: Efficient Serving of LLM-based Applications with Semantic Variable. arXiv (Cornell University). 2024.
[7] Understanding the Corpus of Mobile Payment Services Research: An Analysis of the Literature Using Co-Citation Analysis and Social Network Analysis. Journal of Information Systems and Technology Management. 2020.
[8] Building custom, adaptive and heterogeneous multi-agent systems for semantic information retrieval using organizational-multi-agent systems engineering, O-MaSE. 2016 2nd International Conference on Advances in Computing, Communication, &amp; Automation (ICACCA) (Fall). 2016.