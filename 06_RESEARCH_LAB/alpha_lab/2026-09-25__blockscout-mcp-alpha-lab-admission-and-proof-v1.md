# Blockscout MCP -> Alpha Lab admission + proof-of-value v1

Date: 2026-09-25
Status: ADMITTED_AS_DETERMINISTIC_ENRICHMENT_SOURCE
Authority: research / identity / onchain verification only
Trading authority: NONE
Owner: existing Alpha Lab / Project->CA / Meme Alpha owners
Parallel scanner: FORBIDDEN

## Why this matters

A live Blockscout MCP connection was tested against known Robinhood Chain Alpha Lab cases on chain id 4663.

The result is materially useful.

The source can deterministically provide, in one bounded path:
- address existence and contract state;
- exact creation tx / first transaction block + timestamp;
- token name/symbol/supply/holders;
- verified-contract state and proxy state;
- source-code metadata and constructor arguments;
- decoded launch transaction inputs;
- token mint/transfer events;
- exact project launcher/deployer;
- exact Pons curve / launch-factory fields;
- launch quote amount;
- launch recipient;
- initial tokens acquired;
- snipe-tax exemption arrays;
- first-party social metadata embedded in Pons launch params.

This closes several recurring Alpha Lab UNKNOWNs without relying on DexScreener inference or model interpretation.

## Source role

Blockscout MCP becomes a first-class deterministic ENRICHMENT / VERIFICATION source under the existing source architecture.

It does NOT become:
- a new scanner;
- a project-ownership oracle;
- a market-price oracle;
- a BUY/SELL engine;
- a substitute for first-party project authentication;
- proof that a verified contract is safe.

Authority by fact family:

HIGH:
- chain id;
- address existence;
- contract / EOA status;
- creation transaction;
- block/timestamp;
- exact bytecode/source verification state;
- decoded transaction calldata when available;
- token transfer/mint events;
- token metadata read from indexed chain state.

MEDIUM:
- Pons launch metadata/social links, because these are onchain but self-asserted by the launcher;
- explorer labels / token names.

LOW / NONE:
- project ownership without first-party cross-binding;
- economic quality;
- market outcome;
- legitimacy merely because Blockscout says verified or reputation=ok.

## Proof-of-value run

### Case A - OSINKO

Exact CA:
`0x8cd57b19033a90b753d73dbc122367a4a52b8586`

Blockscout live result:
- contract: YES;
- verified: YES;
- contract name: `PonsV2LauncherToken`;
- proxy: none indexed;
- total supply: 1,000,000,000 OSINKO;
- holder count at observation: 352;
- creation tx: `0x81ee24acd5955346cee7d493560964a1f88d3ffc93ce3f053ac8c2f7db161609`;
- creation/launch block: 57,911,081 for launch tx;
- launch tx timestamp: 2026-09-08T18:39:29Z;
- project launcher / recipient: `0x2DeFd4734CFEb3A3D3653c659b3397897f0b2Db0`;
- Pons launch method: `launchAndBuy`;
- quoteIn: 0.01 ETH;
- initial OSINKO transferred to launcher: ~5.740664M = ~0.5741% of 1B supply;
- snipeTaxExemptions: 0;
- onchain launch description: "The On-Chain Dividend Engine";
- onchain social: `https://x.com/UseOsinko`.

Learning:
The previous OSINKO packet had original token creation / Pons origin / creator and initial allocation as unresolved. Blockscout MCP resolves a large part of that deterministically and confirms that the manually supplied Sep-8 first-party post was essentially contemporaneous with launch.

### Case B - NOIR / NoirPay

Exact CA:
`0xA5F832390447b050955D7b734a9A2fA861B4d3AB`

Blockscout live result:
- contract: YES;
- verified: YES;
- contract: `PonsV2LauncherToken`;
- proxy: none indexed;
- total supply: 1,000,000,000 NOIR;
- holder count at observation: 480;
- creation tx: `0xe045c9d18cce9d4dd7bd9773892e843c50097db68e14337041c8a15bf586b0a7`;
- launch block: 68,914,705;
- launch timestamp: 2026-09-21T15:45:20Z;
- project launcher / recipient: `0x28141bC1Ec06765aBD137eE94D03EaFC18D77792`;
- Pons launch method: `launchAndBuy`;
- quoteIn: 0.1 ETH;
- initial NOIR transferred to launcher: ~54.586382M = ~5.4586% of supply;
- snipeTaxExemptions: 0;
- onchain socials include `https://x.com/noirpay` and `https://t.me/noirpayapp`;
- decoded constructor binds the same project description;
- verified source tree contains the Pons V2 launcher, bonding curve, graduation, hook, locker and buyback-vault components;
- constructor directly records curve `0x6ad81AA97f7Ea92310225fE11a6af51339180460` and launch factory `0x7eD598BcEf8bd9Edd8C97A195C6d13f40801EC7e`.

Learning:
NOIR's earlier audit had origin/access-fairness fields unresolved. We can now distinguish:
- no exemption list at launch;
- a comparatively large ~5.46% initial launcher acquisition;
- exact launch time and launcher wallet;
- first-party-like social metadata embedded in the launch itself.

This should become a prospective risk/structure feature, not a one-case threshold.

### Case C - DEED

Exact CA:
`0x5e55f18453545d0d4314c5106a2d8db934298e95`

