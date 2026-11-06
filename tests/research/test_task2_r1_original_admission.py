import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import scripts.research.task2_r1_original_admission as admission
from scripts.research.task2_r1_original_admission import build, clock_status, original


class OriginalAdmissionTests(unittest.TestCase):
    def test_illegal_clocks_and_settlement_are_not_admitted(self):
        issue = "2026-10-13T12:00:00Z"
        self.assertEqual(clock_status("2026-10-13T11:00:00Z", "2026-10-13T12:00:01Z", issue), "NOT_ADMITTED_RETRIEVED_AFTER_ISSUE")
        self.assertEqual(clock_status("2026-10-13T12:00:01Z", None, issue), "NOT_ADMITTED_OBSERVATION_AFTER_ISSUE")
        self.assertEqual(clock_status(1791849600000, None, issue, funding=True), "SETTLEMENT_IS_NOT_QUOTE_OBSERVATION")
        self.assertEqual(clock_status("2026-10-13T11:00:00Z", None, issue), "RETRIEVAL_CLOCK_UNKNOWN")

    def test_wrong_original_git_blob_fails(self):
        with self.assertRaisesRegex(ValueError, "Git blob mismatch"):
            original("098c50d36b222c4c8ffa179a5879d36a74194bc4", "04_MARKET_LEARNING/handlekompas/official/daily/2026/10/12/CMP-20261012-468da783e9d8.json", "0" * 40)

    def _run_with_tampered_frozen_census(self, modify):
        frozen = json.loads((admission.ROOT / admission.FORECAST_CENSUS).read_text())
        modify(frozen)
        with tempfile.TemporaryDirectory() as td:
            tampered_path = Path(td) / "tampered_frozen_forecast_census.json"
            tampered_path.write_text(json.dumps(frozen))
            with mock.patch.object(admission, "FORECAST_CENSUS", tampered_path):
                return build()

    def test_original_forecast_git_blob_must_match_separately_frozen_census(self):
        def modify(frozen):
            f = next(x for x in frozen["forecast_rows"]
                     if x["original_scoring_contract"] == "OFFICIAL_DAILY_COMPASS_SCORING_v3")
            f["forecast_git_blob_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "Git blob mismatch"):
            self._run_with_tampered_frozen_census(modify)

    def test_original_outcome_presence_must_agree_across_two_censuses(self):
        def modify(frozen):
            f = next(x for x in frozen["forecast_rows"]
                     if x["original_scoring_contract"] == "OFFICIAL_DAILY_COMPASS_SCORING_v3"
                     and x["outcome_12h_presence_at_pinned_commit"] == "PRESENT")
            f["outcome_12h_presence_at_pinned_commit"] = "ABSENT_AT_SNAPSHOT"
        with self.assertRaisesRegex(ValueError, "Original outcome snapshot census mismatch"):
            self._run_with_tampered_frozen_census(modify)

    def test_original_forecast_roster_cannot_be_silently_shrunk(self):
        def modify(frozen):
            f = next(x for x in frozen["forecast_rows"]
                     if x["original_scoring_contract"] == "OFFICIAL_DAILY_COMPASS_SCORING_v3")
            frozen["forecast_rows"].remove(f)
        with self.assertRaisesRegex(ValueError, "Original forecast census or attempt roster mismatch"):
            self._run_with_tampered_frozen_census(modify)

    def test_frozen_parent_commit_must_equal_raw_source_era(self):
        def modify(frozen):
            frozen["pinned_public_main_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "Original forecast census uses a different pinned Git revision"):
            self._run_with_tampered_frozen_census(modify)

    def test_original_git_object_reads_disable_local_replace_objects(self):
        with mock.patch.object(admission.subprocess, "run") as run:
            run.return_value.stdout = b"frozen"
            admission.git("show", "0123456789012345678901234567890123456789:some.json")
            self.assertEqual(run.call_args.args[0][:3], ["git", "--no-replace-objects", "show"])

    def test_info_edge_and_action_edge_have_distinct_nonpromoting_clocks(self):
        d = build()
        self.assertEqual(len(d["rows"]), 11)
        for row in d["rows"]:
            info = row["information_edge_gate"]
            action = row["investor_action_edge_gate"]
            self.assertEqual(info["status"], "NOT_ADMITTED")
            self.assertEqual(action["status"], "NOT_ADMITTED")
            self.assertFalse(info["user_delivery_required"])
            self.assertTrue(action["user_delivery_required"])
            self.assertNotIn("FIRST_USER_DELIVERY_UNVERIFIED", info["missing"])
            self.assertIn("FIRST_USER_DELIVERY_UNVERIFIED", action["missing"])
            self.assertIn("PROVIDER_FIRST_PUBLICATION_UNVERIFIED", info["missing"])
            self.assertIn("PROVIDER_FIRST_PUBLICATION_UNVERIFIED", action["missing"])
            self.assertFalse(action["portfolio_execution_authorized"])
            self.assertEqual(
                "ORIGINAL_OUTCOME_ABSENT_AT_FROZEN_SNAPSHOT" in info["missing"],
                row["original_outcome_status"] != "PRESENT",
            )
        self.assertEqual(sum(r["information_edge_gate"]["status"] == "ADMITTED" for r in d["rows"]), 0)
        self.assertEqual(sum(r["investor_action_edge_gate"]["status"] == "ADMITTED" for r in d["rows"]), 0)

    def _create_disposable_git_outcome(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "nested").mkdir()
        (root / "nested" / "outcome.json").write_text('{"status":"PRESENT"}')
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "frozen test fixture"], cwd=root, check=True)
        return root

    def test_original_missing_path_is_absent_only_after_successful_tree_traversal(self):
        root = self._create_disposable_git_outcome()
        with mock.patch.object(admission, "ROOT", root):
            self.assertEqual(admission.optional_original("HEAD", "nested/never.json"), (None, None))
            actual, blob = admission.optional_original("HEAD", "nested/outcome.json")
            self.assertEqual(actual["status"], "PRESENT")
            self.assertEqual(len(blob), 40)

    def test_missing_original_blob_is_operational_error_never_absence(self):
        root = self._create_disposable_git_outcome()
        blob = subprocess.check_output(["git", "rev-parse", "HEAD:nested/outcome.json"], cwd=root).decode().strip()
        (root / ".git" / "objects" / blob[:2] / blob[2:]).unlink()
        with mock.patch.object(admission, "ROOT", root):
            with self.assertRaises(subprocess.CalledProcessError):
                admission.optional_original("HEAD", "nested/outcome.json")

    def test_missing_original_nested_tree_is_operational_error_never_absence(self):
        root = self._create_disposable_git_outcome()
        tree = subprocess.check_output(["git", "rev-parse", "HEAD:nested"], cwd=root).decode().strip()
        (root / ".git" / "objects" / tree[:2] / tree[2:]).unlink()
        with mock.patch.object(admission, "ROOT", root):
            with self.assertRaises(subprocess.CalledProcessError):
                admission.optional_original("HEAD", "nested/outcome.json")

    def test_failed_git_tree_lookup_must_propagate_not_become_missing(self):
        with mock.patch.object(admission, "git", side_effect=subprocess.CalledProcessError(128, ["git", "ls-tree"])):
            with self.assertRaises(subprocess.CalledProcessError):
                admission.optional_original("HEAD", "nested/outcome.json")

    def test_checkout_head_is_not_labeled_as_verified_main(self):
        rows = build()
        self.assertIn("generated_from_checkout_head_sha", rows)
        self.assertNotIn("generated_from_main_sha", rows)
        self.assertEqual(rows["checkout_ref_semantics"], "MAY_BE_PR_TEST_MERGE_NOT_VERIFIED_CURRENT_MAIN")
        self.assertTrue(all(
            x["checkout_outcome_status"] == "PRESENT_ON_CHECKOUT_HEAD" for x in rows["rows"]
        ))
        self.assertTrue(all("current_main_outcome_status" not in x for x in rows["rows"]))

    def test_checked_in_r1_v2_matches_frozen_context_generation_byte_for_byte(self):
        # CI must compare the published research artifact to exact recomputation,
        # not only compare an intentionally selected status/count summary.
        pinned = "5a41cd3043bb582524f15fe9fde6f52792246a54"
        path = admission.ROOT / (
            "04_MARKET_LEARNING/handlekompas/research/"
            "2026-10-15__TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2.json"
        )
        rebuilt = (json.dumps(build(context_ref=pinned), indent=2, ensure_ascii=False) + "\n").encode()
        self.assertEqual(path.read_bytes(), rebuilt)
        self.assertEqual(json.loads(rebuilt)["cohort"]["admitted"], 0)

    def test_explicit_immutable_context_ref_is_not_ambient_synthetic_head(self):
        pinned = "5a41cd3043bb582524f15fe9fde6f52792246a54"
        historic = build(context_ref=pinned)
        self.assertEqual(historic["contract"], "TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2")
        self.assertEqual(historic["generated_from_context_ref_sha"], pinned)
        self.assertNotIn("generated_from_checkout_head_sha", historic)
        self.assertNotIn("generated_from_main_sha", historic)
        self.assertEqual(historic["cohort"]["admitted"], 0)
        self.assertEqual(len(historic["rows"]), 11)
        for bad in ("main", "HEAD", "0" * 39, "g" * 40):
            with self.subTest(invalid_ref=bad), self.assertRaises(ValueError):
                build(context_ref=bad)
        with self.assertRaises(subprocess.CalledProcessError):
            build(context_ref="0" * 40)

    def test_original_forecast_packet_identity_must_be_consistent_across_all_bindings(self):
        # Simulate post-decode corruption after an exact Git blob check. Both
        # source *identity* and hash must be cross-checked against the
        # independent frozen packet, not trusted from the forecast alone.
        real_original = admission.original
        forecast_suffix = "/CMP-20261012-468da783e9d8.json"
        mutations = (
            ("universe_path", lambda f: f["evidence_snapshot"]["full_feature_universe_reference"].__setitem__("packet_path", "wrong.json")),
            ("universe_hash", lambda f: f["evidence_snapshot"]["full_feature_universe_reference"].__setitem__("packet_sha256", "0" * 64)),
            ("binding_path", lambda f: f["source_bindings"]["auto_market_state"].__setitem__("packet_path", "wrong.json")),
            ("binding_hash", lambda f: f["source_bindings"]["auto_market_state"].__setitem__("packet_sha256", "0" * 64)),
            ("selected_path", lambda f: f["evidence_snapshot"]["selected_features"][0].__setitem__("source_path", "wrong.json")),
        )
        for label, change in mutations:
            def forged_original(ref, path, expected_blob=None):
                obj, blob = real_original(ref, path, expected_blob)
                if path.endswith(forecast_suffix):
                    obj = json.loads(json.dumps(obj))
                    change(obj)
                return obj, blob
            with self.subTest(label=label):
                with mock.patch.object(admission, "original", side_effect=forged_original):
                    with self.assertRaisesRegex(ValueError, "packet binding mismatch|Selected feature packet path mismatch"):
                        build()

    def test_full_cohort_fails_closed_and_separates_later_outcomes(self):
        d = build()
        self.assertEqual(d["cohort"], {"original_attempts": 11, "original_outcomes_present": 9, "original_outcomes_absent": 2, "unique_source_blobs": 10, "unique_raw_capture_blobs": 7, "admitted": 0, "independent_market_event_families_certified": 0})
        self.assertEqual(sum(len(r["selected_feature_clocks"]) for r in d["rows"]), 264)
        self.assertEqual(sum(r["checkout_outcome_status"] == "PRESENT_ON_CHECKOUT_HEAD" for r in d["rows"]), 11)
        self.assertTrue(all(r["nominal_reference_to_target_seconds"] == 43200 for r in d["rows"] if r["original_outcome_status"] == "PRESENT"))
        self.assertTrue(all(r["admissibility"] == "NOT_ADMITTED" and r["first_user_delivery_at_utc"] is None for r in d["rows"]))
        self.assertTrue(all(r["collector_clocks"]["selected_CFGI_scores_match_capture"] and r["collector_clocks"]["selected_OKX_funding_quotes_match_capture"] for r in d["rows"]))
        serialized = json.dumps(d)
        self.assertNotIn('"value":', serialized)
        self.assertNotIn('"funding_rate":', serialized)
        self.assertNotIn('"price":', serialized)


