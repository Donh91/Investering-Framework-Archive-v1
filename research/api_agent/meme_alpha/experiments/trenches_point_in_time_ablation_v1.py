from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

EXPERIMENT = "TRENCHES_POINT_IN_TIME_G2_SOURCE_G3_ABLATION_v1_1"

# Raw/near-raw first-sighting fields only. Decision/gate outputs, reach/X fields and
# curve-progress proxies are intentionally excluded. path_completed is a lifecycle
# outcome, not a profitability label.
G2_FIELDS = [
    "holder_count", "top_10_holder_rate", "creator_balance_rate", "dev_team_hold_rate",
    "fresh_wallet_rate", "new_wallet_volume", "bundler_mhr", "bundler_trader_amount_rate",
    "volume_24h", "swaps_24h", "buys_24h", "sells_24h", "total_fee", "trade_fee",
    "priority_fee", "tip_fee", "sniper_count", "top70_sniper_hold_rate",
    "suspected_insider_hold_rate", "rat_trader_amount_rate", "bot_degen_count", "rug_ratio",
    "is_wash_trading", "age_seconds", "creator_funding_age_s", "tweet_age_s",
    "has_twitter", "has_telegram", "has_website", "has_fund_from_address",
]

# Explicitly not clean reconstructed G3. This vendor annotation is secondary only.
SOURCE_G3_FIELDS = ["smart_degen_count"]
FORBIDDEN_NAME_FRAGMENTS = ["reach_", "progress", "market_cap_sol", "vault_implied"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def numericize(df: pd.DataFrame, cols: list[str]) -> list[str]:
    good: list[str] = []
    for c in cols:
        if c not in df.columns:
            continue
        s = df[c]
        x = s.astype(float) if pd.api.types.is_bool_dtype(s) else pd.to_numeric(s, errors="coerce")
        x = x.replace([np.inf, -np.inf], np.nan)
        if int(x.notna().sum()) < max(100, len(df) // 200) or int(x.nunique(dropna=True)) <= 1:
            continue
        df[c] = x
        good.append(c)
    return good


def evaluate(train: pd.DataFrame, test: pd.DataFrame, features: list[str], target: str) -> dict:
    if not features:
        return {"status": "NO_USABLE_FEATURES", "n_features": 0}
    tr = train[train[target].notna()].copy()
    te = test[test[target].notna()].copy()
    ytr, yte = tr[target].astype(int), te[target].astype(int)
    if len(tr) < 500 or len(te) < 500 or ytr.nunique() < 2 or yte.nunique() < 2:
        return {
            "status": "INSUFFICIENT", "n_features": len(features), "n_train": int(len(tr)),
            "n_test": int(len(te)), "train_positives": int(ytr.sum()), "test_positives": int(yte.sum()),
        }
    pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", RobustScaler(with_centering=False)),
        ("model", LogisticRegression(max_iter=2500, class_weight="balanced", C=0.5, solver="liblinear")),
    ])
    pipe.fit(tr[features], ytr)
    p = pipe.predict_proba(te[features])[:, 1]
    y = yte.to_numpy()
    out = {
        "status": "OK", "n_features": len(features), "features": features,
        "n_train": int(len(tr)), "n_test": int(len(te)), "train_positives": int(ytr.sum()),
        "test_positives": int(y.sum()), "test_base_rate": float(y.mean()),
        "average_precision": float(average_precision_score(y, p)),
        "roc_auc": float(roc_auc_score(y, p)),
    }
    order = np.argsort(-p)
    for frac in (0.01, 0.05, 0.10, 0.20):
        k = max(1, int(len(y) * frac))
        idx = order[:k]
        precision = float(y[idx].mean())
        recall = float(y[idx].sum() / max(y.sum(), 1))
        out[f"top_{int(frac*100)}pct_precision"] = precision
        out[f"top_{int(frac*100)}pct_lift"] = precision / max(float(y.mean()), 1e-12)
        out[f"top_{int(frac*100)}pct_recall"] = recall
    return out


