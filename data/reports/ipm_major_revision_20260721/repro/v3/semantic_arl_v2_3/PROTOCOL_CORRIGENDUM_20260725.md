# Semantic ARL v2.3 協議修訂說明（Corrigendum）

修訂時間：2026-07-25。不覆蓋、不修改`semantic_arl_v2_3_protocol_freeze_20260725.md`原文，僅在此追加說明。

## 修訂內容

原協議凍結文件第一段"條件命名"表格中，V0一欄寫的是：

> **複用現有真實數據**：`data/expanded_outputs/schema_single_agent_v1/`，Q31–Q60子集，已核實251條查詢全部真實生成，不重新調用API

這一條款已在正式運行前失效，原因：`deepseek-chat`模型已被API下架（HTTP 400，"The supported API model names are deepseek-v4-pro or deepseek-v4-flash"），導致V1/V2被迫使用`deepseek-v4-pro`。如果V0繼續複用`deepseek-chat`生成的舊數據，會在V0與V1/V2之間引入模型版本混淆，違反協議本身"同一模型"的公平性要求。

**修訂為**：V0、B1、V1、V2全部基於`deepseek-v4-pro`重新生成，均為Q31–Q60共30條查詢，temperature=0.0，max_tokens=24000，不複用任何`deepseek-chat`時期的舊輸出。

## 這處修訂發生的時間點

修訂決策發生在V0正式全量生成**之前**（僅完成2條查詢的冒煙測試後），因此不構成"看到結果後修改規則"——冒煙測試階段還沒有任何V1/V2對比結果，模型版本問題是在排查冒煙測試失敗原因（token預算耗盡於推理過程）時發現的技術限制，觸發了對V0數據來源的重新評估，不是為了讓某個方向的結果更好看而回頭改判定規則。

## 受影響與不受影響的部分

- **不受影響**：協議凍結文件裡關於確定性門位置、Reviewer四類判定方案（含EVIDENCE_UNAVAILABLE）、CSP/CSC/false removal/unsupported retention四個指標定義、預先設定的顯著性判準（Wilcoxon+BH校正q<0.05）——全部保持原樣，未修改。
- **受影響**：僅V0的數據來源一項，已按上述說明修訂並執行。

## 真實執行結果（供交叉核對）

- V0（30條，deepseek-v4-pro）→ 結構門通過率90.0%
- B1（30條，純規則修復，零API成本）
- V1（30條，deepseek-v4-pro，同一份B1起點）→ 結構門通過率96.7%
- V2（30條，deepseek-v4-pro，同一份B1起點）→ 結構門通過率100.0%

三者模型版本已統一，不存在GPT審查提出的模型混淆問題。
