# ALCE 結構層擴大試點：預先登記（n=15/dataset → n=40/dataset）

日期：2026-07-26。本文件在查看任何 n=40 結果**之前**寫成，用於凍結本輪擴大試點的樣本量、選樣規則、指標定義與分析計畫。

## 一、擴大動機

在 n=15/dataset 下，對 ALCE 的 V0 vs V2 引用結構指標（citation_index_validity、sentence_citation_coverage）做配對 Wilcoxon 符號等級檢定，原始 p 值為 ASQA(0.317, 0.068)、QAMPARI(0.025, 0.034)；以本項目一貫的 BH-FDR（4 檢定為一組 family, q<0.05）校正後，**全部未達顯著**。同時觀察到 30 對配對中沒有任何一對是 V2 比 V0 更差（0 pairs worsened），只是平局比例過高（多為 V0 已達 100% 的天花板）導致檢定力不足。因此擴大樣本量以提高檢定力，檢驗這個方向性信號能否轉為統計顯著結果。

## 二、樣本量與選樣規則（不可事後更改）

- 每個資料集（ASQA、QAMPARI）從 n=15 擴大到 **n=40**。
- 選樣規則沿用原腳本 `select_records()`：對官方 `asqa_eval_gtr_top100.json` / `qampari_eval_gtr_top100.json` 取**固定前 n 筆**（`records[:40]`），與 n=15 版本一致、可稽核、非依輸出結果調整。
- n=40 樣本天然包含原 n=15 樣本的全部 15 筆（因為都是同一份檔案的前綴），但**本輪會用同一套腳本、同一組參數（deepseek-v4-pro, temperature=0, max_tokens=24000）對全部 40 筆重新生成 V0/V1/V2**，不會把舊 n=15 的輸出和新生成的 25 筆混用，以保持單一批次內部一致性、避免生成環境漂移造成的混淆。
- 輸出目錄：`data/external_benchmarks/alce_official_pilot_n40_structural/`（與 n=15 版本 `alce_official_pilot_n15_expanded/` 分開保存，不覆蓋，供追溯比較）。

## 三、指標定義（不變）

沿用 `scripts/external_benchmark/score_alce_official_pilot.py::citation_diagnostics()` 的既有定義，不重新實作：
- `citation_index_validity` = 有效引用標記數 / 全部引用標記數（每筆記錄的連續比例）
- `sentence_citation_coverage` = 帶引用的句子數 / 全部句子數（每筆記錄的連續比例）
- 答案品質指標（Str-EM/Str-Hit/QAMPARI F1）沿用官方 ALCE eval.py 公式，作為描述性背景資訊一併報告，但不是本輪擴大要驗證的假設。

## 四、分析計畫（不可事後更改）

1. 對每個資料集分別計算 V0 vs V2 的配對差異（`citation_index_validity`、`sentence_citation_coverage`），共 4 組配對序列。
2. 對每組做**配對 Wilcoxon 符號等級檢定**（雙尾），沿用 `scripts/external_benchmark/test_alce_structural_significance.py` 既有邏輯，不重新實作統計檢定。
3. 對這 4 個檢定的 p 值做 **Benjamini-Hochberg FDR 校正**，顯著性門檻 **q<0.05**（與本專案其他配對檢定一致的慣例）。
4. 同時報告方向性描述統計：提升/下降/未變筆數，作為輔助判讀（尤其在校正後仍不顯著時，用於區分"零效果"與"效果存在但檢定力不足"）。
5. V0/V1/V2 三條件的答案品質指標（Str-EM 等）僅做描述性報告，不納入本輪的顯著性檢定範圍（避免多重比較膨脹）。

## 五、承諾

- 本輪只擴大樣本量一次（15→40），不會在看到 n=40 結果後再迭代擴大到更大樣本才報告。
- 若校正後仍不顯著，將如實報告"方向一致、樣本量不足以達統計顯著"，不會因此更換檢定方法或校正方式去湊顯著性。
- 若顯著，將明確標註這是外部基準（ALCE）、結構層指標的結果，不代表論文主要基準或語意層的結論，避免與 v3 摘要的現有表述產生範圍衝突。
