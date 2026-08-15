## 1. 检索与筛选概览

本次检索基于给定的证据集E_q，共包含8条记录。其中，[1]和[2]直接涉及系统综述流程中的自动化与多智能体协作机制，[1]明确提出了“对抗式多智能体系统”用于作者-审稿人工作流，[2]则聚焦于EPPI-Reviewer和Copilot 365在系统综述自动化中的评估方案。其余6条记录[3]-[8]均为不同学科领域的公开审稿意见，其标题与摘要内容与“孤儿引用检出率”或“对抗式审阅循环”无直接关联。因此，本合成分析的核心证据来源为[1]和[2]。

## 2. 核心主题与证据

核心主题为：在对抗式审阅循环中，审阅智能体如何通过专项检查清单提升孤儿引用（即未被现有数据库或引用网络充分收录的文献）的检出率。

[1]提出了一个对抗式多智能体系统框架，其中作者与审稿人智能体通过可验证证据与批评循环进行交互。该框架的核心在于“可验证证据”与“批评循环”机制，这为设计专项检查清单提供了理论基础：审阅智能体应重点检查文献引用链的完整性，特别是那些在主流数据库中缺失或被忽视的引用。[2]则提供了自动化筛选的实证方案，其方法包括使用优先化筛选（PS）并设定20%和40%的人工筛选阈值，以计算被优先化筛选遗漏的相关引用比例。该方案直接指向了孤儿引用的检出问题：通过设定不同的筛选阈值并评估遗漏率，可以量化自动化工具在捕捉非常规引用方面的性能边界。

## 3. 证据支持的研究方向

基于现有证据，以下研究方向值得探索：

- **阈值敏感性分析**：借鉴[2]中20%和40%阈值的设定方法，研究在对抗式审阅循环中，不同筛选阈值对孤儿引用检出率的影响，寻找最优平衡点。
- **引用完整性校验清单**：依据[1]的“可验证证据”原则，开发一套专门用于校验引用完整性的检查清单，包括但不限于：检查参考文献是否包含灰色文献、非英语文献、预印本及跨学科来源。
- **遗漏模式分析**：利用[2]中“计算被遗漏的相关引用比例”的方法，系统分析孤儿引用的常见遗漏模式（如特定出版年份、语言、研究类型），从而指导审阅智能体进行针对性补充检索。
- **人机协作验证**：结合[2]中人工与自动化结果的一致性评估（Cohen’s Kappa），设计对抗式循环中的人工复核节点，专门用于验证自动化工具对孤儿引用的判断。

## 4. 摘要级证据的局限

本合成分析存在显著局限。首先，[1]仅提供摘要级信息，未详细说明其对抗式系统的具体检查清单构成或孤儿引用检出率的实测数据。[2]虽提供了详细的方法学方案，但作为研究方案（protocol），其结论尚未产生，无法提供实证结果。其次，[3]-[8]均为不相关的公开审稿意见，无法为孤儿引用检出提供任何直接证据。因此，本分析中的研究方向均基于对现有框架的合理推断，而非来自已完成的实证研究。

## 5. 谨慎结论

在对抗式审阅循环中，审阅智能体应优先采用以下专项检查清单以最大化孤儿引用检出率：**基于阈值调整的遗漏率监控清单**（源自[2]）和**引用完整性校验清单**（源自[1]）。然而，这些清单的有效性尚待实证验证。当前证据仅支持将孤儿引用检出作为系统设计的一个可量化目标，并建议通过设定多级筛选阈值和人工复核节点来降低遗漏风险。在获得更充分的实证数据前，不应将上述清单视为已优化的解决方案。

## 参考文献
[1] Adversarial Multi-Agent System for Systematic Literature Reviews: Author–Reviewer Workflows with Verifiable Evidence and Critique Loops. CrossRef. 2026.
[2] Study protocol for evaluating automation of systematic review processes with EPPI-Reviewer and Copilot 365 in updating the cataract evidence gap map. Systematic Reviews. 2026.
[3] Reviewer #2 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[4] Reviewer #1 (Public review): Agent-based modeling reveals how bats navigate dense group emergences. CrossRef. 2026.
[5] Reviewer #2 (Public review): SICKO: Systematic Imaging of Caenorhabditis Killing Organisms. CrossRef. 2025.
[6] Reviewer #1 (Public review): SICKO: Systematic Imaging of Caenorhabditis Killing Organisms. CrossRef. 2025.
[7] Reviewer #1 (Public Review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.
[8] Reviewer #2 (Public review): Conservation of the cooling agent binding pocket within the TRPM subfamily. CrossRef. 2024.