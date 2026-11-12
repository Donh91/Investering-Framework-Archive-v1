/* CN SITE v2.7 · one first-visit motion helper for all tabs (Kompas O2 can adopt it).
 * Plays `cls` on `el` once per visit (sessionStorage `key`), never under reduced motion,
 * never throws: if storage is unavailable it plays at most once per page load. */
const played = new WeakSet();
export function playOnce(key, el, cls, ms = 1200, env = globalThis) {
  if (!el || played.has(el)) return false;
  played.add(el);
  try { if (env.matchMedia && env.matchMedia('(prefers-reduced-motion: reduce)').matches) return false; } catch {}
  try {
    if (env.sessionStorage.getItem(key) === '1') return false;
    env.sessionStorage.setItem(key, '1');
  } catch {}
  el.classList.add(cls);
  (env.setTimeout || setTimeout)(() => el.classList.remove(cls), ms);
  return true;
}
