# 学术智能合成报告

## 1. 检索与筛选概览

本合成基于给定的8篇文献证据集（E_q），围绕“在benchmark规模有限的情况下，bootstrap与paired t-test分别适合回答什么问题”这一研究查询展开分析。所涉文献涵盖化学推理基准[1]、多智能体协作评估[2]、生物医学语言理解[3]、诊断数据提取可靠性[4]、临床笔记质量评估[5]、人口统计学偏差审计[6]、代码审查智能体评估[7]以及深度研究智能体评估[8]等多个领域。这些文献均涉及不同规模benchmark下的评估方法论，为分析有限规模benchmark场景下的统计推断策略提供了多角度的证据基础。

## 2. 核心主题与证据

### 2.1 Benchmark规模有限带来的评估挑战

在多个研究领域中，benchmark规模受限是一个普遍存在的实际问题。例如，在化学推理评估中，ChemPaperBench虽然覆盖多学科，但其任务规模受限于专家验证的合成任务[1]；在诊断数据提取研究中，评估仅基于固定语料库，单系统运行20次，共产生320个数据集-运行观测值[4]；在临床笔记质量评估中，实验设计采用合成案例与针对性扰动，样本量同样有限[5]。这些案例表明，当benchmark规模有限时，如何从有限样本中得出可靠的统计推断成为核心方法论问题。

### 2.2 Paired t-test的适用场景

Paired t-test适用于比较同一组系统在相同条件下的配对观测值差异，其核心假设是观测值之间具有配对关系且差异近似正态分布。在benchmark规模有限但可进行重复运行（repeated runs）的场景下，paired t-test具有明确优势：

- **系统间比较**：在诊断数据提取基准研究中，研究者对每个系统执行20次独立运行，这种设计天然支持配对比较[4]。通过配对设计，可以控制不同系统在相同测试集上的随机波动，从而更敏感地检测系统间的性能差异。
- **前后对比**：在人口统计学偏差审计中，研究者对同一模型在不同人口统计学变体下的诊断准确性进行比较，采用McNemar配对分析（一种针对分类数据的配对检验方法）[6]，这与paired t-test在配对连续数据上的应用逻辑一致。
- **提示策略比较**：在生物医学语言理解基准中，研究者系统性地比较不同提示策略对同一模型性能的影响[3]，这种同一模型在不同条件下的比较适合采用配对设计。

**关键适用条件**：Paired t-test要求观测值可配对（如同一系统在相同测试集上的多次运行结果），且差异服从正态分布。当benchmark规模有限但可进行多次重复运行时，配对设计能有效提高统计功效。

### 2.3 Bootstrap的适用场景

Bootstrap是一种非参数重采样方法，不依赖正态分布假设，特别适合benchmark规模有限且数据分布未知的场景：

- **置信区间估计**：在人口统计学偏差审计中，研究者使用Wilson 95%置信区间来量化公平性[6]，而bootstrap方法可以替代参数方法，为有限样本下的性能估计提供稳健的置信区间。当benchmark规模较小导致参数方法假设难以满足时，bootstrap通过重采样经验分布来估计统计量的抽样分布。
- **效应量评估**：同一研究中使用Cohen's h效应量来量化性能差距[6]，bootstrap可以用于估计效应量的置信区间，帮助判断观察到的差异是否具有实际意义而非统计假象。
- **非参数假设检验**：在代码审查智能体评估中，研究者发现现有审查智能体仅能解决约40%的任务[7]，这种比例估计的稳定性可以通过bootstrap方法进行评估。当样本量有限时，bootstrap可以模拟多次抽样过程，提供更可靠的推断。
- **稳健性分析**：在深度研究智能体评估中，研究者发现即使领先系统也仅达到68%以下的平均合规率[8]，bootstrap可以用于评估这一估计的稳定性，特别是在rubric评分可能存在主观变异的情况下。

**关键适用条件**：Bootstrap适用于无法假设数据分布、样本量较小、或需要估计复杂统计量（如中位数、分位数、效应量置信区间）的场景。它不依赖配对结构，可以灵活应用于各种评估设计。

### 2.4 两种方法的互补关系

在benchmark规模有限的评估中，paired t-test和bootstrap可以形成互补：

- **配对t检验**侧重于检测系统间或条件间的系统性差异，适用于有明确配对结构的重复测量设计。
- **Bootstrap**侧重于估计统计量的不确定性，适用于分布未知或统计量复杂的情况。

在诊断数据提取研究中，研究者采用非劣效性设计结合精确单侧二项检验[4]，这种设计既包含配对比较的逻辑（与基准阈值比较），又通过精确检验避免了分布假设，体现了两种方法思想的融合。

## 3. 证据支持的研究方向

### 3.1 有限规模benchmark下的统计推断框架

现有证据表明，需要建立针对有限规模benchmark的系统性统计推断框架。在临床笔记质量评估中，研究者建议采用分层策略，将语义指标与LLM-as-evaluator结合，并包含针对性的人工裁决[5]。类似地，在有限规模benchmark中，应明确何时使用参数方法（如paired t-test）与何时使用非参数方法（如bootstrap），并建立相应的样本量规划指南。

