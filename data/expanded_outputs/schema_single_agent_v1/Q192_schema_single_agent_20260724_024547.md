# 中国学术智能综合报告：生物医学知识图谱中区分断言事实与计算推断事实的引用实践

## 1. 检索与筛选概览

本报告基于提供的限定证据集E_q，共包含8篇文献记录。经筛选，其中5篇文献直接涉及生物医学知识图谱中事实区分与引用实践的核心议题，包括：EvidenceNet框架[1]、BioStrataKG与IP-RAR方法[5]、GAPMAP知识缺口映射[3]、Schema-Constrained AI提取系统[6]以及AI工具在文献检索与知识挖掘中的综述[7]。其余文献[2][4][8]因主题偏离（分别涉及农业推广服务、系统综述与叙述综述的方法论争论、数字人文语义网应用）未纳入核心分析。

## 2. 核心主题与证据

### 2.1 断言事实与推断事实的区分需求

生物医学知识图谱面临的核心挑战在于：现有资源要么将证据保留为非结构化文本，要么压缩为扁平三元组，从而忽略了研究设计、来源和定量支持等关键信息[1]。这种信息损失使得知识图谱难以区分哪些事实是直接从文献中提取的断言事实（asserted facts），哪些是通过计算推理产生的推断事实（inferred facts）。EvidenceNet框架通过引入“证据节点”（evidence nodes）概念，将实验验证的发现作为结构化证据记录，并明确标注证据质量评分，从而在知识图谱层面保留了事实的来源与可信度信息[1]。

### 2.2 结构化引用与来源追溯机制

Schema-Constrained AI提取系统提出了一种基于模式约束的提取方法，通过类型化模式（typed schemas）、受控词汇表（controlled vocabularies）和证据门控决策（evidence-gated decisions）来限制模型推理[6]。该系统采用句子级来源追溯（sentence-level provenance）机制，支持事后审计（post-hoc audit），确保每个提取的事实都能追溯到原始文档中的具体位置[6]。这种设计使得知识图谱中的每个事实节点都携带明确的来源标识，从而区分了直接提取的断言事实与可能存在的计算推断。

### 2.3 检索增强推理与事实验证

IP-RAR（Integrated and Progressive Retrieval-Augmented Reasoning）方法通过集成推理式检索和渐进式推理生成，利用自我反思（self-reflection）实现深度思考，在检索和推理过程中区分不同来源的知识[5]。该方法在文档检索F1分数上提升20%，答案生成准确率提升25%，表明通过检索增强机制可以有效验证事实的来源可靠性[5]。

### 2.4 知识缺口映射与事实不确定性标注

GAPMAP框架定义了两种知识缺口类型：显式缺口（explicit gaps）——明确声明缺失的知识；隐式缺口（implicit gaps）——通过上下文推断的缺失知识[3]。该研究引入TABI（Toulmin-Abductive Bucketed Inference）推理方案，对推断结论候选进行结构化推理和分桶验证[3]。这种对知识缺口的系统识别能力，为知识图谱中标注事实的不确定性提供了方法论基础——即明确标注哪些事实是经过验证的断言事实，哪些是基于推断的假设性知识。

## 3. 证据支持的研究方向

### 3.1 证据感知的知识图谱构建

EvidenceNet的成功实践表明，构建疾病特异性知识图谱时，通过LLM辅助管道提取结构化证据节点、标准化生物医学实体、评分证据质量，并连接证据记录与类型化语义关系，可以有效区分断言事实与推断事实[1]。该框架在HCC和CRC两个疾病数据集上实现了98.3%的字段级提取准确率和100%的高置信度实体链接准确率[1]。

### 3.2 可审计的AI提取系统

Schema-Constrained AI系统展示了通过冲突感知合并（conflict-aware consolidation）、基于集合的聚合（set-based aggregation）和句子级来源追溯，实现从异构科学PDF到结构化证据的可扩展、可审计转换[6]。迭代模式优化显著提高了合成关键变量的提取保真度，包括检测分类、结果定义、随访持续时间和测量时间点[6]。

### 3.3 多跳推理与跨文档关联

