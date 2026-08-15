## 检索与筛选概览

当前多智能体文献综述管线中，Screening（筛选）环节与Synthesis（综合）环节的衔接是自动化证据合成的关键。现有研究主要聚焦于利用人工智能（AI）和大语言模型（LLM）优化文献筛选流程。例如，一项系统综述协议计划系统评估AI算法在医学证据合成中自动筛选文献的效果[1][7]，而另一项研究则测试了GPT模型在环境证据合成中用于标题和摘要筛选的效用[2]。此外，最新研究探索了基于LLM的智能体工作流（如GREP-Agent）来优化筛选效率[3]。这些工作共同构成了从人工筛选向自动化、智能化筛选过渡的技术基础。

## 核心主题与证据

Screening角色的打分标准与Synthesis的引用精度对齐，本质上涉及两个核心问题：筛选阶段的召回率与精确率如何影响后续综合阶段的证据完整性。现有证据表明，GPT-4模型在标题和摘要筛选任务中，当概率阈值为0.5时召回率达到100%，意味着未遗漏任何相关文献，此时可节省50%的筛选时间；若将阈值调高至召回率仍高于95%，则可节省75%的时间[2]。这提示，Screening阶段的高召回率（即打分标准宽松）能够确保Synthesis阶段获得完整的文献集，从而提升引用精度。然而，若筛选标准过于严格（如追求高精确率），可能遗漏相关文献，导致Synthesis阶段引用不完整。另一项研究指出，多智能体系统在临床决策支持、机器人干预和重症监护等领域的应用中，超过60%的模型缺乏临床验证[8]，这进一步说明，若Screening阶段未能有效筛选出经过验证的高质量文献，Synthesis阶段的引用精度将受到质疑。

## 证据支持的研究方向

基于现有证据，未来研究可从以下方向推进Screening打分标准与Synthesis引用精度的对齐：第一，开发自适应阈值调整机制，根据Synthesis阶段对引用精度的需求动态调整Screening阶段的打分标准，例如在需要高召回率的场景（如系统综述）中采用较低阈值[2]。第二，探索多智能体协作框架，让Screening角色与Synthesis角色共享反馈信息，例如Synthesis阶段发现引用缺失时反向调整Screening的筛选策略[3]。第三，在医疗等高风险领域，需结合临床验证数据（如QUADAS-2工具）校准Screening打分标准，以确保筛选出的文献具备足够的证据质量[1][7]。第四，针对多智能体系统在医疗领域的应用，应建立包含伦理、隐私和透明度的评估框架，使Screening标准不仅关注相关性，还兼顾文献的伦理合规性[8]。

## 摘要级证据的局限

本合成所依赖的摘要级证据存在明显局限。首先，多数文献仅提供研究协议或初步结果，缺乏完整的实证数据。例如，关于AI筛选方法的系统综述仍处于协议阶段[1][7]，而GREP-Agent的详细性能数据尚未在摘要中披露[3]。其次，GPT筛选效用的测试仅基于一项系统综述和单一提示词，其泛化能力未知[2]。此外，多智能体系统在医疗领域的综述虽提供了比较框架，但摘要未详细说明Screening与Synthesis的具体对齐机制[8]。这些局限意味着，当前结论需谨慎解读，且无法直接推广至所有多智能体文献综述管线。

## 谨慎结论

综合现有摘要级证据，Screening角色的打分标准与Synthesis的引用精度之间存在权衡关系：高召回率的筛选标准有助于提升Synthesis阶段的引用完整性，但可能引入噪声；而高精确率的标准虽减少噪声，却可能遗漏关键文献。GPT模型在特定任务中展示了实现高召回率同时节省大量筛选时间的潜力[2]，但这一发现需在更多领域和提示词下验证。多智能体工作流（如GREP-Agent）为动态对齐提供了技术可能[3]，但缺乏临床验证的模型可能削弱Synthesis的引用可靠性[8]。因此，建议未来研究在完整管线中实证评估Screening打分标准（如阈值、召回率/精确率权重）对Synthesis引用精度（如引用覆盖率、错误引用率）的量化影响，并开发可解释的对齐框架。

## 参考文献
[1] Automation of literature screening using machine learning in medical evidence synthesis: a diagnostic test accuracy systematic review protocol. Systematic Reviews. 2022.
[2] Testing the utility of GPT for title and abstract screening in environmental systematic evidence synthesis. Environmental Evidence. 2025.
[3] Enhancing Evidence Synthesis Efficiency: Leveraging Large Language Models and Agentic Workflows for Optimized Literature Screening. Cochrane evidence synthesis and methods. 2025.
[4] Review for "Enhancing Evidence Synthesis Efficiency: Leveraging Large Language Models and Agentic Workflows for Optimized Literature Screening". CrossRef. 2025.
[5] Decision letter for "Enhancing Evidence Synthesis Efficiency: Leveraging Large Language Models and Agentic Workflows for Optimized Literature Screening". CrossRef. 2025.
[6] Author response for "Enhancing Evidence Synthesis Efficiency: Leveraging Large Language Models and Agentic Workflows for Optimized Literature Screening". CrossRef. 2025.
[7] A Research Protocol for a Systematic Review of Automatic Literature Screening in Medical Evidence Synthesis. CrossRef. 2020.
[8] Multi-Agent AI Systems in Healthcare: Systematic Evidence Synthesis Via PRISMA of Clinical Decision Support Systems, Robotic Interventions, and Critical Care. International Journal of Latest Technology in Engineering Management &amp; Applied Science. 2025.