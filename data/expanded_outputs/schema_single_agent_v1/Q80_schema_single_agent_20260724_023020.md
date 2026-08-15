## 1. 检索与筛选概览

本合成基于提供的8篇摘要级证据，这些文献涵盖了人工智能（AI）与机器学习、多智能体系统、6G网络、能源市场、聊天机器人及用户接受度等多个领域。由于E_q中未包含任何全文级证据，所有分析均严格限定于摘要信息。检索与筛选过程旨在识别与“全文证据使用策略”相关的间接线索，但直接针对该问题的文献缺失。

## 2. 核心主题与证据

现有摘要证据主要围绕AI技术（如聊天机器人、多智能体系统）的应用、用户接受度及未来展望展开。核心主题包括：
- **AI与聊天机器人的应用与挑战**：文献[2]和[5]探讨了ChatGPT及AI聊天机器人在客户服务中的背景、伦理挑战及用户依从性；[6]则聚焦于旅游行业对AI聊天机器人的采纳，发现感知有用性、信任和拟人化是关键因素。
- **用户接受度与理论框架**：[7]通过系统综述指出，感知有用性、信任和努力期望是AI技术接受度的正向预测因素，但文化场景中人类接触的需求可能无法被AI替代。[8]提出了向智能信息系统委托任务的理论框架。
- **多智能体与未来网络**：[1]和[3]分别涉及6G网络架构中的AI自主网络及多智能体学习系统，强调大规模自治与集成。
- **能源领域的代理模型**：[4]讨论了产消者（prosumers）在电力市场中的角色，涉及代理间的交互与市场设计。

这些主题均未直接涉及“全文证据使用策略”，但暗示了在AI与多智能体系统中，代理（agent）的决策依赖于数据与证据的整合。

## 3. 证据支持的研究方向

基于现有摘要证据，可推断出以下与“全文证据使用策略”间接相关的研究方向：
- **多智能体系统中的证据共享与委托**：[3]和[8]指出，多智能体系统及委托框架中，代理需要基于有限信息进行决策。当全文证据稀缺时，摘要级信息可能成为代理间通信与协作的主要依据。
- **AI系统的信任与证据质量**：[5]、[6]和[7]强调信任、感知智能和拟人化对用户接受AI的影响。这暗示在缺乏全文证据时，摘要的完整性和可信度直接影响AI代理的决策可靠性。
- **跨领域证据整合**：[1]和[4]展示了不同领域（通信、能源）中代理如何利用局部信息（如摘要）进行全局优化，这为设计全文稀缺时的证据融合策略提供了参考。

## 4. 摘要级证据的局限

本合成完全依赖摘要级证据，存在以下显著局限：
- **信息深度不足**：摘要仅提供研究的高层概述，缺乏方法细节、数据来源、实验设计及全文中的具体证据使用策略。例如，[2]和[7]虽提及挑战与伦理，但未说明如何从全文提取关键证据。
- **无法验证结论**：摘要中的发现（如[5]中拟人化对依从性的影响）无法通过全文细节进行交叉验证，限制了策略设计的可靠性。
- **领域偏差**：现有证据集中于AI与用户交互，未覆盖其他可能涉及全文与摘要数量失衡的领域（如法律、医学），导致策略通用性存疑。
- **缺乏直接相关性**：无一篇文献直接探讨“全文证据使用策略”，所有推断均为间接关联，可能偏离实际需求。

## 5. 谨慎结论

基于当前摘要级证据，当全文数量远少于摘要时，全文证据的使用策略应优先考虑以下原则：第一，利用摘要作为初步筛选与分类的依据，但需明确标注其局限性（如[7]中强调的自我报告数据偏差）；第二，在多智能体或委托框架中（[3]、[8]），代理应设计为对摘要证据进行置信度评估，并优先引用可验证的全文片段；第三，借鉴[2]和[5]中关于伦理与信任的讨论，策略需确保摘要证据的透明度与可追溯性。然而，这些结论高度推测性，需未来研究通过全文级证据进行实证检验。当前E_q无法支撑更具体的策略设计。

## 参考文献
[1] 6G Wireless Networks: Vision, Requirements, Architecture, and Key Technologies. IEEE Vehicular Technology Magazine. 2019.
[2] ChatGPT: A comprehensive review on background, applications, key challenges, bias, ethics, limitations and future scope. Internet of Things and Cyber-Physical Systems. 2023.
[3] Multi-agent systems: A survey. A Dorri, SS Kanhere, R Jurdak - Ieee Access, 2018 - ieeexplore.ieee.org. 2018.
[4] Electricity market design for the prosumer era. Nature Energy. 2016.
[5] AI-based chatbots in customer service and their effects on user compliance. Electronic Markets. 2020.
[6] Adoption of AI-based chatbots for hospitality and tourism. International Journal of Contemporary Hospitality Management. 2020.
[7] What factors contribute to the acceptance of artificial intelligence? A systematic review. Telematics and Informatics. 2022.
[8] The next generation of research on IS use: A theoretical framework of delegation to and from agentic IS artifacts. A Baird, LM Maruping - MIS quarterly, 2021 - misq.umn.edu. 2021.