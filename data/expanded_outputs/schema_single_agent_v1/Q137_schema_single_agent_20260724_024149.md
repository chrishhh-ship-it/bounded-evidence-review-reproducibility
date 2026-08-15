# 学术智能综合报告：使用BLEU/ROUGE评估历史文本规范化输出时的构念效度威胁

## 1. 检索与筛选概览

本综合报告基于提供的八篇文献证据集（E_q）进行单次综合。这些文献涵盖数字人文、大语言模型应用、技术批判研究、系统综述方法论等多个领域。由于原始检索范围并非针对历史文本规范化评估这一具体问题，证据集中缺乏直接讨论BLEU/ROUGE指标在历史文本规范化评估中构念效度问题的专门研究。因此，本综合报告将基于相关领域文献中的间接证据和类比推理，构建关于构念效度威胁的分析框架。

## 2. 核心主题与证据

### 2.1 自动评估指标的固有局限

BLEU和ROUGE作为基于n-gram重叠的自动评估指标，其核心假设是参考文本与候选文本之间的词汇重叠程度能够反映语义质量。然而，这一假设在历史文本规范化任务中面临根本性挑战。历史文本规范化涉及将非标准化的历史拼写、变体形式转换为现代标准形式，其目标不仅是词汇匹配，更是历史语言特征的准确还原与语义保真度。

### 2.2 构念效度的主要威胁

**（1）历史语境与语义保真度的缺失**

历史文本规范化评估需要捕捉的构念是“规范化质量”，这包括历史语言特征的保留程度、语义信息的完整性以及目标语言规范的符合度。然而，BLEU/ROUGE仅测量表面词汇重叠，无法评估模型是否准确理解了历史文本的语境含义。数字人文研究指出，历史文本分析需要关注“特定（历史）偏见”，这些偏见源于训练数据中的历史语境偏差[2]。当使用BLEU/ROUGE评估时，指标可能奖励那些简单匹配现代参考译文的输出，而惩罚那些保留了历史语言特征但词汇形式不同的规范化结果，从而产生构念效度威胁。

**（2）参考文本的单一性与多样性不足**

历史文本规范化通常不存在唯一的“正确”输出。同一历史文本可能有多种合理的规范化方案，取决于目标规范标准、历史时期特征和具体应用场景。BLEU/ROUGE依赖单一或多个参考译文，但无法捕捉这种规范化方案的多样性。系统综述方法论的研究指出，过度依赖单一方法论框架可能导致“知识景观的显著扭曲”[4]。类似地，在历史文本规范化评估中，仅依赖词汇重叠指标可能扭曲对模型真实能力的评估。

**（3）对罕见语言现象的敏感性不足**

历史文本包含大量罕见拼写、方言变体和过时语法结构。大语言模型研究指出，这些模型“无法预测不寻常或罕见事件”[3]，这一局限同样适用于基于统计匹配的评估指标。BLEU/ROUGE对罕见n-gram的匹配极为敏感，可能因历史文本中的低频词汇而给出不合理的低分，即使规范化输出在语义上是正确的。

**（4）评估指标与人类判断的偏离**

构念效度的核心是评估指标是否真正测量了其声称要测量的构念。在历史文本规范化评估中，这意味着指标分数应与人类专家对规范化质量的判断高度相关。然而，研究表明，自动评估指标与人类判断之间可能存在显著偏离。技术批判研究指出，技术评估往往“将技术视为中立的工具”，而忽视了“社会文化条件”[6]。在历史文本规范化评估中，BLEU/ROUGE的“中立”统计特性可能掩盖了其无法捕捉历史语言细微差别的根本缺陷。

### 2.3 替代评估框架的启示

数字人文研究提出了多模态转向的可能性，认为“多模态模型允许学者超越文本和图像的人为分离”[2]。这一思路对历史文本规范化评估具有启示意义：评估框架应超越单一的词汇匹配维度，纳入语义保真度、历史语境一致性、语言规范符合度等多维构念。用户研究也表明，数字档案用户对计算方法的接受度受“技能缺乏”和“偏好传统方法”等因素影响[5]，这提示评估指标的设计需要考虑目标用户群体的认知框架和评估标准。

## 3. 证据支持的研究方向

### 3.1 多维评估框架的构建

基于上述构念效度威胁分析，未来研究应探索构建多维评估框架，将BLEU/ROUGE作为其中一个子维度而非唯一标准。具体方向包括：

