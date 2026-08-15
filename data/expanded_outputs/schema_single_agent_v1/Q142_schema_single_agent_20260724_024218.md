## 1. 检索与筛选概览

本合成基于提供的8篇摘要级证据记录，涵盖系统综述方法论、大型语言模型（LLM）应用、临床研究评估及人文学科历史等领域。这些记录来自不同学科背景，包括临床医学、公共卫生、数字人文及人工智能研究。检索范围涉及2016年至2025年间发表的文献，其中[1]讨论了系统综述与叙事综述的方法论争议，[2]和[8]探讨了LLM在公共卫生和供应链管理中的潜在应用，[3]和[7]分别评估了运动干预和LLM在临床环境中的效果，[4]分析了LLM综述论文的元数据，[5]聚焦于医疗团队合作教育，[6]则阐述了人文学科历史领域的建立。这些记录均基于摘要级证据，未提供完整的全文细节。

## 2. 核心主题与证据

核心主题围绕数字工具（尤其是LLM）在学术研究和实践中的应用及其可重复性要求展开。关于LLM在临床研究中的应用，[7]通过系统综述和网络荟萃分析发现，不同LLM在回答临床研究问题时表现各异：ChatGPT-4o在客观问题中表现最佳（SUCRA=0.9207），而人类专家在临床病例的顶级诊断（top 1 diagnosis）中排名最高（SUCRA=0.9001）[7]。这表明LLM的准确性因任务类型而异，且人类判断在某些领域仍具优势。

在方法论层面，[1]强调系统综述应具备“方法学可重复性”，即不同研究团队使用相同搜索标准和质量检查工具应获得相同结果[1]。这一原则对依赖特定版本文本分析工具的DH研究尤为重要。然而，[1]也指出，叙事综述通过解释和批判性反思提供“合理真相”，其价值不应被低估[1]。对于LLM的应用，[2]提出LLM代理可通过形式化团队互动、优化工作流程和质量控制来增强一致性和可重复性[2]。但[8]警告，LLM的输出质量高度依赖提示词设计，且存在“垃圾进、垃圾出”的风险，即数据标准化不足会限制其有效性[8]。

## 3. 证据支持的研究方向

基于现有证据，以下研究方向值得关注：首先，应系统评估不同版本文本分析工具对DH研究结果的影响，建立版本控制与可重复性标准，这呼应了[1]中关于方法学透明度的呼吁。其次，需探索LLM在辅助文献筛选、数据提取和代码生成中的可靠性，[2]和[8]均指出LLM可提升效率，但需通过验证和人工监督确保准确性[2][8]。第三，应发展跨学科的方法论框架，结合系统综述的严谨性与叙事综述的解释性，如[1]所述，不同综述类型提供不同形式的真理[1]。最后，针对LLM在特定领域（如临床诊断）的表现，[7]建议进一步研究其与人类专家协作的最佳模式[7]。

## 4. 摘要级证据的局限

本合成仅依赖摘要级证据，存在显著局限。首先，摘要可能未充分反映研究的方法学细节，例如[3]虽报告了荟萃分析结果，但未说明工具版本或软件环境[3]。其次，摘要中的结论可能简化了复杂发现，如[4]仅提及逻辑回归模型的准确率提升至47%，但未讨论特征选择或模型泛化能力[4]。此外，部分记录（如[6]）为编辑性文章，缺乏实证数据支持[6]。最后，摘要级证据无法验证原始研究的内部效度，例如[7]中76.2%的研究被评估为中等偏倚风险，但摘要未详细说明偏倚来源[7]。因此，本合成的结论应视为初步探索，需结合全文分析加以验证。

## 5. 谨慎结论

当DH论文的关键发现依赖于特定版本的文本分析工具时，应满足以下可重复性要求：明确报告工具名称、版本号及运行环境；提供完整的参数设置和代码；采用版本控制机制（如容器化或虚拟环境）；并开展敏感性分析以评估版本变化对结果的影响。这些要求借鉴了[1]中系统综述的方法学透明度原则，以及[2]和[8]中关于LLM工作流程标准化的建议。然而，由于证据基础有限，且LLM等工具仍在快速演进，上述要求需在实践中动态调整。未来研究应优先开展跨学科合作，建立DH领域数字工具可重复性的共识指南。

## 参考文献
[1] Time to challenge the spurious hierarchy of systematic over narrative reviews?. European Journal of Clinical Investigation. 2018.
[2] Importance of investing time and money in integrating large language model-based agents into outbreak analytics pipelines. The Lancet Microbe. 2024.
[3] Impact of exercise training on cognitive function in patients with COPD: a systematic review and meta-analysis of randomised controlled trials.. European respiratory review : an official journal of the European Respiratory Society. 2025.
[4] A Comprehensive Analysis of Survey Papers on Large Language Models. CrossRef. 2024.
[5] Health professionals' experience of teamwork education in acute hospital settings: a systematic review of qualitative literature.. JBI database of systematic reviews and implementation reports. 2016.
[6] A New Field:<i>History of Humanities</i>. History of Humanities. 2016.
[7] Accuracy of Large Language Models When Answering Clinical Research Questions: Systematic Review and Network Meta-Analysis. Journal of Medical Internet Research. 2025.
[8] The Potential Application of Large Language Models in Pharmaceutical Supply Chain Management. The Journal of Pediatric Pharmacology and Therapeutics. 2024.