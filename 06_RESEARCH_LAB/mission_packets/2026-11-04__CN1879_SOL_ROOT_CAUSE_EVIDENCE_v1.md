# One-shot Sol API source packet · CN #1879 · 2026-11-04
**Read-only research. PR HEAD lock: `291e17762f512ad3b1b3e091acd93bdb2e1a3c77`. Original forecast week 2026-W45 remains immutable.**
Reference root-cause comment: https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1879#issuecomment-6641913423

## Claims to ATTACK, not assume
A. Current `_source_gate` may structurally return `envelope_quote_independently_verified=False` even on sound source data, and initial 7/7 may consequently be unconditionally quarantined. Attempt a counterexample. Distinguish a bug in software reachability from safe source abstention.
B. The existing W44 168h source's BTCUSDT/ETHUSDT "spot_flow_readback" records are volume/quote evidence, NOT automatically a proof of OHLC candle and model's numeric forecast unit. Identify the *first actually missing byte-to-byte link*, without demanding market proof of future LLM predictions.
C. Original W45 model made a genuine semantic decision to abstain on 0/7. That is separate from the code gate. Determine most informative minimal no-paid experiment before another model purchase.
D. A weekly and three-window BTC range cannot be converted into authentic seven daily expected closes by interpolation; W45 must remain 0/7. W46 is the first prospective product test, not permission to backfill.

## Genuine public archived W44 and original W45 facts, not test outcomes to use for training
`03_DAILY_CAPTURE_LOGS/weekly/2026/W44.json`, selected fields from original public artifact:
```json
{
  "iso_year": 2026,
  "iso_week": 44,
  "readiness": "READY",
  "generated_at_utc": "2026-11-02T08:12:57Z",
  "hourly_gap_diagnostics": {
    "expected_hours": 168,
    "max_contiguous_gap_hours": 0,
    "missing_hour_count": 0,
    "missing_hours_utc": [],
    "observed_hours": 168,
    "per_field_completeness": {
      "btc_close": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "btc_long_short_ratio": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "btc_open_interest": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "btc_quote_volume": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "btc_taker_buy_quote_share": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "btc_trade_count": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "eth_close": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "eth_long_short_ratio": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "eth_open_interest": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "eth_quote_volume": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "eth_taker_buy_quote_share": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "eth_trade_count": {
        "complete_hours": 168,
        "coverage_pct": 100
      },
      "ethbtc_close": {
        "complete_hours": 168,
        "coverage_pct": 100
      }
    }
  },
  "spot_flow_readback": {
    "BTC": {
      "contract": "WEEKLY_SPOT_FLOW_READBACK_v1",
      "market_interpretation": false,
      "net_aggressive_quote_flow_sum": 519532509.69517994,
      "observed_hours": 168,
      "quote_unit": "USDT",
      "quote_volume_sum": 8141798299.50194,
      "semantics": "RETAINED_SPOT_EXCHANGE_BARS_NOT_MARKET_WIDE_CVD_OR_BUY_CONFIRMATION",
      "source_rows_sha256": "bf0d8c6c0c19b741b88959ecae56461e8e0a6b5b82b92e2ddf5be232c09e38b6",
      "status": "COMPLETE_FOR_OBSERVED_ROWS",
      "symbol": "BTCUSDT",
      "taker_buy_quote_share_weighted": 0.5319052677666568,
      "taker_buy_quote_volume_sum": 4330665404.59869,
      "taker_sell_quote_volume_sum": 3811132894.90351,
      "valid_flow_hours": 168,
      "weekly_completeness_authority": "PARENT_HOURLY_GAP_DIAGNOSTICS"
    },
    "ETH": {
      "contract": "WEEKLY_SPOT_FLOW_READBACK_v1",
      "market_interpretation": false,
      "net_aggressive_quote_flow_sum": 174957713.41499996,
      "observed_hours": 168,
      "quote_unit": "USDT",
      "quote_volume_sum": 3667692205.91098,
      "semantics": "RETAINED_SPOT_EXCHANGE_BARS_NOT_MARKET_WIDE_CVD_OR_BUY_CONFIRMATION",
      "source_rows_sha256": "05a394960e4c14fab50f645f248c5c7c939e54723c8bec4d3810c035b8f1cb58",
      "status": "COMPLETE_FOR_OBSERVED_ROWS",
      "symbol": "ETHUSDT",
      "taker_buy_quote_share_weighted": 0.5238511990090733,
      "taker_buy_quote_volume_sum": 1921324959.6627,
      "taker_sell_quote_volume_sum": 1746367246.2477,
      "valid_flow_hours": 168,
      "weekly_completeness_authority": "PARENT_HOURLY_GAP_DIAGNOSTICS"
    }
  },
  "first_hour_utc": "2026-10-26T00:00:00Z",
  "last_hour_utc": "2026-11-01T23:00:00Z",
  "source_capture_path_count": 41
}
```

