from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH=Path(__file__).parents[2]/'scripts'/'health'/'check_writer_trigger_safety.py'
spec=importlib.util.spec_from_file_location('writer_safety',MODULE_PATH);module=importlib.util.module_from_spec(spec);assert spec and spec.loader;spec.loader.exec_module(module)

class WriterSafetyV2Tests(unittest.TestCase):
    def inspect(self,text:str):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'workflow.yml';path.write_text(text);return module.inspect(path)
    def test_safe_main_pinned_manual_writer(self):
        findings=self.inspect("""on:\n  workflow_dispatch:\npermissions:\n  contents: write\nconcurrency:\n  group: framework-main-writer\njobs:\n  build:\n    if: github.ref == 'refs/heads/main'\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          ref: main\n      - run: git push origin HEAD:main\n""")
        self.assertEqual(findings,[])
    def test_safe_pr_isolated_writer_group(self):
        findings=self.inspect("""on:
  pull_request:
  workflow_dispatch:
permissions:
  contents: write
concurrency:
  group: ${{ github.event_name == 'pull_request' && format('{0}-pr-{1}', github.workflow, github.event.pull_request.number) || 'framework-main-writer' }}
jobs:
  validate:
    if: github.event_name == 'pull_request'
    steps:
      - run: echo validate
  build:
    if: github.event_name != 'pull_request'
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
      - run: git push origin HEAD:main
""")
        self.assertEqual(findings,[])

    def test_unrecognized_dynamic_writer_group_fails(self):
        findings=self.inspect("""on:
  workflow_dispatch:
permissions:
  contents: write
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
jobs:
  build:
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
      - run: git push origin HEAD:main
""")
        self.assertIn('MAIN_WRITER_WITHOUT_SHARED_CONCURRENCY',findings)

    def test_unpinned_manual_writer_fails(self):
        findings=self.inspect("""on:\n  workflow_dispatch:\npermissions:\n  contents: write\nconcurrency:\n  group: framework-main-writer\njobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n      - run: git push origin HEAD:main\n""")
        self.assertIn('UNPINNED_MANUAL_MAIN_WRITER',findings);self.assertIn('MAIN_WRITER_CHECKOUT_NOT_PINNED',findings)
    def test_push_triggered_writer_fails(self):
        findings=self.inspect("""on:\n  push:\npermissions:\n  contents: write\nconcurrency:\n  group: framework-main-writer\njobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          ref: main\n      - run: git push origin HEAD:main\n""")
        self.assertIn('PUSH_TRIGGERED_MAIN_WRITER',findings)
    def test_missing_shared_concurrency_fails(self):
        findings=self.inspect("""on:\n  workflow_dispatch:\npermissions:\n  contents: write\njobs:\n  build:\n    if: github.ref == 'refs/heads/main'\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          ref: main\n      - run: git push origin HEAD:main\n""")
        self.assertIn('MAIN_WRITER_WITHOUT_SHARED_CONCURRENCY',findings)

if __name__=='__main__':unittest.main()