from scripts.research import task2_r1_scoped_readiness_v1 as readiness


class ScopedReadinessReconciliationTests(unittest.TestCase):
    """No market feature is selected and no historical PIT promotion is possible."""

    def sample(self):
        return readiness.pinned_inputs()

    def reject(self, sample, reason):
        with self.assertRaisesRegex(ValueError, "TASK2_RECONCILE_"+reason):
            readiness.reconcile(sample)

    def test_original_frozen_four_receipts_reconcile(self):
        r=readiness.reconcile(self.sample())
        self.assertEqual(r["counts"]["original_attempts"],11)
        self.assertEqual(r["counts"]["source_replayed"],11)
        self.assertEqual(r["counts"]["scoped_source_chain_complete"],10)
        self.assertEqual(r["counts"]["scoped_source_chain_unverified"],1)
        self.assertEqual(r["counts"]["original_outcomes_present"],9)
        self.assertEqual(r["counts"]["original_outcomes_absent"],2)
        self.assertEqual(r["counts"]["connected_outcome_overlap_blocks"],1)
        self.assertEqual(r["counts"]["full_historical_pit_admissions"],0)
        self.assertEqual(r["counts"]["certified_independent_market_event_families"],0)
        self.assertFalse(r["portfolio_execution_allowed"])
        self.assertFalse(r["economic_edge_claim"])
        self.assertFalse(r["forecast_accuracy_edge_claim"])

    def test_development_is_not_certified_historical_backtest(self):
        r=readiness.reconcile(self.sample())
        self.assertEqual(r["counts"]["matched_nonabstained_asset_slots"],16)
        self.assertEqual(r["counts"]["model_correct"],7)
        self.assertEqual(r["counts"]["B2_correct"],7)
        self.assertIn("BLOCKED",r["modes"]["HISTORICAL_PIT_MODEL_BACKTEST"])
        self.assertIn("BLOCKED",r["modes"]["AFTER_COST_INVESTOR_TOURNAMENT"])
        self.assertIn("FORBIDDEN",r["modes"]["ROUND3_OUTCOME_ANALYSIS"])
        self.assertNotIn("price_usd",json.dumps(r))

    def test_fake_historical_pit_admission_rejected(self):
        x=self.sample()
        x["ledger"]["rows"][0]["information_edge_gate"]["status"]="ADMITTED"
        self.reject(x,"FORECAST_UNVERIFIED_GATE")

    def test_fake_source_r1_admission_rejected(self):
        x=self.sample()
        x["source"]["rows"][0]["full_R1_admitted"]=True
        self.reject(x,"FORGED_R1_ADMISSION")

    def test_fake_scoped_publication_fails_without_original_server_log(self):
        x=self.sample()
        original=next(r for r in x["source"]["rows"] if
                      not r["scope_specific_source_chain_complete"])
        original["scope_specific_source_chain_complete"]=True
        self.reject(x,"SOURCE_PUBLICATION_CONFLICT")

    def test_source_complete_requires_proven_remote_push_before_issue(self):
        x=self.sample()
        completed=next(r for r in x["source"]["rows"] if
                       r["scope_specific_source_chain_complete"])
        completed["packet_publication"]["remote_push_reported_at_utc"]="2026-10-14T00:00:00Z"
        self.reject(x,"SERVER_PUBLICATION_PROOF")

    def test_original_hourly_source_arriving_after_decision_rejected(self):
        x=self.sample()
        x["source"]["rows"][0]["hourly_source_availability_upper_bound_utc"]="2026-10-14T00:00:00Z"
        self.reject(x,"HOURLY_AFTER_ISSUE")

    def test_original_outcome_must_not_be_replaced_with_later_backfill(self):
        x=self.sample()
        absent=next(r for r in x["comparison"]["rows"] if
                    r["original_outcome_status"]!="FROZEN_ORIGINAL_HASH_AND_TARGET_MATCHED")
        absent["outcome_git_blob"]="a"*40
        self.reject(x,"BACKFILLED_OUTCOME")

    def test_no_cherry_picking_issued_forecasts(self):
        x=self.sample()
        x["comparison"]["rows"].pop()
        self.reject(x,"ORIGINAL_ATTEMPT_DENOMINATOR")

    def test_duplicate_attempt_cannot_inflate_statistics(self):
        x=self.sample()
        x["source"]["rows"].append(json.loads(json.dumps(x["source"]["rows"][0])))
        self.reject(x,"SOURCE_DUPLICATE_ID")

    def test_wrong_same_clock_outcome_identity_rejected(self):
        x=self.sample()
        record=next(r for r in x["comparison"]["rows"] if
                    r["original_outcome_status"]=="FROZEN_ORIGINAL_HASH_AND_TARGET_MATCHED")
        record["target_at_utc"]="2026-10-15T00:00:00Z"
        self.reject(x,"ORIGINAL_OUTCOME_OR_TARGET_MISMATCH")

    def test_connected_overlapping_targets_do_not_become_independent_events(self):
        x=self.sample()
        x["comparison"]["connected_overlap_blocks_in_nine_target_bound_rows"]=9
        self.reject(x,"CROSS_RECEIPT_CONFLICT")

    def test_exposed_cohort_cannot_claim_untouched_holdout(self):
        x=self.sample()
        x["comparison"]["untouched_holdout"]=True
        self.reject(x,"COMPARISON_SCIENCE_PROMOTION")

    def test_private_round3_historical_use_cannot_be_enabled_by_custody(self):
        x=self.sample()
        x["custody"]["restricted_read_authority"]["round3_value_analysis_authorized_or_executed"]=True
        self.reject(x,"RESTRICTED_SOURCE_AUTHORITY")

    def test_notional_full_sell_economics_not_inferred_from_direction(self):
        x=self.sample()
        x["custody"]["scientific_authority"]["investor_economic_edge_established"]=True
        self.reject(x,"CUSTODY_SCIENCE_PROMOTION")

    def test_receipt_digests_must_be_unchanged(self):
        x=self.sample()
        x["comparison"]["source_audit_result_sha256"]="0"*64
        self.reject(x,"SOURCE_DIGEST_IDENTITY")

    def test_utc_rejects_naive_and_noncanonical_local_times(self):
        for bad in ("2026-10-12T19:59:38", "2026-10-12T21:59:38+02:00", "2026-10-12", None, "2026-10-12T99:59:38Z"):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError,"TASK2_RECONCILE_"):
                readiness.utc(bad)

    def test_pinned_blob_bytes_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for path,_ in readiness.SOURCES.values():
                dest=root/path
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes((readiness.ROOT/path).read_bytes())
            self.assertEqual(readiness.reconcile(readiness.pinned_inputs(root))["counts"]["original_attempts"],11)
            f=root/readiness.SOURCES["source"][0]
            f.write_bytes(f.read_bytes()+b"\n")
            with self.assertRaisesRegex(ValueError,"IMMUTABLE_SOURCE_BLOB_CHANGED"):
                readiness.pinned_inputs(root)