`05_CYCLE_NAVIGATOR/weekly/2026/W45/CYCLE_NAVIGATOR_FORECAST_FREEZE.json`, original immutable forecast selected fields:
```json
{
  "btc_range_low": 72000,
  "btc_range_high": 84000,
  "eth_range_low": 2000,
  "eth_range_high": 2500,
  "forecast_week": "2026-W45",
  "daily_price_path": {
    "BTC": {
      "points": [],
      "reason": "The completed-week evidence and mixed W45 base case support a weekly envelope and three UTC windows, but no defensible day-by-day expected-close sequence; assigning daily closing levels would invent target-week timing.",
      "status": "UNAVAILABLE"
    },
    "ETH": {
      "points": [],
      "reason": "Negative settled ETH flows and incomplete relative recovery support caution, but do not identify a defensible UTC daily closing-price sequence within W45.",
      "status": "UNAVAILABLE"
    },
    "contract": "CN_FROZEN_DAILY_PRICE_PATH_v1",
    "forecast_week": "2026-W45"
  }
}
```

`W45 original freeze digest`: `e933a2c8a08669a7acbe1542c24b1fddd4a5f7852131d83f2b98369834ac1be1`.
`Source collector`: public repo original, not direct provider API confirmation. Check source chain; do not claim those snippets alone prove raw-response SHA.

## Exact existing code snippets, pinned to original #1879 HEAD
### `scripts/cycle_navigator/daily_path_recovery.py` lines 96-209
Pinned original PR head: `291e17762f512ad3b1b3e091acd93bdb2e1a3c77`

