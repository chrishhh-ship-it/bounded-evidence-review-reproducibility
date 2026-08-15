## 检索与筛选概览

当前多智能体文献综述管线中，筛选（Screening）角色的打分标准与合成（Synthesis）的引用精度之间存在内在的协同与对齐需求。现有研究主要聚焦于利用人工智能（AI）和大语言模型（LLM）自动化文献筛选流程，以提升证据合成的效率[1][2][3]。例如，一项系统综述协议指出，AI算法已被应用于自动化医学系统综述中的文献筛选，但不同算法报告的结果差异较大[1]。另一项研究测试了GPT模型在标题和摘要筛选中的表现，发现GPT-4在召回率100%时可节省50%的筛选时间，而在召回率仍高于95%时可节省75%的时间[2]。此外，一项关于多智能体AI系统在医疗保健中应用的系统综述，遵循PRISMA指南，从150篇记录中筛选出32篇符合条件的研究[8]。这些工作表明，筛选环节的自动化打分标准（如概率阈值）直接影响后续合成环节所引用文献的准确性和完整性。

## 核心主题与证据

筛选角色的打分标准与合成引用精度的对齐，核心在于确保筛选阶段保留的文献能够支撑合成阶段的高质量引用。证据显示，自动化筛选工具的性能评估指标（如召回率、精确率）是连接两者的关键桥梁[1][2]。具体而言，GPT-4模型在筛选任务中，当概率阈值为0.5时实现100%召回率，意味着无相关文献遗漏，这为合成阶段提供了完整的引用基础；而提高阈值虽可节省更多时间，但可能遗漏最多5%的相关文献，从而影响合成引用的全面性[2]。同时，多智能体系统在医疗领域的系统综述中，超过60%的研究涉及实际模型但缺乏临床验证，这提示筛选标准若过于宽松，可能导致合成阶段引用的文献质量参差不齐[8]。此外，一项关于增强证据合成效率的研究探索了基于LLM的智能体工作流（GREP-Agent）用于筛选证据[3]，其筛选打分标准的设计直接决定了后续合成环节所引用证据的可靠性和相关性。

## 证据支持的研究方向

基于现有证据，未来研究方向可聚焦于以下方面：第一，开发更精细的筛选打分标准，使其与合成阶段的引用精度需求动态对齐，例如根据合成任务对召回率和精确率的不同要求，自适应调整概率阈值[2]。第二，在医疗系统综述中，需将筛选标准与QUADAS-2等质量评估工具结合，确保筛选出的文献在合成时具有较高的方法学质量[1][7]。第三，针对多智能体系统在医疗领域的应用，应加强筛选阶段对伦理和法律因素的考量，因为现有研究仅有7篇深入讨论了伦理或法律影响[8]，这可能导致合成阶段引用的文献在伦理维度上存在偏差。第四，进一步测试LLM在不同领域和提示条件下的筛选表现，以验证其通用性和鲁棒性[2]，从而为合成阶段提供更稳定的引用来源。

## 摘要级证据的局限

本合成所依据的摘要级证据存在若干局限。首先，部分文献仅为研究协议或初步报告，如[1]和[7]均为系统综述协议，尚未提供实际筛选与合成的对齐结果。其次，[2]仅基于一项系统综述和一种提示进行评估，其结论的泛化能力有限[2]。再次，[3]的摘要内容较为简略，未详细说明筛选打分标准与合成引用精度的具体对齐机制。此外，[4]、[5]、[6]作为同行评审记录和作者回复，其摘要未提供实质性证据。最后，[8]虽然提供了多智能体系统在医疗领域的系统综述结果，但未直接探讨筛选打分标准与合成引用精度的关系。因此，上述证据的结论需谨慎解读，并期待更多实证研究加以验证。

## 谨慎结论

综合现有摘要级证据，多智能体文献综述管线中筛选角色的打分标准与合成引用精度的对齐，依赖于筛选阶段对召回率和精确率的平衡控制，以及筛选标准与质量评估工具的结合。GPT等LLM在筛选任务中展现出高召回率的潜力，但需注意阈值调整可能带来的文献遗漏风险[2]。多智能体系统在医疗领域的应用提示，筛选标准还需纳入伦理和法律考量，以提升合成引用的全面性和可靠性[8]。然而，由于当前证据多来自协议、初步研究或单一案例，且缺乏直接探讨两者对齐机制的实证数据，因此尚不能得出普适性结论。未来需开展更多跨领域、多提示的实证研究，以建立筛选打分标准与合成引用精度之间的量化对齐模型。

## 参考文献
[1] Automation of literature screening using machine learning in medical evidence synthesis: a diagnostic test accuracy systematic review protocol. Systematic Reviews. 2022.
[2] Testing the utility of GPT for title and abstract screening in environmental systematic evidence synthesis. Environmental Evidence. 2025.
[3] Enhancing Evidence Synthesis Efficiency: Leveraging Large Language Models and Agentic Workflows for Optimized Literature Screening. Cochrane evidence synthesis and methods. 2025.
[4] Review for "Enhancing Evidence Synthesis Efficiency: Leveraging Large Language Models and Agentic Workflows for Optimized Literature Screening". CrossRef. 2025.
[5] Decision letter for "Enhancing Evidence Synthesis Efficiency: Leveraging Large Language Models and Agentic Workflows for Optimized Literature Screening". CrossRef. 2025.
[6] Author response for "Enhancing Evidence Synthesis Efficiency: Leveraging Large Language Models and Agentic Workflows for Optimized Literature Screening". CrossRef. 2025.
[7] A Research Protocol for a Systematic Review of Automatic Literature Screening in Medical Evidence Synthesis. CrossRef. 2020.
[8] Multi-Agent AI Systems in Healthcare: Systematic Evidence Synthesis Via PRISMA of Clinical Decision Support Systems, Robotic Interventions, and Critical Care. International Journal of Latest Technology in Engineering Management &amp; Applied Science. 2025.