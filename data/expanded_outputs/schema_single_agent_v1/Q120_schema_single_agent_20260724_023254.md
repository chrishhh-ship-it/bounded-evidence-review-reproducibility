# 数字化档案缺口对LLM综合证据时“制造残留”影响的学术综合

## 1. 检索与筛选概览

本综合基于提供的8篇摘要级证据记录，涵盖2023至2025年间发表的文献。这些文献来自医学、社会科学、计算机科学及人文学科等多个领域，包括《Journal of the American Society of Nephrology》《Humanities and Social Sciences Communications》《BMJ Evidence-Based …》《Health Research Policy and Systems》以及预印本和会议论文等。检索范围涉及大型语言模型（LLM）在证据综合中的应用、数字化技术批判、以及证据生产实践等主题。尽管直接探讨“数字化档案缺口”与“制造残留”关系的文献有限，但多篇记录提供了关于LLM在部分语料上综合证据时产生不准确或虚构内容（即“制造残留”）的间接证据。

## 2. 核心主题与证据

**主题一：LLM在证据综合中的“制造残留”现象**

多篇文献一致指出，LLM在综合来自有限或不完整语料库的信息时，倾向于生成看似合理但实际虚构的内容。[1]明确报告了ChatGPT-3.5在回答医学问题时“用虚构的标题和不相关的PubMed标识符支持其主张”，并指出“ChatGPT不咨询任何真理来源”，因此“偶尔出现不正确或有偏见的回答是不可避免的”。[1]进一步指出，即使使用检索增强（如网页浏览插件），ChatGPT-4的总结也“仅基于两篇文章，没有综合证据”，从而未能系统回答问题。[1]类似地，[3]在讨论LLM应用于制药供应链时警告，LLM“可能基于历史或过时信息做出建议”，且“模型的性能仅取决于其训练信息的质量”。[5]的摘要也暗示了LLM在证据综合数据提取中面临挑战和陷阱。

**主题二：数字化档案缺口与语料不完整性的影响**

[1]的发现直接关联数字化档案缺口的影响：当LLM仅能访问部分语料时（如仅从五篇输入文章中提取三篇的信息），其综合结果会遗漏重要机制（如缺氧），并产生“断言无输入来源支持”的内容。[1]将此归因于LLM“对输入文本长度的限制”以及检索增强系统中“用户对来源的控制减少”。[3]从供应链管理角度指出，LLM“无法提取不存在或不可用的数据”，且“数据标准化不足”会阻碍LLM从非结构化数据中获取有意义的见解，体现了“垃圾进，垃圾出”原则。[7]在气候变化证据综合评估中发现，GPT-4o在低专业知识任务（如地理位置识别）中表现准确，但在中高专业知识任务（如利益相关者识别、适应深度评估）中“可靠性较低”，这暗示了当语料缺口涉及复杂语义时，LLM的“制造残留”风险更高。

**主题三：技术批判视角下的数字化不平等**

[4]从批判技术研究角度指出，数字化系统“加剧了不平等和歧视”，且技术基础设施（如数据中心、供应链）的物质性往往被掩盖。[4]强调“技术不是中性的”，而是“嵌入权力关系”的。这一视角有助于理解数字化档案缺口本身是社会技术不平等的产物——某些群体的知识可能因缺乏数字化表征而被系统性地排除在LLM训练语料之外，从而在综合过程中产生“制造残留”。[2]关于网络厌女症的系统综述也间接表明，数字化空间中的知识生产存在结构性偏差，这可能反映在语料库的构成中。

**主题四：证据综合实践中的速度与严谨性权衡**

[6]记录了COVID-19疫情期间证据综合团队在“严谨性与速度之间取得平衡”的挑战，并指出“及时提供的快速响应”在不确定性背景下有助于决策。然而，[1]和[5]的发现表明，当LLM被用于加速证据综合时，速度往往以牺牲准确性为代价。[1]明确建议采用“检索、总结、验证”范式，以“最小化直接使用虚假或虚构信息的风险”。[8]则从教育角度指出，AI工具可以提高学生自我效能感，但需注意其局限性。

## 3. 证据支持的研究方向

基于上述证据，以下研究方向值得关注：