```python
        raise ValueError("SOURCE_CLOCK_UNZONED")
    return timestamp.astimezone(timezone.utc)


def _source_gate(context: Mapping[str, Any], year: int, week: int, issued: datetime) -> tuple[dict[str, Any], str]:
    completed = context.get("completed_week_hourly_capture") or {}
    mm = context.get("master_monday_machine_package") or {}
    pointer = context.get("master_monday_pointer") or {}
    if not isinstance(completed, dict) or not isinstance(mm, dict) or not isinstance(pointer, dict):
        return {}, "SOURCE_CONTRACT_MISSING"
    cutoff = datetime.combine(date.fromisocalendar(year, week, 1), datetime.min.time(), timezone.utc)
    # Seven forward daily CLOSE points can only be originally issued while
    # the FIRST UTC day's settlement remains in the future.
    if issued >= cutoff + timedelta(days=1) or issued < cutoff:
        return {}, "SEVEN_DAY_PROSPECTIVE_WINDOW_CLOSED_OR_NOT_STARTED"
    completed_monday = date.fromisocalendar(year, week, 1) - timedelta(days=7)
    completed_week = completed_monday.isocalendar()
    if (completed.get("iso_year"), completed.get("iso_week")) != (completed_week.year, completed_week.week):
        return {}, "COMPLETED_WEEK_IDENTITY_MISMATCH"
    if (pointer.get("iso_year"), pointer.get("iso_week")) != (completed_week.year, completed_week.week):
        return {}, "MASTER_MONDAY_IDENTITY_MISMATCH"
    if mm.get("api_status") != "success" or pointer.get("status") != "READY":
        return {}, "MASTER_MONDAY_NOT_READY"
    diagnostics = completed.get("hourly_gap_diagnostics") or {}
    if completed.get("readiness") != "READY" or diagnostics.get("observed_hours") != 168 or diagnostics.get("missing_hour_count") != 0:
        return {}, "COMPLETED_SOURCE_INCOMPLETE"
    if not completed.get("source_capture_paths"):
        return {}, "COMPLETED_SOURCE_LINEAGE_MISSING"
    sequence = completed.get("hourly_sequence") or {}
    if not isinstance(sequence, dict):
        return {}, "COMPLETED_SEQUENCE_MISSING"
    try:
        completed_first = _clock(sequence.get("first_hour_utc"))
        completed_last = _clock(sequence.get("last_hour_utc"))
        cutoff = datetime.combine(date.fromisocalendar(year, week, 1), datetime.min.time(), timezone.utc)
        start = datetime.combine(completed_monday, datetime.min.time(), timezone.utc)
        if completed_first != start or completed_last != cutoff - timedelta(hours=1):
            return {}, "COMPLETED_SOURCE_WINDOW_INVALID"
        if any(_clock(v) > issued for v in (completed.get("generated_at_utc"), mm.get("created_at_utc"))):
            return {}, "SOURCE_CLOCK_AFTER_ISSUANCE"
    except (TypeError, ValueError, OverflowError):
        return {}, "SOURCE_CLOCK_INVALID"
    quotes = {}
    spot = sequence.get("spot_flow_readback") or {}
    for asset in ("BTC", "ETH"):
        source_row = spot.get(asset) or {}
        quote = source_row.get("quote_unit")
        if quote not in ("USD", "USDT"):
            quotes[asset] = None
        else:
            quotes[asset] = quote
    if not any(quotes.values()):
        return {}, "SOURCE_QUOTE_UNVERIFIED"
    # The spot-flow quote cannot certify the separate LLM weekly envelope.
    # Only explicit, source-bound matching quote metadata can do so.
    envelope_quote = context.get("weekly_envelope_quote")
    if not isinstance(envelope_quote, dict):
        return {}, "WEEKLY_ENVELOPE_QUOTE_UNBOUND"
    for asset in ("BTC", "ETH"):
        if envelope_quote.get(asset) not in ("USD", "USDT"):
            quotes[asset] = None
        elif quotes[asset] != envelope_quote[asset]:
            quotes[asset] = None
    if not any(quotes.values()):
        return {}, "WEEKLY_ENVELOPE_QUOTE_MISMATCH"
    return {"quote": quotes, "completed_week": f"{completed_week.year:04d}-W{completed_week.week:02d}",
            "completed_last_utc": completed_last.isoformat(),
            "source_generated_at_utc": completed["generated_at_utc"],
            "master_monday_created_at_utc": mm["created_at_utc"],
            "quote_evidence": "MODEL_DECLARED_ENVELOPE_QUOTE_EQUALS_SPOT_QUOTE_NOT_INDEPENDENT",
            "envelope_quote_independently_verified": False,
            "source_admitted_for_scientific_scoring": False}, "ELIGIBLE"


def reject_unverified_initial_daily_quotes(value: dict[str, Any],
                                          context: Mapping[str, Any], *,
                                          year: int | None = None,
                                          week: int | None = None,
                                          issued_at: datetime | None = None) -> dict[str, Any]:
    """An initial 7/7 model answer cannot bypass original price-quote parity.

    Mutates only the still-unfrozen in-memory publication candidate and never
    changes canonical scoring or a previously frozen forecast.
    """
    freeze = value["forecast_freeze"]
    path = freeze["daily_price_path"]
    quotes = freeze.get("price_quote") or {}
    spot = ((context.get("completed_week_hourly_capture") or {})
            .get("hourly_sequence") or {}).get("spot_flow_readback") or {}
    # Production checks the post-model issuance clock and full source gate,
    # including initially valid 7/7 paths. Missing independent source evidence
    # must never be upgraded from equal model-declared currency labels.
    qualified = None
    gate = "NOT_REQUESTED_FOR_LEGACY_TEST"
    if year is not None or week is not None or issued_at is not None:
        if year is None or week is None or issued_at is None:
            raise ValueError("INITIAL_SOURCE_GATE_ARGUMENTS_INCOMPLETE")
        qualified, gate = _source_gate(context, year, week, issued_at)
    changes = {}
    for asset in ("BTC", "ETH"):
        item = path.get(asset)
        if not isinstance(item, dict) or item.get("status") != "PUBLISHED":
            continue
        actual = (spot.get(asset) or {}).get("quote_unit")
        claimed = quotes.get(asset)
        if (actual not in ("USD", "USDT") or claimed != actual or
                (qualified is None or gate != "ELIGIBLE"
                 or qualified.get("envelope_quote_independently_verified") is not True
                 or qualified.get("quote", {}).get(asset) != actual)):
            changes[asset] = {"status": "UNAVAILABLE", "points": [],
                              "reason": "Initial daily path source, clock or quote unverified before freeze."}
    if changes:
        value["forecast_freeze"] = {**freeze,
            "daily_price_path": {**path, **changes}}
```