### 3.2 重复运行设计的标准化

多个研究均采用了重复运行设计：诊断数据提取研究执行20次运行[4]，人口统计学偏差审计在两种温度设置下运行[6]。这提示在benchmark规模有限时，应标准化重复运行次数，并明确paired t-test所需的配对观测值数量。同时，bootstrap方法可以用于评估重复运行次数是否足够，通过模拟不同重复次数下估计的稳定性来指导实验设计。

### 3.3 效应量与实际意义评估

在人口统计学偏差审计中，研究者不仅报告p值，还报告Cohen's h效应量和最小可检测效应[6]，这为有限规模benchmark下的结果解释提供了范例。当benchmark规模有限导致统计功效不足时，效应量估计（可通过bootstrap获得置信区间）比单纯的显著性检验更具实际意义。

### 3.4 多维度评估的整合

现有benchmark往往从多个维度评估系统性能：化学推理基准评估搜索、提取和推理能力[1]；多智能体基准评估导航、任务执行和协作竞争能力[2]；深度研究基准评估事实基础、推理合理性和清晰度[8]。在有限规模benchmark下，需要整合这些多维度的评估结果，bootstrap可以用于构建多维度性能的综合置信区域，而paired t-test可以用于比较系统在各维度上的差异。

## 4. 摘要级证据的局限

本合成基于摘要级证据，存在以下固有局限：

- **方法论细节缺失**：摘要通常不报告具体的统计方法选择依据、样本量计算过程、或分布假设检验结果。例如，诊断数据提取研究虽然提及非劣效性设计和精确二项检验[4]，但未说明为何选择该方法而非bootstrap或配对t检验。
- **效应量信息有限**：摘要通常报告p值和置信区间，但较少报告效应量大小及其实际意义。人口统计学偏差审计报告了Cohen's h[6]，但其他研究未提供类似信息，限制了跨研究的方法论比较。
- **样本量信息不完整**：虽然部分研究提及运行次数[4]或样本量[6]，但摘要通常不提供详细的样本量论证或功效分析，难以评估paired t-test或bootstrap在具体场景中的适用性。
- **数据分布特征未知**：摘要不报告性能指标的实际分布特征（如是否正态、是否存在异常值），而这些特征直接影响方法选择。例如，如果性能指标呈现偏态分布，bootstrap可能比paired t-test更合适。
- **研究领域差异**：不同领域的benchmark规模、任务复杂度、评估指标性质差异显著，从化学推理[1]到临床笔记[5]再到代码审查[7]，这些差异可能影响统计方法的选择，但摘要级证据不足以进行细致的领域特异性分析。

## 5. 谨慎结论

基于现有摘要级证据，在benchmark规模有限的情况下，可得出以下谨慎结论：

**Paired t-test**适合回答以下问题：在可进行重复运行的有限规模benchmark中，同一系统在不同条件（如不同提示策略、不同温度设置）下的性能是否存在系统性差异？或不同系统在同一测试集上的平均性能是否存在显著差异？其适用前提是观测值可配对且差异近似正态分布。

**Bootstrap**适合回答以下问题：在有限规模benchmark中，系统性能估计的不确定性有多大？观察到的性能差异是否稳健？效应量的置信区间是多少？其优势在于不依赖分布假设，适用于样本量小、分布未知或统计量复杂的情况。

两种方法并非互斥，而是可以互补使用：paired t-test提供假设检验框架，bootstrap提供不确定性量化工具。在实践应用中，建议根据benchmark的具体特征（样本量、配对结构、数据分布）选择合适的方法，并优先报告效应量及其置信区间而非仅依赖p值。

需要强调的是，本结论基于摘要级证据，缺乏对具体统计方法选择依据、数据分布特征和样本量论证的深入分析。未来研究应在完整论文层面系统比较不同统计方法在有限规模benchmark中的表现，并建立领域特异性的方法论指南。

## 参考文献
[1] ChemPaperBench: A Multi-Domain Benchmark for Literature-Grounded Chemical Reasoning of LLM-Based Multi-Agent Systems. 2025 IEEE International Conference on Data Mining Workshops (ICDMW). 2025.
[2] BattleAgentBench: A Benchmark for Evaluating Cooperation and Competition Capabilities of Language Models in Multi-Agent Systems. arXiv Preprint. 2024.
[3] Evaluation of large language model performance on the Biomedical Language Understanding and Reasoning Benchmark. medRxiv. 2024.
[4] End-to-End Reliability of Automated Systems for Diagnostic Data Extraction: A Benchmark Study in Uro-Oncologic Evidence Synthesis. CrossRef. 2025.
[5] Measuring the Quality of AI-Generated Clinical Notes: A Systematic Review and Experimental Benchmark of Evaluation Methods. CrossRef. 2025.
[6] Auditing Demographic Bias in Mistral: An Open-Source LLM’s Diagnostic Performance on the MedQA Benchmark. IEEE Access. 2026.
[7] Code Review Agent Benchmark. Semantic Scholar. 2026.
[8] ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents. arXiv.org. 2025.