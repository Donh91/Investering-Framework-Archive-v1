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
        findings=self.inspect("""on:\n  workflow_dispatch:\npermissions:\n  contents: write\nconcurrency:\n  group: framework-main-writer\n  queue: max\n  cancel-in-progress: false\njobs:\n  build:\n    if: github.ref == 'refs/heads/main'\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          ref: main\n      - run: git push origin HEAD:main\n""")
        self.assertEqual(findings,[])
    def test_safe_pr_isolated_writer_group(self):
        findings=self.inspect("""on:
  pull_request:
  workflow_dispatch:
permissions:
  contents: write
concurrency:
  group: ${{ github.event_name == 'pull_request' && format('{0}-pr-{1}', github.workflow, github.event.pull_request.number) || 'framework-main-writer' }}
  queue: max
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

    def test_fixed_main_writer_group_with_pr_validation_is_rejected(self):
        findings=self.inspect("""on:
  pull_request:
  workflow_dispatch:
permissions:
  contents: write
concurrency:
  group: framework-main-writer
  queue: max
  cancel-in-progress: false
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
        self.assertIn('PR_VALIDATION_COMPETES_WITH_MAIN_WRITER',findings)

    def test_approved_market_owner_writer_group_is_safe(self):
        findings=self.inspect("""on:
  workflow_dispatch:
permissions:
  contents: write
concurrency:
  group: framework-market-owner-writer
  queue: max
  cancel-in-progress: false
jobs:
  build:
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
      - run: git push origin HEAD:main
""")
        # Generic temp path is not allowlisted, so exercise the real approved filename too.
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'hourly-sequence-capture.yml'
            path.write_text("""on:
  workflow_dispatch:
permissions:
  contents: write
concurrency:
  group: framework-market-owner-writer
  queue: max
  cancel-in-progress: false
jobs:
  build:
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
      - run: git push origin HEAD:main
""")
            self.assertEqual(module.inspect(path),[])
        self.assertIn('MAIN_WRITER_WITHOUT_SHARED_CONCURRENCY',findings)

    def test_unapproved_market_owner_writer_group_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'unrelated-writer.yml'
            path.write_text("""on:
  workflow_dispatch:
permissions:
  contents: write
concurrency:
  group: framework-market-owner-writer
  queue: max
  cancel-in-progress: false
jobs:
  build:
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
      - run: git push origin HEAD:main
""")
            self.assertIn('MAIN_WRITER_WITHOUT_SHARED_CONCURRENCY',module.inspect(path))

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
        findings=self.inspect("""on:\n  workflow_dispatch:\npermissions:\n  contents: write\nconcurrency:\n  group: framework-main-writer\n  queue: max\n  cancel-in-progress: false\njobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n      - run: git push origin HEAD:main\n""")
        self.assertIn('UNPINNED_MANUAL_MAIN_WRITER',findings);self.assertIn('MAIN_WRITER_CHECKOUT_NOT_PINNED',findings)
    def test_push_triggered_writer_fails(self):
        findings=self.inspect("""on:\n  push:\npermissions:\n  contents: write\nconcurrency:\n  group: framework-main-writer\n  queue: max\n  cancel-in-progress: false\njobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          ref: main\n      - run: git push origin HEAD:main\n""")
        self.assertIn('PUSH_TRIGGERED_MAIN_WRITER',findings)
    def test_missing_shared_concurrency_fails(self):
        findings=self.inspect("""on:\n  workflow_dispatch:\npermissions:\n  contents: write\njobs:\n  build:\n    if: github.ref == 'refs/heads/main'\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          ref: main\n      - run: git push origin HEAD:main\n""")
        self.assertIn('MAIN_WRITER_WITHOUT_SHARED_CONCURRENCY',findings)


    def test_shared_writer_without_max_queue_fails(self):
        findings=self.inspect("""on:
  workflow_dispatch:
permissions:
  contents: write
concurrency:
  group: framework-main-writer
  cancel-in-progress: false
jobs:
  build:
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
      - run: git push origin HEAD:main
""")
        self.assertIn('MAIN_WRITER_WITHOUT_MAX_QUEUE',findings)


    def test_queue_max_with_cancel_expression_fails(self):
        findings=self.inspect("""on:
  pull_request:
permissions:
  contents: write
concurrency:
  group: ${{ github.event_name == 'pull_request' && format('{0}-pr-{1}', github.workflow, github.event.pull_request.number) || 'framework-main-writer' }}
  queue: max
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
jobs:
  build:
    if: github.event_name != 'pull_request'
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
      - run: git push origin HEAD:main
""")
        self.assertIn('MAIN_WRITER_QUEUE_CANCEL_CONFLICT',findings)
    def test_current_market_owner_chain_is_priority_serialized_and_explicit(self):
        root=Path(__file__).parents[2]
        hourly=(root/'.github/workflows/hourly-sequence-capture.yml').read_text()
        entry=(root/'.github/workflows/entry-signal-ledger.yml').read_text()
        native=(root/'.github/workflows/native-handlekompas.yml').read_text()
        recovery=(root/'.github/workflows/native-market-recovery.yml').read_text()
        event=(root/'.github/workflows/compass-event-refresh.yml').read_text()
        daily=(root/'.github/workflows/daily-compass.yml').read_text()
        pages=(root/'.github/workflows/cycle-navigator-pages.yml').read_text()
        for text in (hourly,entry,native,recovery,event,daily):
            self.assertIn('framework-market-owner-writer',text)
            self.assertIn('queue: max',text)
            self.assertIn('cancel-in-progress: false',text)
        self.assertIn('gh workflow run entry-signal-ledger.yml --ref main',hourly)
        self.assertIn('gh workflow run native-handlekompas.yml --ref main',entry)
        self.assertIn('gh workflow run compass-event-refresh.yml --ref main',entry)
        self.assertIn('gh workflow run cycle-navigator-pages.yml --ref main',native)
        self.assertNotIn('workflow_run:',entry)
        self.assertNotIn('workflow_run:',native)
        self.assertNotIn('workflow_run:',event)
        self.assertNotIn('workflow_run:',pages)

if __name__=='__main__':unittest.main()