def timing_audit(features: pd.DataFrame) -> dict:
    out: dict = {}
    if "reach_derivable_at_decision" in features.columns:
        s = features["reach_derivable_at_decision"].fillna(False).astype(bool)
        out["reach_derivable_at_decision_true"] = int(s.sum())
        out["reach_derivable_at_decision_false_or_missing"] = int((~s).sum())
    if "age_seconds" in features.columns:
        a = pd.to_numeric(features["age_seconds"], errors="coerce").replace([np.inf, -np.inf], np.nan)
        out["negative_age_rows"] = int((a < 0).sum())
        out["min_age_seconds"] = float(a.min()) if a.notna().any() else None
    if {"tau__reach", "tau__reach_read"}.issubset(features.columns):
        tau = pd.to_numeric(features["tau__reach"], errors="coerce")
        read = pd.to_numeric(features["tau__reach_read"], errors="coerce")
        lag_all = (read - tau).dropna()
        finite = lag_all[np.isfinite(lag_all.to_numpy())]
        out["reach_read_lag_ms"] = {
            "n_all_non_null": int(len(lag_all)),
            "n_finite": int(len(finite)),
            "non_finite_count": int(len(lag_all) - len(finite)),
            "min": float(finite.min()) if len(finite) else None,
            "median": float(finite.median()) if len(finite) else None,
            "p95": float(finite.quantile(0.95)) if len(finite) else None,
            "max": float(finite.max()) if len(finite) else None,
            "negative_count": int((finite < 0).sum()) if len(finite) else 0,
        }
    out["forbidden_columns_present_but_excluded"] = sorted([
        c for c in features.columns if any(fragment in c.lower() for fragment in FORBIDDEN_NAME_FRAGMENTS)
    ])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    data_dir, out_dir = Path(args.data_dir), Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    required = [data_dir / "features.parquet", data_dir / "labels.parquet", data_dir / "split.json"]
    for p in required:
        if not p.exists():
            raise FileNotFoundError(p)

    features = pd.read_parquet(required[0])
    labels = pd.read_parquet(required[1])
    split = json.loads(required[2].read_text())
    if "mint" not in features or "mint" not in labels or "path_completed" not in labels:
        raise RuntimeError("Expected mint/path_completed schema missing")

    if "decision_ms" in features.columns:
        features = features.sort_values(["decision_ms", "mint"]).drop_duplicates("mint", keep="first")
    else:
        features = features.drop_duplicates("mint", keep="first")
    panel = features.merge(labels[["mint", "path_completed"]], on="mint", how="inner", validate="one_to_one")
    panel["path_completed"] = panel["path_completed"].astype(float)

    in_sample, out_sample = set(split.get("in_sample", [])), set(split.get("out_of_sample", []))
    if not in_sample or not out_sample:
        raise RuntimeError("split.json missing in_sample/out_of_sample mint lists")

    g2 = numericize(panel, G2_FIELDS)
    sg3 = numericize(panel, SOURCE_G3_FIELDS)
    train, test = panel[panel["mint"].isin(in_sample)].copy(), panel[panel["mint"].isin(out_sample)].copy()
    arms = {
        "G2_ONLY": evaluate(train, test, g2, "path_completed"),
        "SOURCE_CAPTURED_G3_ONLY": evaluate(train, test, sg3, "path_completed"),
        "G2_PLUS_SOURCE_CAPTURED_G3": evaluate(train, test, list(dict.fromkeys(g2 + sg3)), "path_completed"),
    }

    result = {
        "experiment": EXPERIMENT,
        "source": "Tr4m0ryp/trenches-pumpfun-forward-2026-08",
        "source_license": "PolyForm-Noncommercial-1.0.0 for compilation/derived columns; public-ledger facts remain distinct",
        "outcome_semantics": {"path_completed": "chain-reading lifecycle completion label; NOT sellable return, NOT 5x/10x alpha"},
        "rows": {"features": int(len(features)), "labels": int(len(labels)), "panel": int(len(panel)), "train": int(len(train)), "test": int(len(test))},
        "timing_audit": timing_audit(features),
        "g2_features_used": g2,
        "source_captured_g3_features_used": sg3,
        "arms": arms,
        "interpretation_rules": [
            "This is an independent lifecycle/G2 replication, not the preregistered clean-G3 economic-return test.",
            "smart_degen_count is a source-captured annotation, not reconstructed AS-OF wallet quality.",
            "Reach/X fields are excluded because the release documents that they resolve after first-sighting decision time.",
            "Curve-progress and market-cap/vault proxies that mechanically encode lifecycle progress are excluded.",
            "Any incremental smart-degen result is HYPOTHESIS_ONLY until reproduced with actual current-token buyers, matured prior wallet outcomes and entity adjustment.",
            "No result changes BUY_NOW or live thresholds."
        ],
        "provenance": {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in required},
    }
    (out_dir / "trenches_point_in_time_ablation_v1.json").write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))

    def fmt(x):
        return "-" if x is None else f"{x:.4f}" if isinstance(x, float) else str(x)
    lines = [
        "# Trenches point-in-time ablation v1.1", "",
        "Outcome: **path_completed (lifecycle only, not profitability)**", "",
        f"Panel rows: **{len(panel):,}** | train: **{len(train):,}** | test: **{len(test):,}**", "",
        "| Arm | AP | ROC-AUC | Top 5% precision | Top 5% lift | Top 5% recall |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, r in arms.items():
        if r.get("status") != "OK":
            lines.append(f"| {name} | {r.get('status')} | - | - | - | - |")
        else:
            lines.append(f"| {name} | {fmt(r.get('average_precision'))} | {fmt(r.get('roc_auc'))} | {fmt(r.get('top_5pct_precision'))} | {fmt(r.get('top_5pct_lift'))} | {fmt(r.get('top_5pct_recall'))} |")
    lines += ["", "## Guardrail", "", "A source-captured smart-degen delta cannot promote G3. Only a clean AS-OF, entity-adjusted economic-return experiment can do that."]
    (out_dir / "trenches_point_in_time_ablation_v1.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