Blockscout live result reproduces prior canonical forensic work:
- launch tx: `0x36536d4e8bd99303b7782e88dfe965f2cd9be5e8169725400eb2b4e884f94bc7`;
- launch block: 69,205,683;
- launch timestamp: 2026-09-21T23:51:56Z;
- launcher/recipient: `0x0052BB21E9CccfcB790913fe3D9bc52cC45d9dD9`;
- quoteIn: ~0.0528369682 ETH;
- initial DEED: 29.9M = 2.99% of supply;
- snipeTaxExemptions: 25 addresses;
- first-party-like metadata includes x.com/deedestate, Telegram and deed.estate.

This exact match to earlier DEED reconstruction is strong validation that Blockscout MCP can reproduce critical launch-origin evidence consistently.

### Case D - DUCAT prelaunch negative control

Official announced CA:
`0xD0cA71118ca21D674f9018A53026a38A0AB54DbF`

At 2026-09-25 early prelaunch observation Blockscout reported:
- is_contract: FALSE;
- creation tx: NONE;
- first transaction: NONE;
- verified: FALSE;
- token metadata: NONE.

Learning:
This is a valuable healthy-zero / negative-control use case.
The announced CA existed as an address value, but the contract was not yet deployed.
The source can therefore distinguish:
`FIRST_PARTY_CA_ANNOUNCED` from `ONCHAIN_DEPLOYED`.

Do not turn "not deployed yet" into project invalidation.

## High-value features to persist prospectively

For each new exact CA where Blockscout supports Robinhood Chain, freeze:

`blockscout_observed_at`
`chain_id`
`address_exists`
`is_contract`
`is_verified`
`proxy_type`
`creation_tx`
`creation_block`
`creation_timestamp`
`creator_address`
`contract_name`
`token_name`
`token_symbol`
`total_supply`
`holder_count_at_observation`
`launch_method`
`launcher_address`
`recipient`
`launch_factory`
`curve`
`pair_token`
`quote_in`
`initial_tokens_received`
`initial_buy_pct_supply`
`snipe_exemption_count`
`snipe_exemption_addresses_hash`
`embedded_project_socials`
`embedded_description_hash`
`source_verification_state`
`source_health`

UNKNOWN stays UNKNOWN.

Do not persist mutable current holder counts as launch-state unless observation time is frozen.

## Autonomous use policy

Use Blockscout MCP AFTER discovery or exact candidate identification, not as an unbounded whole-chain crawler.

Preferred order:
1. discovery source identifies project/CA/pool candidate;
2. exact CA resolution;
3. Blockscout address info;
4. if contract verified, inspect metadata/source only when it can change qualification;
5. decode creation/launch tx;
6. derive launch-origin/access-fairness fields;
7. cross-bind embedded metadata to first-party project source;
8. continue liquidity/sellability/market outcome with appropriate market sources.

This keeps cost/context low while materially improving truth quality.

## Pool-ID resolution

DexScreener Uniswap-v4 links often contain a 32-byte PoolId rather than a 20-byte token CA.

Hard rule:
`bytes32 pool id != token CA`.

When given a v4 PoolId:
- do not guess token identity;
- resolve pool initialization / currencies using deterministic chain evidence;
- only then run the exact-CA path above.

The current manually supplied pool id
`0xb09df62e4f4bb1bbf2b7f97e9865c62648c3957b2ea0a7b31b447447f87baf51`
remains `PENDING_DETERMINISTIC_POOL_KEY_RESOLUTION` because the free Blockscout MCP session budget was exhausted after the proof run. Preserve it as unresolved, not failed.

## Source health / cost governance

Observed Blockscout MCP behavior:
- Robinhood Chain 4663 is directly supported;
- free session exposed an 8-call budget;
- deterministic address/tx/code calls returned useful structured evidence;
- server warns that from 2026-10-08 a Blockscout PRO API key will be required.

Therefore:
- treat connector availability and remaining call budget as explicit source health;
- cache immutable evidence;
- never repeat creation-tx/code calls unless evidence/version changed;
- use one address-info call as cheap triage;
- reserve code/ABI calls for material cases;
- before 2026-10-08 decide whether the framework should provision a PRO key or rely on existing RPC/explorer fallbacks;
- failure/quota exhaustion = DEGRADED/UNAVAILABLE, never negative chain evidence.

## Learning hypotheses enabled

Do not fit thresholds yet.

Prospective candidate features now measurable:
- initial launcher buy % of supply;
- launch quote size;
- exemption count / exemption graph;
- launcher prior history;
- embedded-social continuity;
- deployer/factory continuity;
- verified-code timing relative to launch;
- proxy/admin topology;
- delay between deployment, first-party CA publication, market creation and broad social propagation.

These can be tested against matched Pons winners/failures.

A particularly useful candidate hypothesis:
`access-fairness topology + initial launcher allocation + independent early buyer breadth`
may improve qualification beyond raw volume/holders alone.

DEED / NOIR / OSINKO are historical representation rows only.
No retrospective alpha credit.

## Architecture verdict

ADMIT_BLOCKSCOUT_MCP = YES
ROLE = DETERMINISTIC_ONCHAIN_ENRICHMENT
DUPLICATE_ENGINE = NO
REPLACE_RPC = NO
REPLACE_MARKET_DATA = NO
REPLACE_FIRST_PARTY_AUTH = NO
ALPHA_EDGE = UNPROVEN
EXPECTED_VALUE = HIGH_FOR_DATA_TRUTH_AND_FALSE_POSITIVE_REDUCTION

The primary value is not "finding pumps".
It is shrinking identity/origin/access-fairness UNKNOWNs quickly enough that Alpha Lab can make earlier, cleaner decisions on genuinely interesting candidates.
