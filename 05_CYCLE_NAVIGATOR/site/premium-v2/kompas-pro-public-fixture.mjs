// Synthetic source-contract fixture. Not market data, not a CDN capture.
export const nowMs=Date.parse('2026-11-24T10:00:00Z');
export const bytes=x=>Buffer.from(JSON.stringify(x)+'\n');
export function fixture(){
 const week='2026-W48',issue=35;
 const latest={schema:'CN_PUBLIC_SNAPSHOT_V2',generated_at:'2026-11-24T09:50:00Z',
  public_series:{contract:'CN_PUBLIC_SERIES_INDEX_v1',current_public_projection:{forecast_week:week,public_issue_number:issue}},
  pointer:{issue_number:39,iso_year:2026,iso_week:48,status:'OK'},package:{issue_number:39,status:'OK',forecast_freeze:{btc_range_low:60000,btc_range_high:70000,eth_range_low:1900,eth_range_high:2300}},
  public_live_precision:{hourly_price_path:{contract:'CN_PUBLIC_HOURLY_PRICE_PATH_v1',forecast_week:week,public_issue_number:issue,observed_through_utc:'2026-11-24T09:00:00Z',BTC:[],ETH:[]}}};
 const compass={contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',compass_id:'SYNTHETIC_ONLY',issued_at_utc:'2026-11-24T09:30:00Z',action_now:'HOLD_WAIT',
  weekly_context:{status:'ALIGNED',forecast_week:week,public_issue_number:issue},
  full_stack:{official_freshness:{contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',status:'VERIFIED_OWNER_POLICY',semantics:'SOURCE_FRESHNESS_EXPIRY_NOT_FORECAST_ETA',source_asof_utc:'2026-11-24T09:00:00Z',valid_until_utc:'2026-11-24T12:00:00Z'}},
  market_now:{directional_state:'BULLISH',market_observation_open_utc:'2026-11-24T08:00:00Z',predecessor_market_observation_open_utc:'2026-11-24T07:00:00Z',new_price_observation:true},
  horizons:Object.fromEntries(['NEXT_1_3D','NEXT_5_7D','NEXT_2_3W','CYCLE_ALTCOINS_3_8W'].map(id=>[id,{expected_direction:'UP',action_posture:'HOLD_WAIT'}])),
  bull_bear_scale:{contract:'OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1',semantics:'EVIDENCE_BALANCE_NOT_PROBABILITY',resolution:'COARSE_CATEGORICAL_DIRECTION',mapping_version:'DIRECTION_ONLY_COARSE_v1',owner:'OFFICIAL_COMPASS',source_of_truth_contract:'MARKET_WEATHER_SOURCE_OF_TRUTH_v1',authority:{site_synthesis_allowed:false,new_market_classifier:false,probability_model:false,portfolio_execution:false},horizons:Object.fromEntries(['1_3d','5_7d','2_3w'].map(id=>[id,{status:'OK',bull:6,bear:4,bias:'LEAN_BULLISH'}]))},
  protection_tracker:{contract:'COMPASS_PROTECTION_TRACKER_v1',authority:{new_market_classifier:false,portfolio_execution:false},pullback_risk_state:'ELEVATED',confidence_quality:'LOW',distribution_risk:'UNKNOWN',reentry_state:'INACTIVE'},
  sell_assessment:{contract:'COMPASS_SELL_ASSESSMENT_v1',authority:{portfolio_execution:false,protection_is_sell_authority:false},state:'NONE'}};
 const lineage={contract:'CN_PUBLICATION_LINEAGE_RELEASE_RECEIPT_v1',semantics:'PUBLIC_BUNDLE_BUILD_TIME_EVIDENCE_NOT_LIVE_CLIENT_FRESHNESS',authority:'READ_ONLY_RECONCILIATION_NO_FORECAST_OR_TRADING_AUTHORITY',source_to_public_equality:'PASS',prospective_forecast_points_created:0,forecast_week:week,public_issue_number:issue,release_freshness_state:'WITHIN_SLA_AT_BUNDLE_TIME',freshness_sla_minutes:90,checked_at_utc:'2026-11-24T09:55:00Z',observed_through_utc:'2026-11-24T09:00:00Z',published_points:{BTC:0,ETH:0}};
 return {latest,compass,lineage};
}
