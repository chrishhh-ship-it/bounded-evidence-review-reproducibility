1. 检索与筛选概览

本合成基于提供的八篇摘要级证据（E_q），涵盖系统综述方法论、AI在学术与临床中的应用及其偏差问题。这些文献来自不同学科领域，包括临床医学、环境科学、工程设计、心理健康和AI技术评估。由于是单智能体基线合成，所有事实性陈述均严格限定于所提供的摘要内容，未进行额外检索或筛选。

2. 核心主题与证据

核心主题围绕AI系统（尤其是大型语言模型）在学术研究和临床应用中可能产生的偏差与误用风险，以及如何通过规范的报告要求来防范对统计结果的错误解读。

首先，关于统计显著性与临床意义的区分，传统系统综述强调通过元分析确认“临床显著效应是否也具有统计显著性”[1]。然而，AI生成的文本可能无法可靠地执行这种关键判断。例如，ChatGPT在生成科学摘要时，人类审稿人仅能正确识别68%的AI生成摘要[4]，这表明AI可能以看似可信的方式呈现不准确信息，从而掩盖小效应量的临床无关性。

其次，AI在心理健康领域的应用已显示出基于性别等人口学特征的偏差。一项针对神经性厌食症和贪食症案例的研究发现，ChatGPT-4在评估心理健康相关生活质量时，对男性案例的评分显著低于女性案例（P=0.04），而现实世界证据并不支持这一模式[5]。这种偏差可能导致AI系统将统计上显著但临床意义微小（如效应量差异）的结果错误地解读为具有临床重要性。

此外，AI生成临床笔记的质量评估方法存在缺陷。当前评估实践主要依赖词汇重叠指标（如ROUGE、BLEU），这些指标虽能检测删除和修改，但会惩罚保留原意的改写[7]。这意味着AI生成的报告可能通过表面上的词汇匹配来掩盖对效应量临床意义的实质性误述。

3. 证据支持的研究方向

基于上述证据，以下研究方向值得关注：

- **开发针对AI合成中效应量解读的专门报告标准**：现有系统综述方法论强调透明性和可审计性[1]，但AI系统缺乏这种结构化报告机制。需要建立类似PICOS框架的AI报告规范，强制要求明确区分统计显著性与临床意义[6]。

- **构建多层次的AI输出质量评估体系**：当前词汇重叠指标不足以检测临床相关错误[7]。建议采用分层策略，结合语义指标（如BERTScore）和AI作为评估者的方法，并辅以针对性的人工裁决[7]。

- **研究AI偏差对临床决策的级联效应**：AI在心理健康评估中表现出的性别偏差[5]可能放大小效应量的误导性解读。需要探索偏差如何影响医生对统计结果的临床判断。

- **推动AI辅助系统综述的实时更新机制**：AI驱动的活体系统综述可减少研究浪费[6]，但需确保其能准确识别和报告效应量的临床相关性，而非仅关注统计显著性。

4. 摘要级证据的局限

本合成受限于摘要级证据的固有局限。首先，摘要可能省略关键的方法学细节，例如[1]中关于系统综述与叙述性综述的讨论未提供具体的效应量阈值标准。其次，部分文献（如[3]）的摘要过于简短，无法提取实质性证据。第三，[6]和[8]分别来自预印本平台（arXiv），其内容尚未经过同行评审。最后，所有证据均来自2021-2026年，可能未涵盖最新的AI报告规范发展。

5. 谨慎结论

基于现有摘要级证据，可以谨慎得出结论：当前AI系统在学术和临床应用中缺乏防止误述统计显著但效应量小的临床意义的报告要求。具体而言，AI生成内容可能因以下原因导致误述：（1）无法可靠区分统计显著性与临床意义[1]；（2）存在基于人口学特征的偏差，可能扭曲效应量的解释[5]；（3）评估方法不充分，无法检测对临床意义的实质性误述[7]。建议未来研究优先开发针对AI合成中效应量解读的强制报告标准，并建立多层次的验证机制。然而，这些结论需通过全文证据和实证研究进一步验证。

## 参考文献
[1] Time to challenge the spurious hierarchy of systematic over narrative reviews?. European Journal of Clinical Investigation. 2018.
[2] How effective is ‘greening’ of urban areas in reducing human exposure to ground-level ozone concentrations, UV exposure and the ‘urban heat island effect’? An updated systematic review. Environmental Evidence. 2021.
[3] Rethink literature review of design research in an age of AI–from 'secretary work'to scholarly synthesis of insight, frameworks, and foresight. Journal of Engineering Design. 2026.
[4] The future of ChatGPT in academic research and publishing: A commentary for <i>clinical and translational medicine</i>. Clinical and Translational Medicine. 2023.
[5] Exploring Biases of Large Language Models in the Field of Mental Health: Comparative Questionnaire Study of the Effect of Gender and Sexual Orientation in Anorexia Nervosa and Bulimia Nervosa Case Vignettes.. JMIR mental health. 2025.
[6] An AI-Driven Live Systematic Reviews in the Brain-Heart Interconnectome: Minimizing Research Waste and Advancing Evidence Synthesis. arXiv.org. 2025.
[7] Measuring the Quality of AI-Generated Clinical Notes: A Systematic Review and Experimental Benchmark of Evaluation Methods. CrossRef. 2025.
[8] Factors That Influence the Adoption of AI-enabled Conversational Agents (AICAs) as an Augmenting Therapeutic Tool by Frontline Healthcare Workers: From Technology Acceptance Model 3 (TAM3) Lens -- A Systematic Mapping Review. arXiv Preprint. 2025.