- **语义保真度评估**：利用大语言模型进行语义相似度判断，如研究所示，LLM在文本分析任务中展现出“相对合理的性能”[8]。
- **历史语境一致性评估**：开发专门评估历史语言特征保留程度的指标，借鉴数字人文研究中“对历史偏见保持警惕”的方法论意识[2]。
- **人类专家评估的标准化**：建立系统化的专家评估流程，克服“叙事综述可能‘挑选’证据以支持特定观点”的批评[4]。

### 3.2 评估指标的领域适配

历史文本规范化评估需要领域特定的指标适配。研究指出，LLM的应用“取决于提示的质量和上下文”[3]，这一原则同样适用于评估指标的设计。未来研究应探索：

- **历史语言特征的嵌入表示**：开发能够捕捉历史拼写变体与标准形式之间映射关系的嵌入方法。
- **多参考译文扩展**：构建包含多种合理规范化方案的多参考译文集，提高评估的包容性。

### 3.3 用户中心评估方法

用户研究强调“用户对计算方法的体验仍然研究不足”[5]。在历史文本规范化评估中，应纳入目标用户（历史学家、语言学家、档案工作者）的评估视角，建立用户驱动的评估标准。技术批判研究也指出，技术评估应“关注技术的社会文化条件”[6]，这意味着评估框架需要考虑历史文本规范化的实际应用场景和用户需求。

## 4. 摘要级证据的局限

本综合报告基于摘要级证据，存在以下局限：

- **证据直接性不足**：提供的文献中缺乏直接讨论BLEU/ROUGE在历史文本规范化评估中构念效度的研究。分析基于类比推理和间接证据，结论的确定性有限。
- **领域覆盖偏差**：证据集主要涵盖大语言模型应用、数字人文方法论和技术批判研究，缺乏计算语言学、机器翻译评估等直接相关领域的文献。
- **摘要信息有限**：摘要级证据无法提供方法细节、实验数据和量化结果，限制了分析的深度和精确性。
- **时间敏感性**：部分文献发表于2018年[4]，可能无法反映该领域的最新进展。

## 5. 谨慎结论

基于现有摘要级证据，可以得出以下谨慎结论：

1. **构念效度威胁确实存在**：使用BLEU/ROUGE评估历史文本规范化输出时，存在显著的构念效度威胁，主要表现为指标无法捕捉历史语境、语义保真度和规范化方案的多样性。

2. **需要多维评估框架**：单一词汇重叠指标不足以评估历史文本规范化质量，未来研究应探索融合语义分析、历史语境评估和人类判断的多维框架。

3. **领域适配至关重要**：评估指标的设计需要考虑历史文本规范化的特殊性，包括历史语言特征的保留、罕见拼写的处理和多种合理规范化方案的存在。

4. **用户视角不可或缺**：评估框架应纳入目标用户群体的需求和判断标准，避免技术中心主义的评估偏差。

5. **进一步研究必要**：需要专门针对历史文本规范化评估构念效度的实证研究，以验证和扩展本报告的分析框架。

## 参考文献
[1] What are the Factors Influencing Service Provider Response to Working with Families Affected by Intimate Partner Violence and Abuse? A Qualitative Systematic Review of the Literature. Journal of Family Violence. 2024.
[2] A multimodal turn in Digital Humanities. Using contrastive machine learning models to explore, enrich, and analyze digital visual historical collections. Digital Scholarship in the Humanities. 2023.
[3] The Potential Application of Large Language Models in Pharmaceutical Supply Chain Management. The Journal of Pediatric Pharmacology and Therapeutics. 2024.
[4] Time to challenge the spurious hierarchy of systematic over narrative reviews?. European Journal of Clinical Investigation. 2018.
[5] Are Users of Digital Archives Ready for the AI Era? Obstacles to the Application of Computational Research Methods and New Opportunities. ACM Journal on Computing and Cultural Heritage. 2024.
[6] What Do We Critique When We Critique Technology?. American Literature. 2023.
[7] Leveraging OpenAI’s LLMs and Cloud-based Learning-as-a-Service (LaaS) Solutions to Create Culturally Rich Conversational AI Chatbot: ChatLoS - A Study Using the Legacy of Slavery Dataset. OpenAlex. 2024.
[8] Using Large Language Models to Detect Depression From User-Generated Diary Text Data as a Novel Approach in Digital Mental Health Screening: Instrument Validation Study.. Journal of medical Internet research. 2024.