### `scripts/cycle_navigator/daily_path_recovery.py` lines 310-369
Pinned original PR head: `291e17762f512ad3b1b3e091acd93bdb2e1a3c77`

```python
                       request=None, budget_check=None,
                       cost_receipt_path: Path | None = None,
                       primary_unaccounted_cost_usd: float = 0.0) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return original value with only independently validated UNAVAILABLE assets repaired."""
    freeze = value["forecast_freeze"]
    original = freeze["daily_price_path"]
    validate_daily_path(original, freeze, year, week)
    if issued_at.tzinfo is None:
        raise ValueError("ISSUE_CLOCK_UNZONED")
    issued_at = issued_at.astimezone(timezone.utc)
    receipt: dict[str, Any] = {
        "contract": "CN_DAILY_PATH_SEMANTIC_RECOVERY_v1",
        "forecast_week": f"{year:04d}-W{week:02d}",
        "issue_number": value.get("issue_number"),
        "issued_at_utc": issued_at.isoformat().replace("+00:00", "Z"),
        "initial": {a: original[a]["status"] for a in ("BTC", "ETH")},
        "attempt_count": 0, "model": model, "status": "NOT_REQUIRED",
        "original_daily_path_sha256": _sha(original),
        "original_weekly_envelope_sha256": _sha({a: [freeze.get(a.lower()+"_range_low"), freeze.get(a.lower()+"_range_high")] for a in ("BTC", "ETH")}),
        "source_context_sha256": _sha(context), "source_derived_from": "FINAL_MASTER_MONDAY_AND_COMPLETED_WEEK_ONLY",
        "portfolio_execution": False, "scoring_authority": False,
    }
    pending = [a for a in ("BTC", "ETH") if original[a]["status"] == "UNAVAILABLE"]
    if not pending:
        receipt["final"] = receipt["initial"].copy()
        return value, receipt
    source, gate = _source_gate(context, year, week, issued_at)
    receipt["source_gate"] = gate
    receipt["source_clock_and_quote"] = source
    if gate != "ELIGIBLE":
        receipt["status"] = "SKIPPED_SOURCE_GUARD"
        receipt["final"] = receipt["initial"].copy()
        return value, receipt
    # Guard against silently promoting an unknown or cross-quoted original price frame.
    for asset in pending:
        if not source["quote"].get(asset):
            receipt.setdefault("per_asset_reason", {})[asset] = "QUOTE_UNVERIFIED"
    eligible = [a for a in pending if source["quote"].get(a)]
    if not eligible:
        receipt["status"] = "SKIPPED_SOURCE_QUOTE"
        receipt["final"] = receipt["initial"].copy()
        return value, receipt
    # Owner policy 2026-11-02: no automatic second paid model call.
    # `request` is an injected offline test callback, never production transport.
    # A future paid exception requires separate authenticated, cross-workflow
    # durable pre-HTTP authorization, not this semantic retry lane.
    if request is None:
        receipt["status"] = "SKIPPED_PAID_RECOVERY_DISABLED"
        receipt["budget_error_code"] = "PAID_SEMANTIC_RECOVERY_NOT_AUTHORIZED"
        receipt["final"] = receipt["initial"].copy()
        return value, receipt
    if os.environ.get("CN_DAILY_RECOVERY_ENABLED", "1") != "1":
        receipt["status"] = "SKIPPED_BUDGET_OR_OPERATOR_GUARD"
        receipt["final"] = receipt["initial"].copy()
        return value, receipt
    candidate_input = {"task": "CN_SEVEN_DAY_PRE_FREEZE_RECOVERY", "forecast_week": receipt["forecast_week"],
                       "issue_number": receipt["issue_number"], "eligible_assets": eligible,
                       "immutable_original_weekly_bounds_sha256": receipt["original_weekly_envelope_sha256"],
                       "evidence": _input_excerpt(context, source, value, freeze)}
    # This is independent of model simulation: even injected requests must
```

