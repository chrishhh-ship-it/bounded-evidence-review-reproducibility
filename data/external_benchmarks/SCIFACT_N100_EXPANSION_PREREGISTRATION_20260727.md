# SciFact 同模型 vs 跨模型擴大試點：預先登記（n=40 → n=100）

日期：2026-07-27。本文件在查看任何 n=100 結果**之前**寫成。

## 一、動機

n=40 下，同模型最終裁決 87.5%/0.865、跨模型最終裁決 90.0%/0.896，V0=90.0%/0.896；McNemar 精確二項式檢定（V0 vs 同模型、V0 vs 跨模型、同模型 vs 跨模型）**全部 p=1.0**，未達顯著。逐條核對顯示跨模型在 5 個不一致案例中勝 3、同模型勝 2，方向支持"跨模型審查不會出現同模型審查的下降"這一假設，但 n=40 的檢定力不足以把方向性信號轉為顯著結果。這是目前"多智能體跨模型審查是否優於同模型自我審查"這條線索裡最有希望、也最需要擴大樣本的部分。

## 二、樣本量與選樣規則（不可事後更改）

- 從 n=40 擴大到 **n=100**。
- 選樣規則沿用 `run_official_scifact_semantic_pilot.py::load_records()`：對官方 `claims_dev.jsonl` 按檔案順序取固定前 n 筆非 AMBIGUOUS 記錄（`len(selected) >= n` 即停止），與 n=40 版本一致、可稽核。
- 本輪對全部 100 筆重新生成同模型 V0/Reviewer/Final（`scifact_semantic_pilot_n100/`），跨模型試點**複用同一批 V0 草稿**（`--reuse-v0-from`），保證兩個條件的 V0 完全相同，如同 n=40 版本的做法。
- 輸出目錄：`data/external_benchmarks/scifact_semantic_pilot_n100/`、`data/external_benchmarks/scifact_cross_model_pilot_n100/`，與 n=40 版本分開保存。

## 三、模型與參數（不變）

- 同模型：Draft/Reviewer/Adjudicator 均為 deepseek-v4-pro，temperature=0。
- 跨模型：Draft/Adjudicator 為 deepseek-v4-pro，Reviewer 為 Kimi moonshot-v1-32k，temperature=0。

## 四、分析計畫（不可事後更改）

1. 計算 V0、同模型最終、跨模型最終三者的 accuracy 與 macro-F1（沿用 `score_scifact_cross_vs_same_model.py` 既有函式，不重新實作）。
2. 對三組配對（V0 vs 同模型、V0 vs 跨模型、同模型 vs 跨模型）分別做**精確二項式 McNemar 檢定**（沿用既有 `mcnemar()` 函式）。
3. 若三個檢定同時檢視，對其 p 值做 BH-FDR 校正（q<0.05），與本專案其他多重比較慣例一致。
4. 逐條列出不一致案例（discordant pairs），報告跨模型/同模型各自勝出的筆數，作為方向性輔助判讀。

## 五、承諾

- 本輪只擴大一次（40→100），不會在看到 n=100 結果後才決定是否繼續擴大到更大樣本。
- 若校正後仍不顯著，將如實報告"方向一致、樣本量仍不足"，不更換檢定方法或校正方式去湊顯著性。
- 若顯著，將明確標註"跨模型審查在 SciFact 外部公共基準上的方向"，不代表論文主要基準或已解決 320/180 條人工盲評缺口。
