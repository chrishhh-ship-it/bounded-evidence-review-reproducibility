## 检索与筛选概览

本合成基于提供的8篇摘要级证据，旨在探讨何种查询（query）最能区分“citation discipline”（引用纪律）与“semantic faithfulness”（语义忠实度）两类能力。检索范围涵盖生物医学文献检索、引文推荐、多智能体系统及语义变量等领域。筛选后，核心相关证据集中于[1]、[2]、[3]三篇，它们直接涉及引用准确性、语义对齐及证据基础推荐，其余文献[4]-[8]虽涉及语义或多智能体主题，但未直接讨论查询设计对两类能力的区分作用。

## 核心主题与证据

现有研究表明，查询的**领域特异性**和**证据基础性**是区分两类能力的关键。在CASPER系统中，针对颅面外科的25个临床问题，系统在儿科气道（0.93）、面部创伤（0.93）和肿瘤外科（0.95）等成熟领域取得高语义相似度（SEM-eval），而在复杂或新兴领域如Le Fort III禁忌症（0.81）和面部女性化规划（0.81）得分较低[1]。这表明**高领域特异性查询**（如“Pierre-Robin下颌牵引术”）能同时测试引用纪律（需精确匹配专业文献）和语义忠实度（需与检索文档高度对齐），而模糊或跨领域查询则难以区分两者。

LITERAS系统进一步揭示，**要求精确引用元数据的查询**（如“提供2023-2024年Q1期刊的随机对照试验”）能显著区分两类能力：LITERAS在引用准确性（99.82%）和引用一致性（96.81%）上表现优异，而Perplexity AI的Sonar虽引用准确性高（100%），但包含35.60%非学术来源[2]。这说明**对引用来源质量（如期刊等级、同行评审状态）的查询约束**能有效分离“引用纪律”（仅引用真实、可验证文献）与“语义忠实度”（生成内容与检索文档语义匹配）。

ILCiteR系统则引入**证据跨度检索**任务，要求查询不仅推荐论文，还需提供支持性证据跨度[3]。这种**需要证据锚定的查询**（如“引用支持‘某药物疗效’的论文并提取相关句子”）能强制系统同时展示引用纪律（证据必须来自真实文献）和语义忠实度（证据跨度必须与查询语义一致），从而暴露两类能力的分离情况。

## 证据支持的研究方向

基于上述证据，以下查询类型最可能有效区分两类能力：

1. **高领域特异性+低资源查询**：如“罕见病手术禁忌症”，此类查询在CASPER中得分最低[1]，表明语义忠实度（生成合理内容）可能高于引用纪律（找到精确文献），从而暴露差距。
2. **多约束引用质量查询**：如“仅引用2023年后影响因子>10的期刊论文”，LITERAS实验显示此类查询会导致不同系统在引用纪律（Sonar-Pro偏好高IF期刊）和语义忠实度（LITERAS更关注近期文献）上产生分歧[2]。
3. **证据跨度验证查询**：要求系统同时输出推荐论文和支撑证据，ILCiteR框架显示此类查询能直接检验引用纪律（证据是否来自推荐论文）与语义忠实度（证据是否匹配查询语义）[3]。

## 摘要级证据的局限

本合成仅依赖摘要级信息，存在以下局限：首先，CASPER[1]和LITERAS[2]的评估指标（SEM-eval、引用准确性）定义不完整，无法判断其是否真正分离了“引用纪律”与“语义忠实度”；其次，ILCiteR[3]为预印本，未经同行评审，其任务设计可能未覆盖真实场景中的查询多样性；最后，[4]-[8]的摘要未提供与查询设计相关的具体数据，无法用于直接分析。

## 谨慎结论

综合现有摘要级证据，**高领域特异性、多约束引用质量、以及需要证据锚定的查询**最可能有效区分“引用纪律”与“语义忠实度”两类能力。具体而言，针对低资源或新兴领域的精确查询（如CASPER中的Le Fort III禁忌症）能暴露语义忠实度高于引用纪律的倾向；而要求严格引用来源质量的查询（如LITERAS中的期刊等级约束）则能突出引用纪律的差异。然而，由于缺乏对两类能力的直接对比实验，且证据来源有限，上述结论需在更系统的实证研究中验证。

## 参考文献
[1] Specialty-Specific Citation-Enabled AI Clinical Decision Support System for Craniofacial Surgery: Development of CASPER.. The Journal of craniofacial surgery. .
[2] LITERAS: Biomedical literature review and citation retrieval agents. Comput. Biol. Medicine. 2025.
[3] ILCiteR: Evidence-grounded Interpretable Local Citation Recommendation. arXiv Preprint. 2024.
[4] Using semantic components to represent dynamics of an interdisciplinary healthcare team in a multi-agent decision support system. S Wilk, M Kezadri-Hamiaz, D Rosu… - Journal of medical …, 2016 - Springer. 2016.
[5] Multi-agent semantic interoperability in complex energy systems simulation and decision support. G Santos, T Pinto, Z Vale… - … Conference on Intelligent …, 2019 - ieeexplore.ieee.org. 2019.
[6] Parrot: Efficient Serving of LLM-based Applications with Semantic Variable. arXiv (Cornell University). 2024.
[7] Understanding the Corpus of Mobile Payment Services Research: An Analysis of the Literature Using Co-Citation Analysis and Social Network Analysis. Journal of Information Systems and Technology Management. 2020.
[8] Building custom, adaptive and heterogeneous multi-agent systems for semantic information retrieval using organizational-multi-agent systems engineering, O-MaSE. 2016 2nd International Conference on Advances in Computing, Communication, &amp; Automation (ICACCA) (Fall). 2016.