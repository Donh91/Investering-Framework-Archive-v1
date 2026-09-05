#!/usr/bin/env python3
import sys
import compounding_learning_v1_core as _core

if __name__ == "__main__":
    _core.main()
else:
    sys.modules[__name__] = _core