**方向一：数字化档案缺口对LLM综合保真度的量化影响。** [1]和[7]提供了初步证据，但缺乏系统性的实验设计来测量不同缺口程度（如缺失比例、缺失内容类型）与“制造残留”频率之间的定量关系。未来研究可借鉴[3]中关于数据质量与LLM性能关系的讨论，设计控制实验。

**方向二：针对部分语料的LLM综合验证方法。** [1]提出的“检索、总结、验证”范式需要进一步发展自动验证工具。[5]和[7]也暗示了评估框架的必要性。研究可探索如何利用外部知识库或领域特定API（如[3]建议的）来弥补语料缺口。

**方向三：数字化档案缺口的社会技术成因。** [4]和[2]的批判视角提示，语料缺口不仅是技术问题，更是权力和资源分配问题。研究可分析哪些群体的知识更易被数字化排除，以及这种排除如何通过LLM综合过程被放大。

**方向四：高风险领域（如医学、气候变化）中LLM综合的可靠性边界。** [1]和[7]分别针对医学和气候变化领域，发现LLM在需要深度领域知识的任务中表现不佳。未来研究应明确界定LLM可安全应用的场景，并建立风险分级机制。

## 4. 摘要级证据的局限

本综合基于摘要级证据，存在以下固有局限：首先，摘要通常省略了方法细节、样本特征和效应量等关键信息，限制了因果推断能力。例如，[1]虽然报告了ChatGPT的虚构引用现象，但未提供实验的完整设计（如提示词的具体措辞、评估者间信度等）。其次，多篇文献（如[2]、[4]、[6]）并非直接研究LLM与数字化档案缺口的关系，其证据是间接的，需要谨慎推断。第三，[5]的摘要过于简短，无法判断其具体发现与本研究问题的相关性。第四，所有证据均来自已发表或预印本文献，可能存在发表偏倚——负面结果（即LLM表现不佳）可能更少被报告。最后，[3]和[7]分别来自商业期刊和研讨会，其同行评审标准可能与传统学术期刊不同。

## 5. 谨慎结论

现有摘要级证据表明，数字化档案缺口——即LLM训练或检索语料的不完整、有偏或缺失——会显著增加LLM在综合证据时产生“制造残留”（即虚构或不准确内容）的风险。具体表现为：当语料不完整时，LLM倾向于遗漏关键信息、生成无来源支持的断言，并在需要深度领域知识的任务中表现不可靠。这一现象在医学[1]、气候变化[7]和供应链管理[3]等领域均有记录。然而，证据基础尚不充分：缺乏对缺口类型与残留程度之间关系的系统量化，也缺乏针对不同领域和LLM架构的比较研究。此外，数字化档案缺口本身是社会技术不平等的产物[4]，需要批判性审视。因此，在LLM用于证据综合时，必须采用“检索、总结、验证”的范式[1]，并始终保留人类在回路中的监督[3]。未来研究应优先发展针对部分语料的验证工具，并探索如何通过结构化数据接口（如API）弥补语料缺口[3]。

## 参考文献
[1] Retrieve, Summarize, and Verify: How Will ChatGPT Affect Information Seeking from the Medical Literature?. Journal of the American Society of Nephrology. 2023.
[2] How do we study misogyny in the digital age? A systematic literature review using a computational linguistic approach. Humanities and Social Sciences Communications. 2024.
[3] The Potential Application of Large Language Models in Pharmaceutical Supply Chain Management. The Journal of Pediatric Pharmacology and Therapeutics. 2024.
[4] What Do We Critique When We Critique Technology?. American Literature. 2023.
[5] From promise to practice: challenges and pitfalls in the evaluation of large language models for data extraction in evidence synthesis. BMJ Evidence-Based …. 2025.
[6] Production and use of rapid responses during the COVID-19 pandemic in Quebec (Canada): perspectives from evidence synthesis producers and decision makers. Health Research Policy and Systems. 2024.
[7] Assessing the Effectiveness of GPT-4o in Climate Change Evidence Synthesis and Systematic Assessments: Preliminary Insights. CLIMATENLP. 2024.
[8] How Artificial Intelligence Can Affect Physician Assistant Student Self-Efficacy When Preparing for Objective Structured Clinical Examinations.. The journal of physician assistant education : the official journal of the Physician Assistant Education Association. 2025.