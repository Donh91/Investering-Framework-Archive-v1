/** Shared width AND height assertion for real CDP mobile acceptance.
 * Preserve the first actual browser failure, rather than forcing viewport or
 * discarding evidence. In the browser test, diagnostics show state before and
 * after clicking UI controls. No CSS or forecast behavior is modified here.
 */
import assert from 'node:assert/strict';

export function assertExactMobileViewport(report, expectedWidth, expectedHeight, before = {}) {
  const diagnostic = JSON.stringify({
    expected: {width: expectedWidth, height: expectedHeight},
    before,
    after: {
      width: report.width,
      height: report.height,
      documentClientWidth: report.documentClientWidth,
      documentScrollWidth: report.documentScrollWidth,
      visualViewportWidth: report.visualViewportWidth,
      viewportMeta: report.viewportMeta
    }
  });
  assert.equal(report.width, expectedWidth, 'Wrong CDP viewport width ' + diagnostic);
  assert.equal(report.height, expectedHeight, 'Wrong CDP viewport height ' + diagnostic);
}
