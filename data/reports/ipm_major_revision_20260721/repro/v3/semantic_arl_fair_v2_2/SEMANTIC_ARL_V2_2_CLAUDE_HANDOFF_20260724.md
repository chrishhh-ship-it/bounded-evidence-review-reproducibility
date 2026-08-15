# Semantic ARL v2.2 确认性试点：执行、审计与 Claude 交接说明

## 一、这轮实验真正回答什么

本轮比较同一模型提供商内部的两种两阶段流程：

- **SELF**：同一角色先审查证据支持度，再按审查意见修订；
- **ARL**：Reviewer 与 Reviser 使用分离角色，Reviewer 只判定支持状态并给出指令，Reviser 依据原主张、指令和对应证据修订。

两组均从同一 B1 输入出发，使用相同模型版本、temperature=0、token 上限、两次调用预算和最多三次技术重试。Q31-Q33 仅用于校准；Q34-Q60 在协议冻结后运行，属于确认性集合。

**主要假设不是“ARL 删除得更多”，而是 ARL 在不造成过度删除的前提下，提高最终保留主张的人工判定语义支持度。**模型自己的 SUPPORTED/PARTIAL 判定只能描述处理行为，不能充当真值。

## 二、冻结与可复现边界

- 协议：`semantic_arl_fair_v2_2_20260724`
- 冻结文件：`data/expanded_outputs/semantic_arl_fair_v2_2/semantic_arl_fair_v2_2_20260724/confirmatory_freeze_20260724.json`
- 运行脚本 SHA-256：`386055f9bd9a8efdd47cd15422399631c40c50f198ca542ec2c8013986ff5158`
- 提供商/模型：DeepSeek `deepseek-v4-pro`；Kimi `moonshot-v1-32k`；OpenAI-compatible 代理 `gpt-4o-mini`。第三项不是 OpenAI 官方端点，论文中必须按 OpenAI-compatible provider 如实报告。
- 模型未在三次内返回覆盖全部稳定 claim ID 的合法 JSON 时，该运行判为失败；没有在结果出来后反复重跑到成功。

## 三、确认性覆盖与自动过程结果

| 提供商 | 可配对查询 | 排除的未配对查询 | SELF保留率 | ARL保留率 | SELF删除率 | ARL删除率 | 保留主张丢失全部引用 SELF/ARL |
|---|---:|---|---:|---:|---:|---:|---:|
| deepseek | 17 | Q36, Q37, Q38, Q39, Q46, Q48, Q51, Q53, Q56, Q60 | 80.0% | 72.1% | 20.0% | 27.9% | 0/0 |
| kimi | 23 | Q36, Q38, Q46, Q51 | 90.5% | 88.8% | 9.5% | 11.2% | 3/9 |
| openai | 26 | Q52 | 95.9% | 88.5% | 4.1% | 11.5% | 16/11 |

自动结果只说明：DeepSeek 与 OpenAI-compatible 条件下 ARL 更保守；Kimi 的主要变化是更多收窄。它不能区分“正确删除”与“误删”。此外，Kimi 和OpenAI-compatible 修订偶尔删除了保留主张的全部引用标记，说明语义层之后仍需确定性发布门检查“保留的可验证主张是否仍有合法引用”。

## 四、人工盲评设计

- 去重后需独立判断 **151 项**；
- 隐藏映射共 **396 行**；
- 其中随机主样本 264 行，仅此层用于确认性比较；
- 修改主张诊断样本 132 行，只解释机制和误删，不能并入主效应。
- 同一“主张+证据”若在多个条件完全相同，只评一次，再映射到对应隐藏条件，避免编码员反复看到重复文本产生记忆效应。
- 两位编码员拿到的项目集合相同但顺序不同；工作表不含提供商、条件、动作或抽样层信息。

评分：`FULLY_SUPPORTED`、`PARTIALLY_SUPPORTED`、`UNSUPPORTED`、`NOT_ASSESSABLE`。主结果为保留主张中的严格完全支持率；同时报告宽松支持率、每个原始主张的严格支持产出率，以及删除项中原本仍有支持的误删率。

## 五、人工执行步骤

