# Semantic ARL 受控試點（Q31–Q60，30 條查詢）

生成時間：2026-07-24。範圍：v3 之外的新增探索性實驗，尚未寫入任何論文版本正文，也未修改 v3 的任何結果。

## 設計

四組條件，共用同一批 Q31–Q60（extended pilot，MAS 單領域，與論文既有的 60-query 擴展先導方法論一致），共用同一 E_q：

| 條件 | 內容 | 生成方式 |
|---|---|---|
| B0 | schema-matched 單智能體（已存在於 v3） | 直接複用 `schema_single_agent_v1`，未重新生成 |
| B1 | 確定性結構修復（移除不在 E_q 內的正文引用、移除未被引用的參考文獻條目） | 純規則腳本，零 API 成本 |
| B2 | 同一模型對自己 B0 草稿做單次語義自我批判與修訂 | 1 次 API 呼叫/query |
| B3 | Semantic Reviewer（只判定不改寫）→ Semantic Reviser（只依指令修訂，不可新增引用） | 2 次 API 呼叫/query |

Claim 切分單位（所有條件用同一規則，凍結後才套用）：含 `[N]` 引用標記的句子。

## 已完成、可自動驗證的結果

`automatable_pilot_stats.json`：

- 結構完整性：B0/B1/B2/B3 的 ICP/BMR 全部維持 100%，語義修訂沒有破壞引用結構。
- Orphan rate：B0/B2 = 7.08%，B1 = 0%（規則移除後必然），B3 = 3.19%（語義修訂順帶清掉了部分未引用條目）。
- 成本：B2 平均10.3秒/query，B3平均20.0秒/query（含Reviewer+Reviser兩次呼叫）。全部30條pilot query的B2+B3合計API成本可忽略（DeepSeek定價下遠低於1美元）。
- B3 Reviewer 自報的判定分佈（**注意：這是模型自己的判斷，不是獨立人工核驗，不能當CSP/CSC使用**）：SUPPORTED 57.2%、PARTIAL 19.7%、INSUFFICIENT 23.1%、CONTRADICTED 0%。分佈不是全SUPPORTED的退化結果，顯示Reviewer確實在做判別。

## 已知問題與修復記錄（誠實揭露）

Q51 的 Reviewer 呼叫在 `max_tokens=2500` 處被截斷，原始JSON陣列不完整，導致初次解析得到0個verdict。沒有重新呼叫API蒙混過關，而是：

1. 寫了bracket-counting的救援解析器，從截斷回應中恢復所有語法完整的verdict物件（24個，0個丟棄）；
2. 只重跑Reviser（不重跑Reviewer，省成本），用救援後的24個verdict產生Q51的最終B3輸出；
3. 在Q51的metadata裡誠實記錄了這個修復過程（`repair_note`欄位）。

## 尚未完成、需要真人操作的部分

**已生成但未填寫的盲評包**：`semantic_csp_blind_packet_coder_A.csv` / `_coder_B.csv`，各150條（B0/B2/B3各50條，隨機交錯排序，條件身份已隱藏），金鑰隔離在 `semantic_csp_gold_key_do_not_share.csv`。

**這會和已有的320對結構閾值盲評包疊加**，兩份盲評工作現在都在排隊等人工：
- 320對（title-match，0.72閾值驗證，R3-5）
- 150條（本次，CSP/CSC，B0 vs B2 vs B3）

兩位編碼者需要：獨立填寫verdict欄位（SUPPORTED/PARTIAL/CONTRADICTED/INSUFFICIENT）、不互相參考、不看金鑰，完成後解盲計算kappa，再按條件算CSP（SUPPORTED/總數）和CSC，並報告95% CI。

## 這個試點能回答、但還不能回答的問題

**能自動回答**：語義修訂沒有破壞結構層（ICP/BMR仍100%），B3確實會拒絕/修改部分claim（不是空轉）。

**還不能回答**（需要上面的盲評結果）：B3是否比B2（純自我批判）在CSP/CSC上有統計顯著提升——這才是GPT提案裡"能否救回ARL"的關鍵判準。目前只能說：技術管線已經建好、真實跑過、結構層乾淨，語義層的真正結果懸而未決。
