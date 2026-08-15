# 学术情报综合报告：数字人文管线中元数据标准作为架构约束的引用策略

## 1. 检索与筛选概览

本报告基于给定的八条摘要级证据记录（E_q）进行综合。这些记录涵盖数字人文元数据、人工智能伦理、大型语言模型应用、技术批判等多个领域，但与本查询直接相关的核心文献为[8]《Metainformation scenarios in Digital Humanities: Characterization and conceptual modelling strategies》（2019），该文系统梳理了数字人文领域最常用的元数据方法及其存在的问题[8]。其余记录虽涉及元数据、AI系统或技术标准等主题，但均未直接讨论Dublin Core、METS、EAD等具体元数据标准在数字人文管线中的引用规范问题。经筛选，仅有[8]提供了与查询主题直接相关的实质性证据。

## 2. 核心主题与证据

**元数据标准在数字人文中的角色与困境**：证据[8]明确指出，数字人文领域存在“标准泛滥”的问题——过多的元数据“标准”使得研究者难以选择，这是现有元数据方法的主要问题之一[8]。该文进一步指出，元数据与数据（或元信息与信息）被普遍假定为本质不同的实体，导致各自发展出独立的语言和工具集，引入了冗余模型；同时，大多数方法将概念关切与实现关切混为一谈，违反了模块化和关注点分离的基本工程原则[8]。这些问题在数字人文项目中尤为突出。

**元信息场景缺乏特征化**：证据[8]强调，在人文项目中，元信息（元数据）发挥作用的场景缺乏特征化，导致元信息被记录和管理时缺乏特定目的，进而阻碍了关于“记录什么元信息”以及“如何概念化、存储和管理”的决策过程[8]。该文提出了一种基于ConML概念建模语言的新方法，采用“元信息本质上与信息无异”的整体观点，并通过真实数据集在数字人文场景中进行了验证[8]。

**与查询主题的关联**：尽管[8]未直接提供Dublin Core、METS、EAD作为“架构约束”时的引用格式，但其揭示了元数据标准在数字人文管线中使用的根本性问题：标准选择困难、概念与实现混淆、缺乏场景化目标设定。这些发现为理解为何需要明确引用元数据标准提供了背景——当标准被用作架构约束时，其引用不仅是技术文档要求，更是确保管线可复现性、互操作性和学术透明度的必要实践。

## 3. 证据支持的研究方向

基于现有证据，以下研究方向值得关注：

**（1）元数据标准引用规范的标准化研究**：证据[8]指出数字人文领域存在“标准泛滥”问题[8]，这暗示需要建立统一的元数据标准引用规范，明确在学术出版物、技术文档和软件代码中如何引用Dublin Core、METS、EAD等标准。

**（2）架构约束视角下的元数据标准评估**：证据[8]揭示了概念与实现混淆的问题[8]，这提示需要从软件工程架构约束的角度重新评估元数据标准，研究其作为管线组件时的接口规范、版本管理和依赖关系。

**（3）数字人文管线可复现性框架**：证据[8]强调元信息记录需要“特定目的”[8]，这指向建立数字人文管线元数据引用清单（类似软件引用的CITATION.cff），使元数据标准的使用成为管线可复现性的组成部分。

**（4）跨学科引用实践比较**：虽然本证据集未提供其他学科的比较数据，但[4]关于LLM在供应链管理中的应用[4]和[7]关于机器学习在输血医学中的综述[7]均涉及技术标准的引用问题，暗示可开展跨学科元数据标准引用实践的对比研究。

## 4. 摘要级证据的局限

本综合面临以下显著局限：

**（1）直接证据不足**：在八条记录中，仅[8]直接讨论了数字人文元数据标准问题，且该文并未提供Dublin Core、METS、EAD的具体引用格式或引用规范建议。其余记录[1]-[7]均与查询主题无直接关联，无法提供实质性证据。

**（2）证据时效性**：核心证据[8]发表于2019年，距今已逾五年。在此期间，数字人文领域的技术栈和元数据实践可能已发生变化，例如FAIR原则的推广、Schema.org的普及、以及LLM驱动的元数据生成技术（如[2]讨论的AI辅助情感元数据[2]）的发展。

**（3）摘要级信息的粒度限制**：所有证据均为摘要级，缺乏全文细节。例如[8]的摘要虽提及“对最常用的元数据方法进行回顾”，但未列出具体标准名称（Dublin Core、METS、EAD等），也未说明其提出的ConML方法如何解决引用问题。

**（4）缺乏实践案例**：证据集中没有提供任何数字人文管线实际使用元数据标准作为架构约束的案例研究，无法从具体实践中归纳引用模式。

## 5. 谨慎结论

基于现有有限证据，可得出以下谨慎结论：

第一，数字人文领域元数据标准的使用面临“标准泛滥”、概念与实现混淆、缺乏场景化目标设定等根本性问题[8]，这为建立统一的引用规范提出了迫切需求。当Dublin Core、METS、EAD等标准被用作管线架构约束时，其引用应遵循软件工程中组件引用的基本原则：明确版本号、提供持久标识符（如DOI或标准注册机构URL）、说明使用范围（如描述性元数据、结构元数据或管理元数据）。

第二，目前缺乏针对元数据标准作为架构约束时的专门引用指南。建议参考软件引用（software citation）和标准引用（standard citation）的成熟实践，例如遵循FORCE11软件引用原则，在数字人文管线文档中为每个元数据标准提供：标准名称、版本号、发布机构、发布日期、持久标识符（如ISO标准号或DCMI命名空间URI）。

第三，未来研究应优先开展以下工作：（1）对现有数字人文管线进行实证调查，收集Dublin Core、METS、EAD的实际引用方式；（2）借鉴[8]提出的场景特征化方法[8]，开发针对不同管线架构的元数据标准引用模板；（3）建立数字人文社区共识，将元数据标准引用纳入学术出版指南和技术文档规范。

第四，本综合的结论受限于证据集的规模和粒度。建议在获取更全面的文献（包括元数据标准官方文档、数字人文项目技术报告、软件工程引用指南）后，进行更深入的系统综述。

## 参考文献
[1] Multi-Agent Systems Should be Treated as Principal-Agent Problems. arXiv Preprint. 2026.
[2] Evaluating the Effectiveness of AI-Assisted Emotional Metadata in Enhancing the Discoverability of Literary Texts in Digital Libraries. Social Sciences &amp; Humanity Research Review. 2025.
[3] Intersex people or khunthā in the Middle East – How they are perceived, accepted, & treated: qualitative evidence synthesis & framework analysis. Psychology &amp; Sexuality. 2024.
[4] The Potential Application of Large Language Models in Pharmaceutical Supply Chain Management. The Journal of Pediatric Pharmacology and Therapeutics. 2024.
[5] What Do We Critique When We Critique Technology?. American Literature. 2023.
[6] Updates in service standards in hotels: how COVID-19 changed operations. International Journal of Contemporary Hospitality Management. 2021.
[7] Machine learning in transfusion medicine: A scoping review. Transfusion. 2023.
[8] Metainformation scenarios in Digital Humanities: Characterization and conceptual modelling strategies. Information Systems. 2019.