### `scripts/cycle_navigator/build_weekly_cycle_navigator.py` lines 719-747
Pinned original PR head: `291e17762f512ad3b1b3e091acd93bdb2e1a3c77`

```python
        "previous_cycle_navigator_machine_package": prev_machine,
        "previous_score_parameter_ids": expected_score_parameter_ids(prev_machine),
        "existing_track_record": maybe_text(repo / "05_CYCLE_NAVIGATOR/track_record/CN_TRACK_RECORD_LEDGER.jsonl"),
        "completed_week_hourly_capture": weekly_capture,
        "prospective_range_bridge": load_bridge(repo, target_year=target_year, target_week=target_week, freeze_at=datetime.now(timezone.utc)),
        "range_continuity_rule": "READY 168h hourly capture makes BTC/ETH weekly and intraday ranges mandatory."
    }
    # Supply an immutable pre-model observation of the actual retained spot
    # pair/quote and weekly source bytes. This is a DATA-QUALITY HINT, not
    # independent attestation of the LLM-generated weekly price envelope.
    # The source gate must still independently qualify issuance at use.
    observed_spot = (((weekly_capture or {}).get("hourly_sequence") or {})
                     .get("spot_flow_readback") or {})
    context["pre_model_spot_quote_observation"] = {
        "contract": "CN_PREMODEL_SPOT_QUOTE_OBSERVATION_v1",
        "authority": "SOURCE_OBSERVATION_NOT_ENVELOPE_ATTESTATION",
        "weekly_capture_sha256": (sha256_bytes(weekly_capture_path.read_bytes())
                                  if isinstance(weekly_capture, dict) else None),
        "assets": {
            asset: {field: (observed_spot.get(asset) or {}).get(field)
                    for field in ("symbol", "quote_unit", "source_rows_sha256",
                                  "status", "observed_hours")}
            for asset in ("BTC", "ETH")
        },
    }
    prompt = (
        f"Generate internal Cycle Navigator machine issue #{issue} for ISO week W{target_week:02d}, but the continuing public series number for this forecast week is CN #{public_issue}. Use CN #{public_issue} in readable_markdown and x_ready_markdown headings/current-issue references. First evaluate the prior frozen machine issue #{prev_issue} against completed W{completed_week:02d}. "
        "Then freeze the new week's explicit forecasts. The X-ready version must include a precision section, an honest what-went-well/what-went-wrong section, "
        "a concise public track-record section that only uses archived/reproducible values, a current-state section, weekly BTC/ETH ranges or UNAVAILABLE, "
```

### `scripts/cycle_navigator/build_weekly_cycle_navigator.py` lines 896-944
Pinned original PR head: `291e17762f512ad3b1b3e091acd93bdb2e1a3c77`

