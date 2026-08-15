### 1. 检索与筛选概览

本合成基于提供的八篇摘要级证据，这些文献均来自2021年至2025年间发表的系统综述或预印本。证据来源涵盖医学、公共卫生、人工智能与证据综合等多个领域，包括《Journal of Family Violence》、《Environmental Evidence》、《The Journal of Headache and Pain》等同行评审期刊，以及medRxiv和arXiv等预印本平台。所有文献均遵循PRISMA等系统综述报告规范，并采用了双人独立筛选、一致性检验等质量控制措施[1][2][3][5][6]。然而，这些摘要主要聚焦于各自领域的应用结果，并未专门针对半自动化系统综述流程中的人机交互检查点设计进行深入探讨。

### 2. 核心主题与证据

现有证据一致强调，在自动化或半自动化文献筛选流程中，**人类监督（human oversight）是不可或缺的**，尤其是在防止错误纳入（如虚构文献）方面。具体而言：

- **可靠性阈值与角色分工**：一项针对定制GPT（cGPT）在全文筛选中可靠性的评估发现，cGPT作为“第二审稿人助理”时，其与人类共识的一致性（kappa=0.733）达到了人类-人类配对的一致性区间（0.713–0.784），而作为“自主审稿人”或“第一审稿人助理”时则未达到实用阈值[2]。这表明，将AI定位为辅助角色而非替代角色，是维持筛选可靠性的关键检查点。

- **人类监督的必要性**：多项研究明确指出，AI工具在临床决策和证据综合中应“补充而非取代临床判断”[5]，且“人类监督仍然至关重要”[5]。在自动化元分析领域，尽管AI在数据处理（57%）方面表现突出，但在高级综合阶段（如偏倚评估、异质性分析）的自动化程度极低（仅17%），且仅有一项研究探索了初步的全流程自动化[6]。这暗示，在涉及质量评估和纳入决策的关键环节，必须设置人工复核检查点。

- **一致性与质量控制**：传统系统综述中，通过双人独立筛选和一致性检验（如Cohen's kappa）来确保纳入的准确性[2][3][5]。这些方法同样适用于半自动化流程：当AI作为辅助工具时，其输出应与至少一名人类审稿人的决策进行交叉验证，并计算一致性指标[2]。此外，在标题/摘要筛选和全文筛选阶段，设置“不一致裁决”检查点（如由第三位审稿人或资深专家介入）是防止错误纳入的常见做法[3][5]。

### 3. 证据支持的研究方向

基于现有证据，以下研究方向对于构建防止虚构文献纳入的半自动化系统综述检查点至关重要：

- **AI辅助角色的标准化阈值研究**：需要建立统一的、跨领域的可靠性阈值标准，以判断AI在何种角色（如助理、审稿人）下可被安全地整合到筛选流程中[2][5]。当前的研究仅针对特定模型（cGPT）和特定数据集，缺乏通用性。

- **人机协作的检查点设计**：应系统研究在筛选流程的哪些阶段（标题筛选、摘要筛选、全文筛选、质量评估）设置人工干预点最为有效。例如，当AI的置信度低于某一阈值时，自动触发人工复核[2][6]。

- **针对“虚构文献”的检测机制**：现有研究主要关注AI的误判（如错误排除或纳入），但未专门探讨AI可能“虚构”或“幻觉”出文献标题或摘要的问题。未来需开发专门的检测算法或检查点，例如要求AI提供纳入决策的引用来源或逻辑链，并由人类验证其真实性[5][6]。

- **多模态与多模型验证**：探索结合不同AI模型（如LLM与专用分类器）或不同提示策略，通过交叉验证来降低单一模型产生虚构输出的风险[2][6]。

### 4. 摘要级证据的局限

本合成完全依赖于摘要级信息，存在以下固有局限：

- **缺乏方法学细节**：摘要未提供关于“人类监督检查点”具体操作流程的详细描述，例如人工复核的样本比例、不一致时的裁决机制、以及如何定义“虚构文献”或“错误纳入”[1][2][3]。这些细节通常仅在全文的方法部分出现。

- **领域特异性**：大多数证据来自医学或特定领域（如头痛医学、放射肿瘤学、老年康复）[4][5][8]，其关于AI可靠性的发现可能无法直接推广到其他学科（如社会科学或环境科学）的系统综述中。

- **预印本与灰色文献**：部分证据来自未经同行评审的预印本（如medRxiv和arXiv）[2][6][7]，其结论可能尚未经过充分验证，存在不确定性。

- **未直接回答研究问题**：没有任何一篇摘要直接探讨“如何防止虚构文献通过半自动化筛选”，而是间接提供了关于AI可靠性、人类监督必要性和质量控制方法的相关证据。因此，本合成是基于间接证据的推断。

### 5. 谨慎结论

综合现有摘要级证据，在半自动化系统综述流程中，为防止虚构文献通过筛选阶段，至少需要设置以下人类监督检查点：

1.  **角色定义检查点**：明确AI仅作为“辅助工具”或“第二审稿人助理”，而非自主决策者[2][5]。
2.  **一致性验证检查点**：在标题/摘要筛选和全文筛选后，计算AI与人类审稿人的一致性（如kappa值），并设定一个低于人类-人类一致性下限的阈值作为“警报线”[2]。
3.  **不一致裁决检查点**：当AI与人类决策不一致时，必须由第三位独立审稿人或资深专家进行仲裁[3][5]。
4.  **质量与偏倚评估检查点**：在纳入文献的质量评估和偏倚风险评估阶段，必须由人类专家主导，因为当前AI在此阶段的自动化能力极为有限[6]。
5.  **来源真实性验证检查点**：要求AI在推荐纳入时提供明确的、可追溯的文献来源（如DOI或稳定ID），并由人类随机抽样验证其真实性，以防范“幻觉”或虚构引用[5][6]。

这些检查点应嵌入到系统综述的标准化工作流中，并定期进行校准和验证。鉴于当前证据的局限性，强烈建议在实施前进行试点研究，并参考全文文献以获取更详细的操作指南。

## 参考文献
[1] What are the Factors Influencing Service Provider Response to Working with Families Affected by Intimate Partner Violence and Abuse? A Qualitative Systematic Review of the Literature. Journal of Family Violence. 2024.
[2] Evaluating the Reliability of a Custom GPT in Full-Text Screening of a Systematic Review. medRxiv. 2025.
[3] How effective is ‘greening’ of urban areas in reducing human exposure to ground-level ozone concentrations, UV exposure and the ‘urban heat island effect’? An updated systematic review. Environmental Evidence. 2021.
[4] Leveraging human-robot interaction and virtual reality for digital biomarkers in diagnostics and rehabilitation: a review from the Age-It Research Program.. The journals of gerontology. Series B, Psychological sciences and social sciences. 2025.
[5] Artificial intelligence in headache medicine: between automation and the doctor-patient relationship. A systematic review. The Journal of Headache and Pain. 2025.
[6] Transforming Evidence Synthesis: A Systematic Review of the Evolution of Automated Meta-Analysis in the Age of AI. arXiv.org. 2025.
[7] Machines in the Margins: A Systematic Review of Automated Content Generation for Wikipedia. arXiv Preprint. 2025.
[8] The continuous improvement of digital assistance in the radiation oncologist's work: from web-based nomograms to the adoption of large-language models (LLMs). A systematic review by the young group of the Italian association of radiotherapy and clinical oncology (AIRO).. La Radiologia medica. 2024.