1. 将 `semantic_arl_coder_A.xlsx` 与 `semantic_arl_coder_B.xlsx` 分别发给两位编码员；**不要发送 `DO_NOT_SHARE_condition_key.csv`**。
2. 两位编码员不得在全部标签冻结前讨论具体项目；只依据表内主张和证据，不使用外部知识补齐。
3. 完成后先保存原文件和 SHA-256，再运行评分脚本。脚本先计算独立一致性；若有分歧，自动生成 adjudication 表，不会直接替作者决定。
4. 裁决完成后才解盲并生成 SELF/ARL 条件结果。任何条件比较都只用`random_primary` 主样本；诊断层单列。

评分命令：

```powershell
python scripts\score_semantic_arl_human_packet_v2_2.py
```

如有分歧，填完自动生成的 `semantic_arl_adjudication.xlsx` 后：

```powershell
python scripts\score_semantic_arl_human_packet_v2_2.py `
  --adjudicated data\expanded_outputs\semantic_arl_fair_v2_2\semantic_arl_fair_v2_2_20260724\human_evaluation\semantic_arl_adjudication.xlsx
```

## 六、当前可以与不可以写进论文的结论

**现在可以写：**在冻结的多提供商配对试点中，角色分离改变了审查/修订行为，总体更倾向于收窄或删除；所有成功运行都未新增超出原引用集合的编号；实验也暴露了语义修订后引用标记可能丢失，因此最终发布门必须确定性校验结构。

**现在不可以写：**ARL 已提高语义忠实度、减少语义幻觉、优于 self-critique，或已经“救回”ARL。上述主张必须等待双人盲评结果，并同时检查严格支持率、支持产出率和误删率；只提高精度但大量删除有效主张，也不能称为全面改善。

## 七、交给 Claude 的审查重点

请 Claude 核查：①确认性协议是否真正同起点、同参数、同调用预算；②失败运行的配对排除是否透明；③随机主样本与诊断样本是否严格分开；④评分是否同时惩罚误删和引用丢失；⑤论文是否把确定性 validator 定位为最终发布门，把 Reviewer-Reviser定位为语义识别与文本修订模块，而不是把多智能体继续写成唯一创新来源。

## 八、关键文件及哈希

- `data/expanded_outputs/semantic_arl_fair_v2_2/semantic_arl_fair_v2_2_20260724/confirmatory_freeze_20260724.json`  
  SHA-256: `529bdd0b6f95941e549e7ddd501e130cb68d2714a92359c42cadf336c9fa5090`
- `data/expanded_outputs/semantic_arl_fair_v2_2/semantic_arl_fair_v2_2_20260724/analysis/automatic_process_summary.json`  
  SHA-256: `f2424526894c655c07538f90c88b3273293298fda7a6b8bb4a6d0900307c6497`
- `data/expanded_outputs/semantic_arl_fair_v2_2/semantic_arl_fair_v2_2_20260724/analysis/AUTOMATIC_PROCESS_AUDIT.md`  
  SHA-256: `7789de2302c35ae808122fdce19dcb842aac95823ce1e9dde826c9cb45bdd72f`
- `data/expanded_outputs/semantic_arl_fair_v2_2/semantic_arl_fair_v2_2_20260724/human_evaluation/semantic_arl_coder_A.xlsx`  
  SHA-256: `9e6d528a65d273924fab35cd32932c525677e39e4330b3d2eb6f87a3c018b753`
- `data/expanded_outputs/semantic_arl_fair_v2_2/semantic_arl_fair_v2_2_20260724/human_evaluation/semantic_arl_coder_B.xlsx`  
  SHA-256: `3fc50077823dda14e50f5f2b4cd17ac49fc96e43a5dd268b7df9edb0d9d4588d`
- `data/expanded_outputs/semantic_arl_fair_v2_2/semantic_arl_fair_v2_2_20260724/human_evaluation/DO_NOT_SHARE_condition_key.csv`  
  SHA-256: `8e1b247737da35b6c3ddadd6113828f014a4b3702a3f087e54955b2af0c9c041`
- `data/expanded_outputs/semantic_arl_fair_v2_2/semantic_arl_fair_v2_2_20260724/human_evaluation/packet_manifest.json`  
  SHA-256: `cc650c60a02bc4ead3f2f246aa5f9466df5713c2a4b1871a860f3faa1b201803`
