1. 检索与筛选概览

本综合基于所提供的有限证据集（E_q）进行单次合成，旨在探讨多智能体系统如何在不混淆权威层级的前提下，综合来自同行评审研究与灰色文献（如IEA、IRENA报告）的证据。证据集包含8项记录，涵盖系统评价方法论、多智能体系统应用（代码生成、电路设计、文献综述、宇宙学模拟）以及医学治疗研究。其中，[1]和[2]直接涉及对同行评审与灰色文献的综合方法，[4]讨论了大型语言模型（LLM）在医学文献检索中的局限，[5]和[6]则提出了多智能体系统在文献综述中的具体架构。然而，该证据集并未包含IEA或IRENA的具体报告，因此无法直接评估其权威层级差异。

2. 核心主题与证据

核心主题聚焦于如何利用LLM或多智能体系统进行文献证据的综合，并区分不同来源的权威性。[1]指出，LLM（如GPT-4）在系统评价的筛选与数据提取任务中，其表现受数据集平衡性和提示质量影响，在高度平衡的数据集中表现不佳，但在特定条件下可达到“人类水平”[1]。该研究同时涉及同行评审与灰色文献，但未专门讨论如何区分两者的权威层级[1]。[2]通过多声部文献综述（MLR）方法，系统综合了学术与工业来源（包括灰色文献）关于LLM多智能体系统在代码生成中的研究，将挑战与解决方案归纳为六大类[2]。这表明MLR方法本身可容纳不同权威来源，但未提供具体区分策略。[4]则强调，LLM在医学文献检索中存在“幻觉”问题，会生成看似可信但虚假的引用，因此提出“检索-总结-验证”范式，要求用户对输出进行验证[4]。该范式隐含了对信息来源权威性的关注，但未明确区分同行评审与灰色文献。

3. 证据支持的研究方向

基于现有证据，以下研究方向值得关注：第一，开发能够自动标注证据来源权威层级的多智能体系统。[5]提出的对抗性多智能体系统，通过作者-审稿人工作流与验证性证据及批评循环，可能为区分不同来源提供机制[5]。第二，利用多智能体系统实现文献参数的自动化提取与验证。[3]中的AmpAgent通过文献分析、数学推理和设备尺寸设定三个智能体，从文献中提取关键信息并用于电路设计，显著提高了效率[3]。[6]中的SimAgents则通过物理推理、软件验证和工具执行智能体，从宇宙学文献中提取参数并确保其物理一致性与软件合规性[6]。这些系统展示了多智能体在结构化提取证据方面的潜力，但未涉及权威层级区分。第三，在系统评价中明确采用MLR方法，如[2]所示，该方法可系统整合不同来源，但需进一步制定评估灰色文献权威性的标准[2]。

4. 摘要级证据的局限

本合成完全依赖摘要级证据，存在显著局限。首先，摘要信息有限，无法获取研究的方法细节、数据来源及具体结论的完整上下文。例如，[1]中关于GPT-4性能的详细数据（如调整后性能下降）仅基于摘要描述，缺乏对具体实验设计的深入理解[1]。其次，证据集未包含任何IEA或IRENA的灰色文献报告，因此无法直接分析其权威层级与同行评审研究的差异。第三，部分摘要（如[5]）内容缺失，仅提供标题，无法提取任何实质性证据[5]。最后，摘要可能省略了关键的限制性说明，例如[4]中关于LLM生成摘要不准确性的具体实例，在摘要中仅以概括性语言呈现[4]。

5. 谨慎结论

基于现有摘要级证据，多智能体系统在综合同行评审与灰色文献方面展现出潜力，但当前证据不足以支持其在不混淆权威层级的情况下进行有效综合。关键挑战包括：LLM的“幻觉”问题可能导致虚假引用[4]；现有系统（如AmpAgent、SimAgents）主要关注技术参数提取，而非证据权威性评估[3][6]；MLR方法虽可整合不同来源，但缺乏标准化权威层级区分框架[2]。因此，在开发此类系统时，必须嵌入来源验证机制（如[4]提出的“检索-总结-验证”范式）和对抗性批评循环（如[5]所示），并明确标注每项证据的来源类型与权威层级。未来研究应基于更完整的全文证据，并纳入具体灰色文献（如IEA、IRENA报告）进行实证评估。

## 参考文献
[1] Can large language models replace humans in systematic reviews? Evaluating GPT-4's efficacy in screening and extracting data from peer-reviewed and grey literature in multiple languages.. Research synthesis methods. 2024.
[2] LLM-Based Multi-Agent Systems for Code Generation: A Multi-Vocal Literature Review ⋆. CrossRef. 2026.
[3] AmpAgent: An LLM-based Multi-Agent System for Multi-stage Amplifier Schematic Design from Literature for Process and Performance Porting. arXiv Preprint. 2024.
[4] Retrieve, Summarize, and Verify: How Will ChatGPT Affect Information Seeking from the Medical Literature?. Journal of the American Society of Nephrology. 2023.
[5] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[6] Bridging Literature and the Universe Via A Multi-Agent Large Language Model System. arXiv Preprint. 2025.
[7] INNV-39. INVESTIGATING MULTI-AGENT INTRATHECAL CHEMOTHERAPY AS A TREATMENT FOR PRIMARY AND SECONDARY CENTRAL NERVOUS SYSTEM LYMPHOMA: SAFETY AND EFFICACY RESULTS FROM AN INSTITUTIONAL COHORT STUDY. Neuro-Oncology. 2023.
[8] Analysing the synergies between Multi-agent Systems and Digital Twins: A systematic literature review. Information and Software Technology. 2024.