from scripts.research import task2_r1_original_publication_recovery_v1 as recovered


class OriginalPublicationRecoveryTests(unittest.TestCase):
    """The newly recovered server witness repairs ONE publication proof, no PIT/edge."""

    def sample(self):
        return recovered.pinned_inputs(), recovered.load_witness()

    def reject(self, inputs, witness, reason):
        with self.assertRaisesRegex(ValueError, "TASK2_RECONCILE_"+reason):
            recovered.recover(inputs, witness)

    def test_real_original_log_recovers_last_scoped_publication(self):
        inputs, witness = self.sample()
        output = recovered.recover(inputs, witness)
        self.assertEqual(output["original_forecasts"], 11)
        self.assertEqual(output["preexisting_original_publication_witnesses"], 10)
        self.assertEqual(output["new_original_publication_witnesses"], 1)
        self.assertEqual(output["scoped_original_publication_witnesses"], 11)
        self.assertEqual(output["original_witness_publication_commit"], recovered.COMMIT)
        self.assertEqual(output["full_R1_scientific_PIT_admissions"], 0)
        self.assertEqual(output["certified_independent_event_families"], 0)
        self.assertEqual(output["historic_original_outcomes_present"], 9)
        self.assertEqual(output["historic_original_outcomes_absent"], 2)
        self.assertFalse(output["economic_edge_established"])
        self.assertFalse(output["untouched_holdout"])
        self.assertIn("BLOCKED", output["historical_backtest_release"])
        self.assertIn("BLOCKED", output["investor_after_cost_backtest"])

    def test_old_source_recovery_is_not_rewritten(self):
        inputs, witness = self.sample()
        before = recovered.reconcile(inputs)
        recovered.recover(inputs, witness)
        after = recovered.reconcile(inputs)
        self.assertEqual(before, after)
        self.assertEqual(after["counts"]["scoped_source_chain_complete"], 10)
        self.assertEqual(after["counts"]["full_historical_pit_admissions"], 0)

    def test_wrong_original_id_cannot_convert_a_different_attempt(self):
        inputs, witness = self.sample()
        witness["source_forecast_id"] = "CMP-20261013-88618d3ad2a7"
        self.reject(inputs, witness, "RECOVERED_WITNESS_NOT_ORIGINAL_MISSING_CASE")

    def test_original_issuer_clock_cannot_be_backdated(self):
        inputs, witness = self.sample()
        witness["original_forecast_issued_at_utc"] = "2026-10-12T19:58:00Z"
        self.reject(inputs, witness, "RECOVERED_WITNESS_ORIGINAL_ISSUER_CHANGED")

    def test_source_blob_substitution_is_rejected(self):
        inputs, witness = self.sample()
        witness["original_packet_blob_sha"] = "0"*40
        self.reject(inputs, witness, "RECOVERED_WITNESS_ORIGINAL_SOURCE_IDENTITY")

    def test_publication_commit_substitution_is_rejected(self):
        inputs, witness = self.sample()
        witness["original_packet_first_add_commit"] = "0"*40
        self.reject(inputs, witness, "RECOVERED_WITNESS_ORIGINAL_SOURCE_IDENTITY")

    def test_wrong_job_id_cannot_borrow_a_good_run(self):
        inputs, witness = self.sample()
        witness["github_original_job_id"] = 114983897924
        self.reject(inputs, witness, "RECOVERED_WITNESS_GITHUB_RUN_BINDING")

    def test_job_failure_cannot_be_called_a_publication_success(self):
        inputs, witness = self.sample()
        witness["github_original_job_conclusion"] = "failure"
        self.reject(inputs, witness, "RECOVERED_WITNESS_GITHUB_RUN_BINDING")

    def test_forged_original_server_push_line_is_not_accepted(self):
        inputs, witness = self.sample()
        witness["authenticated_log_lines"]["remote_push"] = (
            "2026-10-12T19:59:40Z 74130fa250..6495f36225 HEAD -> main")
        self.reject(inputs, witness, "RECOVERED_WITNESS_ORIGINAL_LOG_IDENTITY")

    def test_forged_original_commit_created_path_is_not_accepted(self):
        inputs, witness = self.sample()
        witness["authenticated_log_lines"]["original_path_first_add"] = (
            "2026-10-12T19:58:03.8343024Z create mode 100644 future.json")
        self.reject(inputs, witness, "RECOVERED_WITNESS_ORIGINAL_LOG_IDENTITY")

    def test_fake_github_log_can_never_claim_vendor_first_publication(self):
        inputs, witness = self.sample()
        witness["first_provider_publication_or_original_response_full_model_verified"] = True
        self.reject(inputs, witness, "RECOVERED_WITNESS_FORBIDDEN_PROMOTION")

    def test_private_round3_stays_off(self):
        inputs, witness = self.sample()
        witness["round3_analysis_authorized"] = True
        self.reject(inputs, witness, "RECOVERED_WITNESS_FORBIDDEN_PROMOTION")

    def test_user_delivery_economics_cannot_be_promoted_from_packet_log(self):
        inputs, witness = self.sample()
        witness["first_user_delivery_verified"] = True
        self.reject(inputs, witness, "RECOVERED_WITNESS_FORBIDDEN_PROMOTION")

    def test_scoped_11_of_11_is_not_global_11_of_11_pit(self):
        inputs, witness = self.sample()
        witness["source_scope_complete_after_this_witness"] = "FULL_HISTORICAL_PIT_ADMITTED"
        self.reject(inputs, witness, "RECOVERED_WITNESS_SCOPED_CLASSIFICATION")

    def test_missing_old_original_still_not_a_new_historical_outcome(self):
        inputs, witness = self.sample()
        inputs["ledger"]["cohort"]["admitted"] = 1
        self.reject(inputs, witness, "ORIGINAL_SCIENCE_GATE")

    def test_recovered_server_line_requires_strict_utc(self):
        with self.assertRaisesRegex(ValueError, "TASK2_RECONCILE_"):
            recovered.logtime("2026-10-12T21:58:05+02:00 HEAD -> main")

    def test_witness_is_pinned_to_exact_public_git_blob(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / recovered.PATH
            path.parent.mkdir(parents=True)
            path.write_bytes((recovered.ROOT / recovered.PATH).read_bytes())
            self.assertEqual(recovered.load_witness(root)["contract"],
                             "TASK2_R1_MISSING_ORIGINAL_PUBLICATION_WITNESS_V1")
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "WITNESS_IMMUTABLE_BLOB_CHANGED"):
                recovered.load_witness(root)