BioStrataKG与IP-RAR方法通过构建分层知识图谱和跨文档问答数据集，实现了潜在知识检索和多跳推理，帮助医生整合治疗证据以制定个性化用药方案，并支持研究人员分析进展和研究缺口[5]。

### 3.4 知识缺口驱动的研究方向识别

GAPMAP的研究表明，LLM在识别显式和隐式知识缺口方面具有强大能力，可以支持早期研究构思、政策制定和资助决策[3]。这种能力可以反向应用于知识图谱的质量评估——通过识别知识图谱中哪些事实是基于推断的（即存在知识缺口），从而区分断言事实与推断事实。

## 4. 摘要级证据的局限

本报告基于摘要级证据，存在以下固有局限：

- **信息粒度不足**：摘要无法提供方法细节，如EvidenceNet的具体证据质量评分标准[1]、Schema-Constrained AI系统的冲突解决算法[6]、IP-RAR的自我反思机制实现细节[5]等关键信息。
- **验证范围有限**：各研究的评估指标（如98.3%提取准确率[1]、20%检索F1提升[5]）仅在特定数据集上获得，泛化性有待验证。
- **方法细节缺失**：GAPMAP的TABI推理方案的具体实现步骤[3]、BioStrataKG的分层结构定义[5]等关键方法细节在摘要中无法获取。
- **时间滞后性**：部分文献为预印本（2025-2026年）[1][3][6]，尚未经过同行评审，结论的可靠性需进一步确认。
- **跨领域适用性**：现有研究主要聚焦生物医学领域，其区分断言事实与推断事实的方法是否适用于其他领域（如社会科学、工程学）尚不明确。

## 5. 谨慎结论

基于现有摘要级证据，可以得出以下谨慎结论：

1. **结构化证据节点是区分事实来源的关键机制**：EvidenceNet通过引入证据节点和证据质量评分，为知识图谱中每个事实提供了明确的来源标识和可信度评估，从而区分了直接提取的断言事实与可能存在的计算推断[1]。

2. **来源追溯与审计机制是事实区分的保障**：Schema-Constrained AI系统的句子级来源追溯和冲突感知合并机制[6]，以及IP-RAR的检索增强推理[5]，共同构成了区分断言事实与推断事实的技术基础。

3. **知识缺口标注提供了不确定性量化框架**：GAPMAP对显式和隐式知识缺口的系统识别[3]，为知识图谱中标注推断事实的不确定性提供了方法论支持。

4. **现有方法仍处于早期阶段**：尽管各研究取得了积极结果，但均未提供完整的、经过大规模验证的区分断言事实与推断事实的标准化引用实践方案。未来需要更多研究来建立统一的证据溯源标准、推断事实标注规范以及跨系统互操作机制。

5. **人类专家监督不可或缺**：AI工具在文献检索和知识挖掘中的应用仍面临输出质量变异、幻觉风险和算法透明度不足等挑战[7]，在区分断言事实与推断事实的关键任务中，人类专家的监督和验证仍然至关重要。

## 参考文献
[1] Building evidence-based knowledge graphs from full-text literature for disease-specific biomedical reasoning. arXiv Preprint. 2026.
[2] Improving the effectiveness of agricultural extension services in supporting farmers to adapt to climate change: Insights from northeastern Ghana. Climate Risk Management. 2021.
[3] GAPMAP: Mapping Scientific Knowledge Gaps in Biomedical Literature Using Large Language Models. arXiv.org. 2025.
[4] Time to challenge the spurious hierarchy of systematic over narrative reviews?. European Journal of Clinical Investigation. 2018.
[5] A retrieval-augmented knowledge mining method with deep thinking LLMs for biomedical research and clinical support. GigaScience. 2025.
[6] From Chaos to Clarity: Schema-Constrained AI for Auditable Biomedical Evidence Extraction from Full-Text PDFs. arXiv Preprint. 2025.
[7] Artificial Intelligence Tools in Biomedical Research: Part 1—Literature Search and Knowledge Mining. Antioxidants and Redox Signaling. 2025.
[8] Using the Semantic Web in digital humanities: Shift from data publishing to data-analysis and serendipitous knowledge discovery. Semantic Web. 2020.