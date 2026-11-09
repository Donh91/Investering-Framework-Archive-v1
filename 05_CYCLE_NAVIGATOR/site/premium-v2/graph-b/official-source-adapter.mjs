/**
 * Compatibility import for the isolated Premium v2 Graph B prototype.
 * Canonical source-only validators now live at site/source-adapter, shared
 * with the public CN SITE v2 module. NO second forecast or data interpreter.
 */
export {readOfficialGraphB,replayObservedUntil}
  from '../../source-adapter/official-source-adapter.mjs';
