## 检索与筛选概览

本次检索围绕“负样本测试设计以检验reviewer agent识别错误引用能力”这一研究问题展开。在提供的证据集E_q中，共包含8条记录，涵盖多智能体系统在文献综述、空间文本到SQL转换以及生物建模等领域的应用。其中，[1]和[8]直接涉及多智能体文献综述系统中的作者-审稿人工作流设计；[7]展示了包含执行阶段审查（execution-based review）的多智能体框架；[2]至[6]则主要涉及生物领域的审稿人评论，与核心研究问题的直接相关性较低。经过筛选，[1]、[7]和[8]被确定为最相关的核心证据来源。

## 核心主题与证据

现有证据表明，多智能体系统中的审稿（review）机制已被应用于多个领域以提升输出质量。[1]提出了一个对抗性多智能体系统，用于系统文献综述，其中包含作者-审稿人工作流与可验证证据及批评循环（verifiable evidence and critique loops）。[8]则描述了LatteReview框架，该框架利用大语言模型实现系统综述自动化，其工作流包括由两名初级审稿人代理（junior reviewer agents）进行标题和摘要筛选（A轮），随后由一名更高级的审稿人代理（senior reviewer agent）进行概念提取（B轮）。[7]中的多智能体框架在空间文本到SQL任务中引入了执行阶段审查，结果显示在加入审查阶段后，系统在SpatialQueryQA基准上的准确率从76.7%提升至87.7%，表明审查机制能有效提升系统鲁棒性。

然而，上述证据均未直接涉及“负样本测试”或“识别错误引用”的具体设计方法。现有框架的审查机制主要针对内容质量（如筛选相关性、提取概念）或执行结果（如SQL查询正确性），而非专门检测引用错误。

## 证据支持的研究方向

基于现有证据，可以推断出设计负样本测试以检验reviewer agent识别错误引用能力的几个可能方向：

1. **利用对抗性工作流设计负样本**：[1]中提到的“对抗性多智能体系统”和“可验证证据与批评循环”为设计负样本提供了思路。可以故意在文献综述中插入错误引用（如张冠李戴、虚构引用、引用与论点不匹配等），观察reviewer agent能否在批评循环中识别并标记这些错误。

2. **借鉴分阶段审查流程**：[8]中A轮（初级审稿人）与B轮（高级审稿人）的分级设计提示，负样本测试可以分层进行：初级审稿人负责检测明显错误，高级审稿人负责检测更隐蔽的引用错误。测试可评估不同层级agent的识别能力差异。

3. **参考执行结果验证机制**：[7]中通过执行SQL查询来验证生成结果正确性的方法，可类比应用于引用验证。例如，可设计负样本使得被引文献的实际内容与声称内容不符，要求reviewer agent通过检索或比对证据库来识别这种“语义级”错误引用。

## 摘要级证据的局限

本合成所依赖的E_q均为摘要级证据（abstract-level evidence），存在以下显著局限：

- **缺乏方法细节**：摘要未提供负样本构造的具体方法、错误引用的类型分类、或评估指标（如精确率、召回率）等关键信息。例如，[1]虽提及“可验证证据”，但未说明如何生成错误引用作为测试用例。
- **领域不匹配**：[2]至[6]主要涉及蝙蝠群体涌现和TRPM亚家族冷却剂结合口袋等生物学主题，与“错误引用检测”的研究问题无直接关联，无法提供有效证据。
- **未明确提及引用错误检测**：所有证据均未将“识别错误引用”作为审查机制的核心功能进行描述，因此无法直接推断负样本测试的具体设计原则。

## 谨慎结论

基于现有摘要级证据，可以得出以下谨慎结论：

1. **现有框架具备审查基础**：[1]、[7]和[8]表明，多智能体系统中的审查机制已被证明能提升任务质量，这为设计针对错误引用的负样本测试提供了可行性前提。

2. **负样本测试设计需从零构建**：由于缺乏直接证据，负样本测试的具体设计（如错误类型、难度梯度、评估标准）需要研究者自行开发。建议参考[1]的对抗性思路和[7]的执行验证思路，构建包含“明显错误”（如作者、年份错误）和“隐蔽错误”（如引用内容与论点矛盾）的多层次测试集。

3. **需结合全文证据进行验证**：摘要级证据不足以支撑严谨的测试设计。未来研究应获取[1]和[8]的全文，以了解其审查机制的具体实现细节，并在此基础上设计针对错误引用识别的负样本测试方案。

## 参考文献
[1] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[2] Reviewer #2 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[3] Reviewer #1 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[4] Reviewer #1 (Public Review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[5] Reviewer #2 (Public review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[6] Reviewer #3 (Public Review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[7] From Questions to Queries: An AI-powered Multi-Agent Framework for Spatial Text-to-SQL. arXiv.org. 2025.
[8] LatteReview: a multi-agent framework for systematic review automation using large language models. arXiv preprint arXiv …. 2025.