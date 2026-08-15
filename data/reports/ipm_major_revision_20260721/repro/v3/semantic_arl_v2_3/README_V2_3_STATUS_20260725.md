# Semantic ARL v2.3：全新DeepSeek v4一致性確認實驗——狀態

生成時間：2026-07-25。協議凍結文件：`semantic_arl_v2_3_protocol_freeze_20260725.md`（凍結後未修改判定規則）。

## 為什麼要重跑

原計劃复用`schema_single_agent_v1`（`deepseek-chat`）作為V0，但V1/V2因為`deepseek-chat`已被API下架，被迫改用`deepseek-v4-pro`，造成V0與V1/V2模型版本不一致，無法做公平對照。按你的決定，V0/V1/V2全部用`deepseek-v4-pro`從頭重跑。

## 真實執行鏈路（全部deepseek-v4-pro，temperature=0.0，max_tokens=24000）

```
V0：schema-matched單智能體基線（scripts/run_v23_v0_baseline.py，30條查詢，真實API）
  ↓
B1：確定性結構修復（scripts/build_v23_b1.py，純規則，零API成本）
  ↓
V1：單智能體自我批判（scripts/run_v23_v1_self_critique.py，30條查詢，真實API）
V2：Reviewer–Reviser雙角色ARL（scripts/run_v23_v2_arl.py，30條查詢×2次呼叫，真實API）
```

過程中發現並修正一個問題：`deepseek-v4-pro`是推理模型，completion token的多數會被隱藏的`reasoning_content`吃掉，原本沿用舊腳本的`max_tokens=6000`會導致輸出完全空白（V1/V2冒煙測試最初都是0條verdict/0字節輸出）。調到`24000`後恢復正常。

另有一次操作失誤：第一次啟動V1全量任務後執行了`TaskStop`，但背景程序在真正終止前又多跑了21條查詢，這些用的是**舊B1**（推導自deepseek-chat的V0），已確認並清空，未混入最終數據。

## 真實結果

### 確定性發布門通過率（`gate_summary.json`）

| 條件 | n | 通過率 |
|---|---:|---:|
| V0（基線） | 30 | 90.0% |
| V1（自我批判） | 30 | 96.7% |
| V2（ARL） | 30 | **100.0%** |

### 盲評包（`v23_csp_blind_packet_coder_A/B.csv`）

- 固定抽60個V0錨點claim（僅限發布門通過的查詢，V0=27條可用查詢），追蹤同一claim在V1、V2的命運
- 60×3=180項，其中V1有5項、V2有2項在原地找不到對應claim，標記為`REMOVED`（不是靜默丟棄）
- 金鑰單獨存放於`v23_csp_gold_key_do_not_share.csv`，兩份coder檔案不含condition欄位

## 尚未完成，需要真人操作

180項盲評包已生成、已可發放，但**尚未有人工編碼**。按協議凍結文件的預先設定判準：V2相對V0或V1在CSP上的配對Wilcoxon檢定（Benjamini-Hochberg校正）必須q<0.05，才能恢復"ARL具有增量語義價值"的論斷；若不顯著，改寫為"CDMA提供證據邊界和確定性準入控制，ARL是條件化的語義審查機制"這個更保守但誠實的定位。

## 與其他已排隊任務的關係

現在待人工的盲評包一共三份：
1. 320對閾值驗證（R3-5，v3提交本身卡住的項目）
2. 151項v2.2語意CSP盲評
3. 180項v2.3語意CSP盲評（本次新增）

三份互相獨立，不能共用編碼員的同一批判斷去湊數；如果編碼員資源有限，建議優先順序仍是1 > 2 > 3，因為只有第1項是v3提交的硬性要求，第2、3項都是加分項。