```python

    validate_daily_range_plan(freeze.get("daily_range_plan"), freeze, target_year, target_week)
    # Quote is original model envelope metadata, independently crosschecked
    # against completed-week source quote in the recovery source gate.
    context["weekly_envelope_quote"] = freeze.get("price_quote")
    # The FIRST model answer also needs price-quote integrity. A PUBLISHED
    # asset whose original weekly quote does not match the source quote is
    # reduced to an honest UNAVAILABLE before any immutable freeze.
    value = reject_unverified_initial_daily_quotes(
        value, context, year=target_year, week=target_week,
        issued_at=datetime.now(timezone.utc))
    freeze = value["forecast_freeze"]
    # A valid semantic abstention may receive at most ONE additional bounded
    # source-qualified call, always before the original immutable week freeze.
    primary_usage = raw.get("usage") if isinstance(raw.get("usage"), dict) else {}
    try:
        primary_input = primary_usage.get("input_tokens")
        primary_output = primary_usage.get("output_tokens")
        if any(type(x) is not int or x < 0 for x in (primary_input, primary_output)):
            raise ValueError("INVALID_PRIMARY_USAGE")
        primary_unaccounted_cost = estimate_cost(args.model, primary_input, primary_output)
    except (KeyError, TypeError, ValueError):
        # Let semantic retry fail closed without blocking the valid original
        # weekly publication if provider cost is not independently priceable.
        primary_unaccounted_cost = float("nan")
    value, daily_recovery_receipt = recover_daily_path(
        value, context, year=target_year, week=target_week,
        model=args.model, issued_at=datetime.now(timezone.utc),
        primary_unaccounted_cost_usd=primary_unaccounted_cost,
        cost_receipt_path=(repo / "research/api_agent/outputs/weekly" /
                           str(target_year) / f"W{target_week:02d}" /
                           "CN_DAILY_RECOVERY_COST_RESERVATION.json"))
    # A request that starts before day-one close but finishes after it
    # cannot be frozen as a prospective seven-day forecast.
    generated_unix = int(time.time())
    value = quarantine_late_daily_issuance(
        value, year=target_year, week=target_week,
        publication_clock=datetime.fromtimestamp(generated_unix, tz=timezone.utc))
    freeze = value["forecast_freeze"]
    validate_daily_path(freeze.get("daily_price_path"), freeze, target_year, target_week)
    daily_path_issue = daily_path_issue_summary(freeze.get("daily_price_path"), freeze, target_year, target_week)
    source_manifest = {"daily_path_issuance": daily_path_issue, "daily_path_recovery": daily_recovery_receipt, "contract": "CYCLE_NAVIGATOR_SOURCE_MANIFEST_v1", "issue_number": issue, "public_issue_number": public_issue, "completed_iso_year": completed_year, "completed_iso_week": completed_week, "target_iso_year": target_year, "target_iso_week": target_week, "deterministic_range_baseline_persistence": {"forecast": range_forecast_persistence, "prior_score": prior_range_score_persistence}, "master_monday_dir": str(mm_dir.relative_to(repo)), "master_monday_files": {name: sha256_bytes((mm_dir / name).read_bytes()) for name in required}, "previous_issue_number": prev_issue or None, "previous_machine_available": prev_machine is not None, "previous_exact_text_available": prev_text is not None}
    scoring_valid_from_unix = ((generated_unix + 3599) // 3600) * 3600
    scoring_valid_from_utc = datetime.fromtimestamp(scoring_valid_from_unix, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    package = {"contract": "CYCLE_NAVIGATOR_MACHINE_PACKAGE_v1", "generated_unix": generated_unix, "public_issue_number": public_issue, "authority": "USER_FACING_DERIVED_FROM_FINAL_MASTER_MONDAY", "publication_status": "X_READY_NOT_CONFIRMED_PUBLISHED", "source_manifest_sha256": sha256_bytes(canonical_bytes(source_manifest)), **value}
    scorecard = {"contract": "CYCLE_NAVIGATOR_SCORECARD_v1", "issue_scored": prev_issue or None, "completed_iso_year": completed_year, "completed_iso_week": completed_week, **value["evaluation"]}
    pointer = {"contract": "CYCLE_NAVIGATOR_DELIVERY_POINTER_v1", "issue_number": issue, "public_issue_number": public_issue, "iso_year": target_year, "iso_week": target_week, "completed_source_year": completed_year, "completed_source_week": completed_week, "week_dir": str(target_dir.relative_to(repo)), "status": value["status"], "status_reason_codes": value["status_reason_codes"], "publication_status": package["publication_status"], "master_monday_pointer_sha256": sha256_bytes((repo / args.master_monday_pointer).read_bytes()), "machine_package_sha256": sha256_bytes(canonical_bytes(package)), "forecast_freeze_sha256": sha256_bytes(canonical_bytes(freeze))}

    (target_dir / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json").write_bytes(canonical_bytes(package))
```

