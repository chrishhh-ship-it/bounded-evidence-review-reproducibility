## 1. 检索与筛选概览

本合成基于提供的8篇文献证据集（E_q），涵盖多智能体系统在代码生成、网络安全、电动汽车充电管理、会计信息安全、空间设计决策支持及供应链管理等多个应用领域。文献发表年份从2019年至2025年，其中2025年文献3篇[2][3][5]，2024年2篇[4][6]，2023年1篇[1]，2020年1篇[7]，2019年1篇[8]。所有证据均来自摘要级信息，未涉及全文内容。

## 2. 核心主题与证据

多智能体系统（MAS）在多个领域展现出应用潜力，但证据显示其性能存在显著的条件依赖性。在代码生成领域，研究发现语义等价的输入会导致MAS性能大幅下降，7.9%至83.3%的初始成功问题无法解决，其中75.3%的失败源于“规划者-编码者差距”[2]。这一差距表现为规划代理将需求分解为不充分的规范，编码代理随后在代码生成过程中误解复杂逻辑[2]。类似地，在电动汽车充电管理中，现有研究在个体用户需求、能源管理和系统连接性方面存在显著空白[5]。在会计信息安全领域，多智能体演化博弈分析揭示了不同主体在信息泄露、数据篡改等挑战下的策略选择规则[6]。在空间设计决策支持中，多智能体仿真被用于辅助决策者评估设计方案[7]。供应链管理领域的文献综述则概述了MAS在该领域的应用现状[8]。

值得注意的是，证据集中有一篇关于蚊虫控制的系统综述[1]，其元分析显示Bti处理对摇蚊科和甲壳纲动物的丰度存在一致的负面影响，但该影响的分析窗口从1天到21年不等，且研究在方法学、严谨性和时空尺度上高度可变[1]。这一发现直接回应了研究问题：当分析窗口起始年份不同时，趋势可能发生逆转。然而，该文献属于生态学领域，与多智能体系统无直接关联。

## 3. 证据支持的研究方向

基于现有证据，多智能体合成管线在处理引文时应关注以下方向：首先，需明确记录每项证据的时空分析窗口，特别是当趋势可能因起始年份不同而改变时[1]。其次，应建立机制以识别和量化“规划者-编码者差距”导致的信息损失[2]，这要求管线能够追踪多阶段转换过程中的信息流。第三，需考虑不同应用领域（如代码生成[2][4]、网络安全[3]、能源管理[5]、会计安全[6]）中MAS的特定条件依赖性，避免跨领域泛化。第四，应整合多智能体演化博弈分析[6]和仿真方法[7]来评估不同策略选择下的结果变化。

## 4. 摘要级证据的局限

本合成完全依赖摘要级信息，存在以下固有局限：首先，无法获取研究方法细节、样本量、效应量等关键参数，限制了证据强度的评估。例如，关于Bti处理影响的分析窗口具体如何影响趋势逆转，摘要未提供足够信息[1]。其次，摘要可能选择性报告正向结果，存在发表偏倚风险。第三，多篇文献[3][7][8]的摘要信息极为简略，无法判断其具体发现与多智能体合成管线的相关性。第四，不同文献对“多智能体系统”的定义和应用场景差异显著，从代码生成[2][4]到电动汽车充电[5]再到会计安全[6]，摘要级证据无法支持对这些异质性研究的深入比较。

## 5. 谨慎结论

基于现有摘要级证据，多智能体合成管线在处理引文时应建立明确的时空上下文标注机制，特别是当分析窗口（如起始年份）可能影响趋势方向时[1]。管线需要设计信息损失检测模块，以应对“规划者-编码者差距”导致的性能波动[2]。然而，由于证据集高度异质且缺乏全文信息，任何关于趋势逆转的具体机制或普遍性结论均不成立。建议在获得全文证据后，进一步分析不同分析窗口下MAS性能变化的模式，并探索多提示生成等修复方法[2]在跨领域应用中的有效性。

## 参考文献
[1] Effects of mosquito control using the microbial agent Bacillus thuringiensis israelensis (Bti) on aquatic and terrestrial ecosystems: a systematic review. Environmental Evidence. 2023.
[2] Understanding and Bridging the Planner-Coder Gap: A Systematic Study on the Robustness of Multi-Agent Systems for Code Generation. Semantic Scholar. 2025.
[3] MAD-CTI: Cyber threat intelligence analysis of the dark web using a multi-agent framework. S Shah, VK Madisetti - IEEE Access, 2025 - ieeexplore.ieee.org. 2025.
[4] Transforming Software Development: A Study on the Integration of Multi-Agent Systems and Large Language Models for Automatic Code Generation. 2024 12th International Conference in Software Engineering Research and Innovation (CONISOFT). 2024.
[5] A Review of Support Tools for User-Centric Electric Vehicle Charging Management Based on Artificial Intelligence and Multi-Agent System Approaches. Energies. 2025.
[6] Research on Accounting Information Security Control Strategy under the Background of Digital Intelligence: Based on the Evolutionary Game Perspective of Multi-agent. Proceedings of the 5th International Conference on Computer Information and Big Data Applications. 2024.
[7] Decision support systems based on multi-agent simulation for spatial design and management of a built environment: the case study of hospitals. D Esposito, D Schaumann, D Camarda… - … on Computational Science …, 2020 - Springer. 2020.
[8] A Literature Review on the State of the Art of Multi-agent Systems in Supply Chain Management. Lecture notes in logistics. 2019.