from scripts.research import task2_r1_original_causal_source_matrix_v1 as causal


class OriginalCausalSourceInventoryTests(unittest.TestCase):
    """Frozen code/forecast field roles and source clock gaps, no PIT promotion."""

    def test_pinned_original_engine_extracts_exact_12h_direction_inputs(self):
        raw=causal.original.git("show", f"{causal.ORIGINAL_ENGINE_REF}:{causal.ENGINE_PATH}")
        actual=causal.audited_original_engine(raw)
        self.assertEqual(actual["original_12h_direction_delta_source_keys"],
                         ["btc_usdt", "eth_usdt", "ethbtc"])
        self.assertEqual(actual["direction_sign_required_deltas"],
                         ["btc_delta_since_prior_packet_pct","eth_delta_since_prior_packet_pct"])
        self.assertEqual(len(actual["evidence_snapshot_index_ids"]),24)
        self.assertEqual(actual["source_git_blob"],causal.ENGINE_SHA)

    def test_genuine_original_11_attempt_causal_inventory(self):
        r=causal.build()
        self.assertEqual(r["original_forecasts"],11)
        self.assertEqual(r["selected_feature_instances"],264)
        self.assertEqual(r["source_role_counts"],{
            "DIRECT_12H_DIRECTION_DELTA":22,
            "ORIGINAL_PRICE_INPUT_TO_DIRECTION_DELTA_AND_REFERENCE":22,
            "RELATIVE_DIRECTION_CONTEXT_NOT_BTC_ETH_12H_SIGN":22,
            "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN":198,
        })
        self.assertEqual(r["scoped_original_packet_publication_witnesses"],11)
        self.assertEqual(r["full_original_R1_PIT_admissions"],0)
        self.assertFalse(r["source_authentication_semantics"]["full_model_historical_backtest_authorized"])
        self.assertEqual(len(r["original_rows"]),11)
        self.assertEqual(sum(x["original_outcome_state"]=="PRESENT" for x in r["original_rows"]),9)
        self.assertEqual(sum(x["original_outcome_state"]=="ABSENT_AT_ORIGINAL_SNAPSHOT" for x in r["original_rows"]),2)
        self.assertFalse(any(r["prohibitions"].values()))

    def test_source_clock_count_does_not_mean_publication_admission(self):
        r=causal.build()
        self.assertEqual(sum(r["selected_feature_clock_status_counts"].values()),264)
        self.assertEqual(sum(r["selected_feature_owner_counts"].values()),264)
        self.assertEqual(r["source_authentication_semantics"]["entire_upstream_vendor_revision_first_known"],
                         "NOT_VERIFIED")
        self.assertEqual(r["independent_12h_market_event_families_certified"],0)
        self.assertNotIn('"value":',json.dumps(r))
        self.assertNotIn('"funding_rate":',json.dumps(r))

    def test_altered_frozen_engine_fails_even_if_shape_appears_similar(self):
        raw=causal.original.git("show", f"{causal.ORIGINAL_ENGINE_REF}:{causal.ENGINE_PATH}")
        with self.assertRaisesRegex(ValueError,"ORIGINAL_ENGINE_BLOB_CHANGED"):
            causal.audited_original_engine(raw+b"\n")

    def test_altered_original_sign_logic_fails_closed(self):
        raw=causal.original.git("show", f"{causal.ORIGINAL_ENGINE_REF}:{causal.ENGINE_PATH}")
        with self.assertRaisesRegex(ValueError,"ORIGINAL_ENGINE_BLOB_CHANGED"):
            causal.audited_original_engine(raw.replace(b'btc > 0 and eth > 0',
                                                       b'btc > 0 or eth > 0'))

    def test_missing_a_directional_feature_is_not_silently_ignored(self):
        x=causal.pinned_inputs()
        x["ledger"]["rows"][0]["selected_feature_clocks"].pop()
        with self.assertRaisesRegex(ValueError,"ORIGINAL_LEDGER_FEATURE_ROSTER"):
            causal.build(originals=x)

    def test_moved_original_source_clock_cannot_invalidate_history_silently(self):
        x=causal.pinned_inputs()
        x["ledger"]["rows"][0]["selected_feature_clocks"][0]["declared_observed_at"]="2026-10-14T20:00:00Z"
        with self.assertRaisesRegex(ValueError,"ORIGINAL_FIELD_SOURCE_OR_CLOCK_MISMATCH"):
            causal.build(originals=x)

    def test_original_forecast_must_match_frozen_main_source_and_issuer(self):
        x=causal.pinned_inputs()
        x["ledger"]["rows"][0]["original_forecast_git_blob_sha"]="0"*40
        with self.assertRaisesRegex(ValueError,"ORIGINAL_FORECAST_IDENTITY|ORIGINAL_FORECAST_GIT_BLOB|ORIGINAL_ATTEMPT"):
            causal.build(originals=x)

    def test_original_vintage_inventory_rejects_forged_pit_promotion(self):
        x=causal.pinned_inputs()
        x["ledger"]["rows"][0]["information_edge_gate"]["status"]="ADMITTED"
        with self.assertRaisesRegex(ValueError,"FORECAST_UNVERIFIED_GATE"):
            causal.build(originals=x)

    def test_cannot_backfill_original_outcomes_in_causal_inventory(self):
        x=causal.pinned_inputs()
        missing=next(y for y in x["ledger"]["rows"] if y["original_outcome_status"]=="ABSENT_AT_ORIGINAL_SNAPSHOT")
        missing["original_outcome_status"]="PRESENT"
        with self.assertRaisesRegex(ValueError,"ORIGINAL_OUTCOME_OR_TARGET_MISMATCH"):
            causal.build(originals=x)

    def test_cannot_change_24_feature_role_contract_without_reproving_engine(self):
        old=causal.ROLES["sentiment_market_score"]
        try:
            causal.ROLES["sentiment_market_score"]="DIRECT_12H_DIRECTION_DELTA"
            raw=causal.original.git("show", f"{causal.ORIGINAL_ENGINE_REF}:{causal.ENGINE_PATH}")
            with self.assertRaisesRegex(ValueError,"ROLE_DENOMINATOR_CHANGED"):
                causal.audited_original_engine(raw)
        finally:
            causal.ROLES["sentiment_market_score"]=old

    def test_independent_event_n_is_still_zero_even_with_all_packet_publications(self):
        r=causal.build()
        self.assertEqual(r["original_forecasts"],r["scoped_original_packet_publication_witnesses"])
        self.assertEqual(r["full_original_R1_PIT_admissions"],0)
        self.assertEqual(r["independent_12h_market_event_families_certified"],0)
        self.assertEqual(r["source_authentication_semantics"]["original_12h_direction"],
                         "NOWCAST_DELTA_CONTINUATION_NOT_PROVEN_PREDICTIVE_EDGE")



if __name__ == "__main__":
    unittest.main()