### `scripts/daily_capture/build_hourly_sequence.py` lines 516-561
Pinned original PR head: `291e17762f512ad3b1b3e091acd93bdb2e1a3c77`

```python
    args = parser.parse_args()

    now = (
        datetime.fromisoformat(args.retrieval_timestamp.replace("Z", "+00:00"))
        if args.retrieval_timestamp else datetime.now(timezone.utc)
    )
    now = now.astimezone(timezone.utc)
    end = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    start = end - timedelta(hours=max(1, args.lookback_hours) - 1)
    start_ms = to_ms(start)
    end_ms = to_ms(end + timedelta(hours=1)) - 1
    args.raw_output.mkdir(parents=True, exist_ok=True)

    spot_data = {}
    oi_data = {}
    ls_data = {}
    funding_data = {}
    source_records = []
    spot_failures = 0
    derivative_failures = 0

    for symbol in SPOT_SYMBOLS:
        url = build_url(BINANCE_SPOT, {
            "symbol": symbol, "interval": "1h", "startTime": start_ms, "endTime": end_ms, "limit": 1000,
        })
        status, body, error = source_read(args.fixture_dir, f"{symbol}_spot.json", url)
        record = {"name": f"{symbol}_spot", "venue": "BINANCE_SPOT", "status": status, "url": url, "error": error}
        if body:
            path = args.raw_output / f"{symbol}_spot.json"
            path.write_bytes(body)
            record.update(bytes=len(body), sha256=sha256_bytes(body))
            try:
                spot_data[symbol] = parse_spot(body, symbol)
                record["row_count"] = len(spot_data[symbol])
            except SourceError as exc:
                record.update(status=exc.status, error=str(exc))
                spot_failures += 1
        else:
            spot_failures += 1
        source_records.append(record)

    for symbol, instrument, ccy in DERIVATIVE_SYMBOLS:
        queries = {
            "oi": (
                "/api/v5/rubik/stat/contracts/open-interest-history",
                {"instId": instrument, "period": "1H", "begin": start_ms - 3_600_000, "end": end_ms, "limit": 100},
```

### `scripts/daily_capture/build_hourly_sequence.py` lines 639-681
Pinned original PR head: `291e17762f512ad3b1b3e091acd93bdb2e1a3c77`

```python
        window_start_utc=iso_utc(start),
        window_end_utc=iso_utc(end + timedelta(hours=1)),
        requested_hours=requested_hours,
        output_receipts=output_receipts,
        source_records=source_records,
    )
    manifest = {
        "contract": "HOURLY_SEQUENCE_CAPTURE_v2_2",
        "run_id": run_id,
        "retrieved_at_utc": iso_utc(now),
        "window_start_utc": iso_utc(start),
        "window_end_utc": iso_utc(end + timedelta(hours=1)),
        "requested_hours": requested_hours,
        "spot_complete_hours": spot_complete,
        "spot_flow_complete_hours": spot_flow_complete,
        "derivatives_oi_complete_hours": oi_complete,
        "long_short_complete_hours": long_short_complete,
        "status": status,
        "spot_status": spot_status,
        "derivatives_status": derivatives_status,
        "spot_venue": "BINANCE",
        "derivatives_venue": "OKX",
        "interpolation": False,
        "forward_fill": False,
        "permanent_outputs": permanent_outputs,
        "permanent_output_receipts": output_receipts,
        "source_records": source_records,
        "directional_summary": summary,
        "directional_summary_sha256": summary["summary_sha256"],
        "authority": AUTHORITY,
    }
    run_dir = args.output_root / "runs" / now.strftime("%Y/%m/%d")
    run_dir.mkdir(parents=True, exist_ok=True)
    run_path = run_dir / f"{now:%H%M%S}_{run_id}.json"
    run_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    pointer = {
        "contract": "HOURLY_SEQUENCE_LATEST_POINTER_v2_2",
        "run_id": run_id,
        "run_path": run_path.as_posix(),
        "retrieved_at_utc": manifest["retrieved_at_utc"],
        "window_start_utc": manifest["window_start_utc"],
        "window_end_utc": manifest["window_end_utc"],
        "status": status,
```

