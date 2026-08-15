# E2 / R3-2 補齊：LLM Reviewer vs 確定性驗證器（Deterministic Validator）逐條一致率

日期：2026-07-27。本文件在查看任何結果**之前**寫成。

## 一、要補的缺口是什麼

當前 v7 對 E2、R3-2 的狀態是"實質性完成"：251-query schema-matched B0 和 deterministic gate 都已真實運行（gate pass=197/251），但**舊版 LLM Reviewer（M2 pipeline 中的 `review_draft()`）從未輸出可與 gate 逐條比對的結構化 item-level 判定**——它的輸出是整篇草稿的整體 JSON（`overall_score`、`major_issues`、`citation_issues` 字串列表、`accept_without_revision`），不是逐條引用編號的判定，因此無法回溯計算"Reviewer 分類 vs deterministic validator"的 precision/recall/F1。這不是一個可以靠翻找舊日誌解決的問題——舊輸出的資料結構本身就不支援這個比較。

## 二、這次補齊的方法（新實驗，非回溯舊資料）

不修改、不重新生成 251 個 B0 草稿本身（B0 保持凍結）。新增一個**獨立的、結構化輸出的 LLM Reviewer**，對同一批已凍結的 B0 草稿做結構層審查：

1. 對每個 query，用 `evaluate_metrics.py` 現有的 `_build_candidate_pool()`（不重新實作）取得該 query 在凍結語料庫中真正可檢索到的候選論文標題清單（deterministic gate 判定"引用是否對應真實文獻"時使用的同一份標題池）。
2. 把 B0 草稿的正文、參考文獻列表、以及這份候選標題清單一起交給 Reviewer（deepseek-v4-pro，temperature=0），要求它**只根據文字比對自行判斷**（不透露 gate 的規則或閾值），輸出結構化 JSON：
   - `orphan_citation_numbers`：正文中有引用標號但參考文獻列表找不到對應條目的編號
   - `uncited_bibliography_numbers`：參考文獻列表中存在但正文從未引用的條目編號
   - `suspect_fabricated_or_mismatched_numbers`：參考文獻條目的標題在候選論文清單中找不到明顯對應者
   - `overall_verdict`："RELEASE"（結構合規）或"BLOCK"（存在至少一項結構問題）
3. 把 Reviewer 的 `overall_verdict` 與 `schema_single_agent_per_query.csv` 裡该 query 真實的 `release`（pass/block）逐條比對。

## 三、樣本與範圍（不可事後更改）

- 全部 251 個 query，與現有 B0/gate 範圍完全一致，不抽樣、不篩選。
- 沿用已凍結的 B0 草稿文件（`data/expanded_outputs/schema_single_agent_v1/`），不重新生成。

## 四、分析計畫（不可事後更改）

1. 以 deterministic gate 的 `release`（pass/block）作為結構合規的參照標準（它是規則式、可審計的，不是語意金標準，只回答"這是否是一個結構乾淨的引用文檔"）。
2. 以 BLOCK 為正類，計算 Reviewer 的 accuracy、precision、recall、F1、混淆矩陣（TP/FP/FN/TN）。
3. 額外報告"原因層級"重疊率：Reviewer 標記的 orphan_citation_numbers 是否非空，與 gate 的 `text_orphans>0` 是否一致；uncited_bibliography_numbers 非空與 `uncited_bibliography_entries>0` 是否一致。
4. 不會因為結果不理想而更換比對方式或正類定義。

## 五、這個結果能不能證明什麼

- 若一致率高：說明 LLM Reviewer 可以作為 deterministic validator 的**近似替代或輔助信號**，這是對 R3-2/E2 的直接、真實回答。
- 若一致率低：如實報告，並解釋為結構性限制（例如 LLM 對"標題模糊匹配"的判斷閾值與 `_match_title(threshold=0.72)` 不同），不會把它包裝成"Reviewer 也做到了驗證器的功能"。
- 無論結果如何，這只回答"LLM Reviewer 是否能重現 deterministic gate 的結構判定"，**不涉及語意層 CSP/CSC，也不能替代 320/180 條人工盲評**。

## 六、輸出位置

`data/reports/ipm_major_revision_20260721/repro/v3/e2_r32_reviewer_vs_gate/`
