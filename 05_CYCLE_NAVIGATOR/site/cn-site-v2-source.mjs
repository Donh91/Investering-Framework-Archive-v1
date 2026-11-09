/**
 * CN SITE v2 public, design-neutral data entrypoint.
 *
 * Deliberately NO fetch, DOM, CSS, charts, model calls, source mutations,
 * scoring or second forecast logic. The source-owned contract and validators
 * live in the existing premium-v2/graph-b/official-source-adapter.mjs.
 *
 * Import from a future site design:
 *   import {readOfficialGraphB,replayObservedUntil} from '../cn-site-v2-source.mjs';
 *   const graph = readOfficialGraphB(latest, 'BTC', {
 *     now_utc: new Date().toISOString(), publication_lineage: lineage
 *   });
 *
 * Inputs must be the exact same-origin public JSON files:
 *   /data/latest.json and /data/publication-lineage.json
 * No synthetic sample data or network calls are performed by this module.
 */
export {readOfficialGraphB,replayObservedUntil}
  from './source-adapter/official-source-adapter.mjs';
