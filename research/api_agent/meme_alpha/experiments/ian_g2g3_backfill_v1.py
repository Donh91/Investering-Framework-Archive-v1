from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
from collections import defaultdict, deque
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

SOURCE_COMMIT = "7070d00e1e4492f8604d988549d91785cc5f43f7"

G2_CANDIDATES = [
    "time_since_launch_sec", "market_cap_usd", "liquidity_usd", "holder_count",
    "top10_holder_pct", "dev_remaining_pct", "rat_position_pct", "new_wallet_count",
    "unique_buyers", "unique_sellers", "buy_usd_1h", "sell_usd_1h", "net_flow_usd",
    "trade_buy_sell_ratio", "flipper_ratio", "large_buy_streak", "seller_loss_ratio",
    "bundler_ratio", "top_holder_ratio", "insider_cluster_size", "insider_holding_ratio",
    "insider_net_usd", "buy_early", "buy_late", "buy_total", "buy_last10", "sell_late",
    "n_early", "n_late", "buyers_early", "buyers_late",
]

G3_FEATURES = [
    "asof_wallets_seen", "asof_qualified_wallets", "asof_mean_hit2x", "asof_max_hit2x",
    "asof_mean_prior_n", "asof_weighted_hit2x", "asof_known_funder_wallets",
    "asof_distinct_known_funders", "asof_max_known_funder_group",
    "asof_common_funder_fraction", "asof_independence_adjusted_qualified",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def to_epoch_seconds(s: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(s):
        return (s.astype("int64") // 1_000_000_000).astype("int64")
    x = pd.to_numeric(s, errors="coerce")
    med = x.dropna().median() if x.notna().any() else 0
    if med > 1e14:
        x = x / 1_000_000
    elif med > 1e11:
        x = x / 1_000
    return x.round().astype("Int64")


def canonical_tokens(tokens_path: Path) -> pd.DataFrame:
    df = pd.read_parquet(tokens_path)
    required = {"token_address", "captured_at"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"tokens.parquet missing required columns: {sorted(missing)}")
    df["captured_at_s"] = to_epoch_seconds(df["captured_at"])
    df = df[df["captured_at_s"].notna()].copy()
    df["captured_at_s"] = df["captured_at_s"].astype("int64")
    df = df.sort_values(["captured_at_s", "token_address"]).drop_duplicates("token_address", keep="first")
    for col in ["max_return_24h", "max_return_3d"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    primary = "max_return_3d" if "max_return_3d" in df.columns else "max_return_24h"
    if primary not in df.columns:
        raise RuntimeError("No max_return_3d/max_return_24h label found")
    df["label_return_primary"] = df[primary]
    if "max_return_24h" in df:
        df["label_2x24"] = (df["max_return_24h"] >= 2.0).astype(float)
        df.loc[df["max_return_24h"].isna(), "label_2x24"] = np.nan
    else:
        df["label_2x24"] = np.nan
    for mult in [2, 5, 10, 25, 50]:
        df[f"label_{mult}x"] = (df["label_return_primary"] >= float(mult)).astype(float)
        df.loc[df["label_return_primary"].isna(), f"label_{mult}x"] = np.nan
    return df.reset_index(drop=True)


def load_early_buyers(data_dir: Path, canon: pd.DataFrame) -> dict[str, list[str]]:
    con = duckdb.connect()
    con.register("canon", canon[["token_address", "captured_at_s"]])
    trade_glob = str(data_dir / "trades-*.parquet")
    q = f"""
    SELECT DISTINCT t.token_address, t.wallet
    FROM read_parquet('{trade_glob}') t
    JOIN canon c USING(token_address)
    WHERE lower(t.side)='buy'
      AND t.wallet IS NOT NULL
      AND length(t.wallet) >= 20
      AND CASE
            WHEN try_cast(t.ts AS BIGINT) > 100000000000 THEN CAST(try_cast(t.ts AS BIGINT)/1000 AS BIGINT)
            ELSE try_cast(t.ts AS BIGINT)
          END <= c.captured_at_s
    """
    buyers = con.execute(q).df()
    out: dict[str, list[str]] = defaultdict(list)
    for tok, wallet in zip(buyers["token_address"], buyers["wallet"]):
        out[str(tok)].append(str(wallet))
    return out


def load_funding(data_dir: Path) -> dict[str, tuple[list[int], list[str]]]:
    path = data_dir / "wallet_funding.parquet"
    if not path.exists():
        return {}
    df = pd.read_parquet(path)
    if not {"wallet", "funder", "ts"}.issubset(df.columns):
        return {}
    df = df.dropna(subset=["wallet", "funder", "ts"]).copy()
    df["ts_s"] = to_epoch_seconds(df["ts"])
    df = df[df["ts_s"].notna()].sort_values(["wallet", "ts_s"])
    out: dict[str, tuple[list[int], list[str]]] = {}
    for wallet, g in df.groupby("wallet", sort=False):
        out[str(wallet)] = (g["ts_s"].astype(int).tolist(), g["funder"].astype(str).tolist())
    return out


def funder_asof(funding: dict[str, tuple[list[int], list[str]]], wallet: str, cutoff: int) -> str | None:
    item = funding.get(wallet)
    if not item:
        return None
    times, funders = item
    i = bisect.bisect_right(times, cutoff) - 1
    return funders[i] if i >= 0 else None


def build_asof_wallet_features(canon: pd.DataFrame, buyers_by_token: dict[str, list[str]], funding: dict[str, tuple[list[int], list[str]]]) -> pd.DataFrame:
    # Historical wallet quality uses only 24h outcomes that had matured before the current candidate.
    stats: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0])  # n, 2x wins
    pending: deque[tuple[int, list[str], float]] = deque()
    rows: list[dict] = []

    ordered = canon.sort_values("captured_at_s")
    for r in ordered.itertuples(index=False):
        t = int(r.captured_at_s)
        while pending and pending[0][0] <= t:
            _, ws, outcome = pending.popleft()
            if not math.isnan(outcome):
                for w in ws:
                    s = stats[w]
                    s[0] += 1.0
                    s[1] += outcome

        token = str(r.token_address)
        wallets = list(dict.fromkeys(buyers_by_token.get(token, [])))
        hist = []
        qualified = []
        funder_groups: dict[str, int] = defaultdict(int)
        known_funder_wallets = 0
        for w in wallets:
            n, wins = stats.get(w, [0.0, 0.0])
            if n > 0:
                hit = wins / n
                hist.append((w, n, hit))
            if n >= 3:
                qualified.append((w, n, wins / n))
                f = funder_asof(funding, w, t)
                if f:
                    known_funder_wallets += 1
                    funder_groups[f] += 1

        qn = len(qualified)
        if qn:
            q_hits = np.array([x[2] for x in qualified], dtype=float)
            q_ns = np.array([x[1] for x in qualified], dtype=float)
            weighted = float(np.average(q_hits, weights=np.maximum(q_ns, 1)))
        else:
            q_hits = np.array([], dtype=float)
            q_ns = np.array([], dtype=float)
            weighted = 0.0
        duplicate_known = sum(max(v - 1, 0) for v in funder_groups.values())
        rows.append({
            "token_address": token,
            "asof_wallets_seen": len(hist),
            "asof_qualified_wallets": qn,
            "asof_mean_hit2x": float(q_hits.mean()) if qn else 0.0,
            "asof_max_hit2x": float(q_hits.max()) if qn else 0.0,
            "asof_mean_prior_n": float(q_ns.mean()) if qn else 0.0,
            "asof_weighted_hit2x": weighted,
            "asof_known_funder_wallets": known_funder_wallets,
            "asof_distinct_known_funders": len(funder_groups),
            "asof_max_known_funder_group": max(funder_groups.values()) if funder_groups else 0,
            "asof_common_funder_fraction": (duplicate_known / qn) if qn else 0.0,
            "asof_independence_adjusted_qualified": max(qn - duplicate_known, 0),
        })

        outcome = float(r.label_2x24) if not pd.isna(r.label_2x24) else float("nan")
        pending.append((t + 24 * 3600, wallets, outcome))

    return pd.DataFrame(rows)


def clean_feature_matrix(df: pd.DataFrame, cols: list[str]) -> list[str]:
    good = []
    for c in cols:
        if c not in df.columns:
            continue
        x = pd.to_numeric(df[c], errors="coerce")
        if x.notna().sum() < max(100, len(df) // 100):
            continue
        if x.nunique(dropna=True) <= 1:
            continue
        df[c] = x.replace([np.inf, -np.inf], np.nan)
        good.append(c)
    return good


def evaluate_arm(df: pd.DataFrame, features: list[str], target: str, train_end: int, val_end: int) -> dict:
    d = df[df[target].notna()].copy()
    tr = d[d["captured_at_s"] <= train_end]
    va = d[(d["captured_at_s"] > train_end) & (d["captured_at_s"] <= val_end)]
    te = d[d["captured_at_s"] > val_end]
    if len(tr) < 200 or te[target].nunique() < 2 or tr[target].nunique() < 2:
        return {"status": "INSUFFICIENT", "n_train": len(tr), "n_val": len(va), "n_test": len(te)}
    pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", RobustScaler(with_centering=False)),
        ("model", LogisticRegression(max_iter=2000, class_weight="balanced", C=0.5, solver="liblinear")),
    ])
    pipe.fit(tr[features], tr[target].astype(int))
    p = pipe.predict_proba(te[features])[:, 1]
    y = te[target].astype(int).to_numpy()
    out = {
        "status": "OK", "n_train": len(tr), "n_val": len(va), "n_test": len(te),
        "test_base_rate": float(y.mean()),
        "test_average_precision": float(average_precision_score(y, p)),
        "test_roc_auc": float(roc_auc_score(y, p)),
    }
    order = np.argsort(-p)
    for frac in [0.01, 0.05, 0.10, 0.20]:
        k = max(1, int(len(y) * frac))
        idx = order[:k]
        precision = float(y[idx].mean())
        recall = float(y[idx].sum() / max(y.sum(), 1))
        out[f"top_{int(frac*100)}pct_precision"] = precision
        out[f"top_{int(frac*100)}pct_lift"] = precision / max(float(y.mean()), 1e-12)
        out[f"top_{int(frac*100)}pct_recall"] = recall
    return out


def simple_feature_slices(df: pd.DataFrame) -> dict:
    out = {}
    for name in ["asof_qualified_wallets", "asof_independence_adjusted_qualified", "asof_common_funder_fraction"]:
        if name not in df:
            continue
        x = pd.to_numeric(df[name], errors="coerce").fillna(0)
        bins = []
        if "fraction" in name:
            masks = [("0", x == 0), ("0_to_0.5", (x > 0) & (x < 0.5)), ("ge_0.5", x >= 0.5)]
        else:
            masks = [("0", x == 0), ("1_2", x.between(1, 2)), ("3_4", x.between(3, 4)), ("5_plus", x >= 5)]
        for label, m in masks:
            sub = df[m]
            bins.append({
                "bucket": label,
                "n": int(len(sub)),
                "rate_2x": float(sub["label_2x"].mean()) if len(sub) else None,
                "rate_5x": float(sub["label_5x"].mean()) if len(sub) else None,
                "rate_10x": float(sub["label_10x"].mean()) if len(sub) else None,
                "rate_25x": float(sub["label_25x"].mean()) if len(sub) else None,
                "rate_50x": float(sub["label_50x"].mean()) if len(sub) else None,
            })
        out[name] = bins
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    required_files = [data_dir / "tokens.parquet"] + [data_dir / f"trades-{i:03d}.parquet" for i in range(4)]
    missing = [str(p) for p in required_files if not p.exists()]
    if missing:
        raise RuntimeError(f"Missing required files: {missing}")

    provenance = {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in required_files}
    if (data_dir / "wallet_funding.parquet").exists():
        p = data_dir / "wallet_funding.parquet"
        provenance[p.name] = {"bytes": p.stat().st_size, "sha256": sha256(p)}

    canon = canonical_tokens(data_dir / "tokens.parquet")
    buyers = load_early_buyers(data_dir, canon)
    funding = load_funding(data_dir)
    g3 = build_asof_wallet_features(canon, buyers, funding)
    df = canon.merge(g3, on="token_address", how="left")

    g2 = clean_feature_matrix(df, G2_CANDIDATES)
    g3cols = clean_feature_matrix(df, G3_FEATURES)
    # Independence/funder controls are still G3-derived, but separated to quantify their incremental effect.
    g3_core = [c for c in g3cols if c not in {"asof_known_funder_wallets", "asof_distinct_known_funders", "asof_max_known_funder_group", "asof_common_funder_fraction", "asof_independence_adjusted_qualified"}]
    funder_cols = [c for c in g3cols if c not in g3_core]

    q60, q80 = df["captured_at_s"].quantile([0.60, 0.80]).astype(int).tolist()
    arms = {
        "G2_ONLY": g2,
        "G3_ASOF_ONLY": g3_core,
        "G2_PLUS_G3": g2 + g3_core,
        "G2_PLUS_G3_PLUS_FUNDER": g2 + g3_core + funder_cols,
    }
    targets = ["label_2x", "label_5x", "label_10x", "label_25x", "label_50x"]
    results = {}
    for target in targets:
        results[target] = {}
        for arm, features in arms.items():
            results[target][arm] = evaluate_arm(df, features, target, q60, q80)

    report = {
        "experiment": "IAN05012_G2_G3_POINT_IN_TIME_BACKFILL_v1",
        "source_commit": SOURCE_COMMIT,
        "canonical_tokens": int(len(df)),
        "time_min": int(df["captured_at_s"].min()),
        "time_max": int(df["captured_at_s"].max()),
        "split_epoch": {"train_end": q60, "validation_end": q80},
        "g2_features_used": g2,
        "g3_asof_features_used": g3_core,
        "funder_features_used": funder_cols,
        "label_base_rates": {t: float(df[t].mean()) for t in targets},
        "buyer_graph": {
            "tokens_with_pre_capture_buyers": int(sum(bool(v) for v in buyers.values())),
            "unique_wallets": int(len({w for ws in buyers.values() for w in ws})),
            "wallet_funding_wallets_with_history": int(len(funding)),
        },
        "results": results,
        "descriptive_wallet_slices": simple_feature_slices(df),
        "provenance": provenance,
        "limitations": [
            "Source selection is graduated/trending biased and is not the full Pump.fun launch denominator.",
            "Primary tail labels use source forward max-return fields and are not independently proven realizable exits.",
            "AS-OF wallet quality is deliberately reconstructed from prior matured 24h 2x outcomes only; source current wallet labels are excluded from the primary G3 arm.",
            "Funding adjustment only uses funding edges timestamped before each candidate cutoff; missing funding remains unknown.",
            "Logistic regression is a deliberately simple common model for arm comparison, not a production predictor.",
            "Any apparent edge requires independent denominator replication and prospective shadow validation before promotion."
        ],
    }
    (out_dir / "ian_g2g3_results_v1.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Ian05012 G2/G3 point-in-time backfill v1",
        "",
        f"Source commit: `{SOURCE_COMMIT}`",
        f"Canonical earliest token snapshots: **{len(df):,}**",
        f"Pre-capture buyer wallets: **{report['buyer_graph']['unique_wallets']:,}**",
        f"Wallets with timestamped funding history: **{len(funding):,}**",
        "",
        "## Chronological holdout results",
        "",
        "Metrics below are on the final 20% chronological holdout. AP = average precision. Lift = precision in top-scored 5% divided by holdout base rate.",
        "",
        "| Outcome | Arm | Base | AP | ROC-AUC | Top 5% precision | Top 5% lift | Top 5% recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for target in targets:
        for arm in arms:
            r = results[target][arm]
            if r.get("status") != "OK":
                lines.append(f"| {target} | {arm} | - | insufficient | - | - | - | - |")
                continue
            lines.append(
                f"| {target} | {arm} | {r['test_base_rate']:.4f} | {r['test_average_precision']:.4f} | "
                f"{r['test_roc_auc']:.4f} | {r['top_5pct_precision']:.4f} | {r['top_5pct_lift']:.2f}x | {r['top_5pct_recall']:.4f} |"
            )
    lines += [
        "",
        "## Interpretation contract",
        "",
        "- G3 is incremental only if G2+G3 improves chronological tail metrics over G2 alone, not merely in-sample fit.",
        "- Funder/entity adjustment is useful only if G2+G3+FUNDER improves or stabilizes holdout performance and reduces false convergence.",
        "- 25x/50x results are treated as sparse-tail evidence and require independent replication.",
        "- No result from this run changes BUY_NOW or production thresholds.",
        "",
        "## Source limitations",
        "",
    ] + [f"- {x}" for x in report["limitations"]]
    (out_dir / "ian_g2g3_report_v1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print((out_dir / "ian_g2g3_report_v1.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
