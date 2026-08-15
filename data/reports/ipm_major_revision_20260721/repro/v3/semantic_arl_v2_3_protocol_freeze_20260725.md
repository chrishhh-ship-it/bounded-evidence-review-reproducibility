# Semantic ARL v2.3 协议凍結

冻结时间：2026-07-25，在查看任何v2.3输出之前写下。本协议解决GPT提案与既有工作之间的两处冲突（条件命名、确定性门位置），此后不再更改判定规则。

## 条件命名（取代GPT提案的B0/B1/B2，避免与既有B0–B3记号混淆）

| 记号 | 内容 | 起点 | 生成方式 |
|---|---|---|---|
| V0 | schema-matched单智能体基线（无修订） | 直接从证据集生成 | **复用现有真实数据**：`data/expanded_outputs/schema_single_agent_v1/`，Q31–Q60子集，已核实251条查询全部真实生成，不重新调用API |
| V1 | 单智能体自我批判 | **同一份B1草稿**（见下方"确定性门位置"） | 新生成，30条查询 |
| V2 | Reviewer–Reviser双角色ARL | **同一份B1草稿** | 新生成，30条查询，Reviewer只判定不改写，Reviser只依指令修订 |

V1和V2必须从同一个起点出发，这是v2.2"公平确认性试点"已经验证过的关键设计，v2.3延续，不倒退回V1从V0直接出发、V2从别的草稿出发这种不公平对照。

## 确定性门的位置

GPT提案没有交代这一点，本协议明确：**确定性发布门在每个条件生成完成之后统一施加，作为最后一步，不作为V1/V2修订前的预筛选**。具体顺序：

```
V0/V1/V2 各自生成最终文本
        ↓
对V0/V1/V2的最终文本，用同一个deterministic release gate判定
（复用 scripts/evaluate_metrics.py 的解析与匹配逻辑，
 0.72标题阈值，与v3正文一致）
        ↓
只对"通过发布门"的输出做claim抽取和CSP/CSC盲评
（未通过发布门的输出单独统计gate pass rate，
 不与结构不合规的输出混进语义评估）
```

理由：如果先筛选再修订，就没法比较"V1/V2各自的产出里有多少能通过发布门"这个本身就有信息量的指标；如果修订后不筛选直接送盲评，语义评估可能被结构违规污染。

## Reviewer判定方案（四类，证据可用性检查写入prompt本身）

不再采用"先生成INSUFFICIENT，再靠脚本事后按摘要长度回溯分类"的做法（这是HEDGE v2.3模拟被审计指出的方法论弱点）。改为：**Reviewer在judgement阶段就先检查证据是否存在**，证据缺失时直接输出`EVIDENCE_UNAVAILABLE`，不强迫模型对着空文本猜测支持与否：

| 判定 | 触发条件 | 处理 |
|---|---|---|
| `EVIDENCE_UNAVAILABLE` | 被引记录的摘要字段为空/未提取到 | 保留主张，加注"证据不可得"警语（不是静默删除，也不当作语义未支持） |
| `SUPPORTED` | 摘要明确支持该主张 | KEEP |
| `PARTIAL` | 摘要主题相关但不完全支持具体措辞 | NARROW（收窄措辞以匹配摘要实际内容） |
| `INSUFFICIENT` | 摘要存在但内容不足以判断 | REMOVE（真实证据不足，不是证据缺失） |
| `CONTRADICTED` | 摘要内容与主张冲突 | REMOVE |

这样`EVIDENCE_UNAVAILABLE`和`INSUFFICIENT`在生成时就是两个不同的判定，不需要事后用字符长度去猜哪些INSUFFICIENT其实是缺证据——这是对上一轮审计意见的直接采纳。

## 盲评指标（先定义分母，防止审计意见R3-4式的口径漂移）

- **CSP**（Claim-Support Precision）= 人工判定为SUPPORTED的保留主张数 / 全部保留主张数
- **CSC**（Claim-Support Coverage）= 人工判定为SUPPORTED的保留主张数 / 全部原始主张数（含被删除的）——本轮只覆盖"带引用的句子"这个既有范围，不含未带引用但需要证据的主张，这一点必须在报告里注明，不能写成完整CSC
- **false removal rate** = REMOVE的主张中，人工判定其实SUPPORTED或PARTIAL的比例
- **unsupported retention rate** = KEEP/NARROW的主张中，人工判定其实UNSUPPORTED或CONTRADICTED的比例

## 预先设定的显著性判准（写在结果出来之前）

V2（ARL）相对V0（基线）或V1（自我批判）在CSP上的配对Wilcoxon检验，Benjamini-Hochberg校正后 q < 0.05，才能恢复"ARL具有增量语义价值"的论断。仅在false-removal rate上有改善但CSP不显著，只能写"ARL在减少误删上可能有价值，语义精确度上证据不足"，不能笼统写"ARL更好"。

## 范围与资源现实

- 仅deepseek单一provider，Q31–Q60共30条查询（复用既有extended pilot子集），不复制v2.2的三provider设计——资源和时间都不允许在8/20前再做一轮三provider confirmatory。
- 预估新增API调用：V1约30次，V2约60次（Reviewer+Reviser），共约90次，成本可忽略（参考此前B2/B3实测均值10–20秒/次）。
- 本协议冻结后，不得因为看到中间结果而修改上述规则；如需修改，必须新开v2.4并说明理由。
