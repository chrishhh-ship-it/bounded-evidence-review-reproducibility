## 1. 检索与筛选概览

本合成基于提供的8篇摘要级证据，围绕“same-model ARL与cross-model ARL的成本收益差异在实验中的报告方式”这一研究问题进行系统梳理。所涉文献涵盖大语言模型（LLM）的跨学科评估[1]、医疗应用框架[2]、跨语言命名实体识别基准[3]、通信领域模型适应[4]、城市韧性综述[5]、纳米材料视觉语言模型[6]、异构联邦学习[7]以及法律多智能体系统[8]。经筛选，直接涉及模型内（same-model）与跨模型（cross-model）比较的证据主要来自[3]、[4]、[6]、[7]和[8]，其余文献提供间接背景支撑。

## 2. 核心主题与证据

**2.1 模型内适应（same-model ARL）的成本收益**  
[4]提出LLM4SG方法，采用低秩适应（LoRA）对骨干网络进行任务导向微调，仅选择性地微调部分层以保留通用知识并降低训练成本。该方法在跨条件泛化测试中显著优于传统深度学习模型，表明same-model适应在保持预训练知识的同时，能以较低计算成本获得高性能收益。[6]开发的SEM-VLM通过对比学习在文献图像-文本对上进行领域特定适应，仅用2.1%训练标签即超越全监督模型，展示了same-model适应在标签稀缺场景下的显著成本效益。

**2.2 跨模型协作（cross-model ARL）的成本收益**  
[7]提出FedMD框架，通过迁移学习和知识蒸馏实现异构联邦学习，允许各参与方独立设计模型。实验表明，10个不同模型协作后平均测试准确率提升20%，仅比数据池化场景低几个百分点，揭示了跨模型协作在保护知识产权和隐私前提下的显著收益。[8]的Chatlaw系统采用混合专家（MoE）模型，通过不同专家处理不同法律问题，在Lawbench和统一法律职业资格考试中分别比GPT-4准确率高7.73%和11分，展示了跨模型架构在专业领域的性能优势。

**2.3 跨模型与模型内适应的比较证据**  
[3]对多种多语言大模型进行基准评估，发现GigaBERT在阿拉伯语跨语言NER中表现最优，而语言自适应预训练（LAPT）是最有效的适应方法。该研究直接比较了不同模型（cross-model）与同一模型的不同适应方法（same-model），指出融入语言特定知识对提升远距离语言对（如英-阿）性能至关重要。[2]提出的评估框架将LLM应用分为三类，指出不同类别面临的理解缺失、不可预测性和共情缺失等根本局限，为比较不同模型策略的成本收益提供了分析维度。

## 3. 证据支持的研究方向

**3.1 成本收益的量化指标**  
实验应报告以下指标：准确率/性能增益（如[7]的20%提升、[8]的7.73%准确率优势）、训练成本（如[4]的LoRA微调层数选择）、标签依赖程度（如[6]的2.1%训练标签）、泛化能力（如[4]的跨条件测试、[3]的跨语言评估）。

**3.2 实验设计要素**  
- **基线设置**：应包含same-model适应（如LoRA、LAPT）与cross-model协作（如FedMD、MoE）的对比基线[3][4][7]。  
- **场景覆盖**：需考虑不同数据规模（如[6]的少样本与全监督对比）、领域差异（如[1]的学科间性能差异）、语言距离（如[3]的英-阿远距离对）。  
- **成本报告**：应明确计算资源、标注成本、模型复杂度等维度，如[4]报告LoRA减少训练成本、[6]报告标签需求降低数量级。

**3.3 报告规范建议**  
- 采用[2]的分类框架明确应用类别（如监督输出、行政输出），并针对不同类别报告相应的根本局限（理解缺失、不可预测性）。  
- 参考[1]的跨学科比较方法，报告same-model与cross-model策略在不同领域（如自然科学与人文学科）的性能差异及统计显著性（如P值）。  
- 遵循[7]的联邦学习报告标准，明确参与模型数量、数据分布、隐私保护机制等。

## 4. 摘要级证据的局限

本合成仅基于摘要级证据，存在以下局限：  
- **细节缺失**：无法获取完整实验设置、超参数配置、统计检验方法等关键信息，如[4]的LoRA秩参数、[7]的蒸馏温度设置。  
- **领域偏差**：证据主要来自通信[4]、材料[6]、法律[8]等特定领域，可能不适用于其他领域（如医疗[2]）。  
- **时效性**：部分文献为预印本（如[7][8]），未经同行评审，结论可能随后续研究调整。  
- **比较框架不统一**：各研究采用不同的评估指标和实验条件，直接比较same-model与cross-model策略的成本收益存在方法论挑战。

## 5. 谨慎结论

基于现有摘要级证据，same-model ARL（如LoRA、LAPT）在保留预训练知识、降低训练成本方面具有优势，特别适用于标签稀缺场景[4][6]；cross-model ARL（如FedMD、MoE）在利用多模型互补知识、提升专业领域性能方面表现突出[7][8]。实验报告应系统量化性能增益、计算成本、数据需求等维度，并参考[2]的框架明确应用类别与根本局限。然而，由于证据的领域局限和细节缺失，上述结论需在完整论文验证和跨领域复现后进一步确认。建议未来研究建立统一的成本收益报告标准，涵盖模型复杂度、训练时间、推理效率、泛化能力等综合指标。

## 参考文献
[1] Evaluation of Large Language Model Performance and Reliability for Citations and References in Scholarly Writing: Cross-Disciplinary Study.. Journal of medical Internet research. 2024.
[2] A Framework for Critically Assessing ChatGPT and Other Large Language Artificial Intelligence Model Applications in Health Care. Mayo Clinic Proceedings Digital Health. 2023.
[3] A Benchmark Evaluation of Multilingual Large Language Models for Arabic Cross-Lingual Named-Entity Recognition. Electronics. 2024.
[4] LLM4SG: Adapting Large Language Model for Scatterer Generation via Synesthesia of Machines. Semantic Scholar. 2025.
[5] Multi-dimensional Construction of Urban Climate ResilienceA Systematic Review of Infrastructure, Governance Model and Financial Mechanism. Advances in Economics, Management and Political Sciences. 2026.
[6] A visual language model enabling intelligent nanomaterial scanning electron micrograph annotation.. Nanoscale. 2025.
[7] FedMD: Heterogenous Federated Learning via Model Distillation. arXiv (Cornell University). 2019.
[8] Chatlaw: A Multi-Agent Collaborative Legal Assistant with Knowledge Graph Enhanced Mixture-of-Experts Large Language Model. arXiv (Cornell University). 2023.