### `scripts/daily_capture/build_weekly_calibration.py` lines 262-303
Pinned original PR head: `291e17762f512ad3b1b3e091acd93bdb2e1a3c77`

```python

def weekly_spot_flow(rows: list[dict[str, str]], prefix: str) -> dict[str, Any]:
    """Expose retained exchange-bar flow values, never market-wide CVD."""
    fields = ("quote_volume", "taker_buy_quote_volume", "taker_sell_quote_volume", "taker_buy_quote_share")
    evidence = [{"timestamp_utc": row.get("timestamp_utc"), "spot_status": row.get("spot_status"),
                 **{field: row.get(f"{prefix}_{field}") for field in fields}} for row in rows]
    valid = []
    for row in evidence:
        values = [None if isinstance(row[field], bool) else f(row[field]) for field in fields]
        if row["spot_status"] != "PASS" or any(value is None or not math.isfinite(value) for value in values):
            continue
        total, buy, sell, share = values
        if (total <= 0 or not 0 <= buy <= total or sell < 0 or not 0 <= share <= 1
                or not math.isclose(buy + sell, total, rel_tol=1e-8, abs_tol=1e-6)
                or not math.isclose(buy / total, share, rel_tol=1e-8, abs_tol=1e-8)):
            continue
        valid.append((total, buy, sell))
    try:
        stamps = [parse_utc(row["timestamp_utc"]) for row in evidence]
        identity_ok = (len(stamps) == len(set(stamps)) and stamps == sorted(stamps)
                       and len({stamp.isocalendar()[:2] for stamp in stamps}) == 1
                       and all(stamp.minute == stamp.second == stamp.microsecond == 0 for stamp in stamps))
    except (TypeError, ValueError, OverflowError):
        identity_ok = False
    complete = len(rows) > 0 and len(valid) == len(rows) and identity_ok
    total = sum(row[0] for row in valid) if complete else None
    buy = sum(row[1] for row in valid) if complete else None
    sell = sum(row[2] for row in valid) if complete else None
    return {
        "contract": "WEEKLY_SPOT_FLOW_READBACK_v1",
        "status": "COMPLETE_FOR_OBSERVED_ROWS" if complete else "UNAVAILABLE_INVALID_OR_MISSING_FLOW",
        "observed_hours": len(rows), "valid_flow_hours": len(valid),
        "source_rows_sha256": hashlib.sha256((json.dumps(evidence, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest(),
        "quote_unit": "USDT", "symbol": prefix.upper() + "USDT",
        "quote_volume_sum": total, "taker_buy_quote_volume_sum": buy,
        "taker_sell_quote_volume_sum": sell,
        "net_aggressive_quote_flow_sum": buy - sell if complete else None,
        "taker_buy_quote_share_weighted": buy / total if complete else None,
        "semantics": "RETAINED_SPOT_EXCHANGE_BARS_NOT_MARKET_WIDE_CVD_OR_BUY_CONFIRMATION",
        "weekly_completeness_authority": "PARENT_HOURLY_GAP_DIAGNOSTICS",
        "market_interpretation": False,
    }
```


## Decision output to provide
1. Minimal actual cause tree, rank by whether proven from excerpts. Is positive 7/7 *reachable* now? Show exact conditional flow.
2. One source-quote-owner proposal that uses *existing* admitted source artifacts. Define precisely what is verified and what is not.
3. Minimum production-code patch locations and <=4 deterministic positive/negative tests; no implementation, no invented tests-run.
4. Explicit distinction between historical input provenance vs future forecast quality vs prediction publication/score authority.
5. Five-line decision: PROCEED_SIMPLE_PATCH / PAUSE_MISSING_SOURCE / REJECT_HYPOTHESIS, with minimal proof needed, one original PR owner and next prospective W46 check.
6. Identify any security/data-integrity reason the simple fix could be unsafe. Do not relax source gates and do not add API/automation/paid retry.

**Source visibility limit:** Exact recent PR code snippets and archived source summary are supplied, but full raw Binance response bodies and private authenticated billing/stock evidence are NOT supplied. Mark them UNKNOWN. Do not infer actual tests from CI names. No prediction values or numeric forecast candidates.
