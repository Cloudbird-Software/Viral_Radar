"""W0-C1 骨架验收（pytest 面）：四层包 / 版本契约 / arch 边界执法。

本文件与 tests/card/w0/card-6-python-skeleton.test.ts 互补：TS 驱动是 g050
机器红复现的验收测试，本文件是 python 侧的骨架冒烟（make test 执行）。
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]


class TestSkeleton:
    def test_four_layers_importable(self):
        import viral_radar
        import viral_radar.adapters as adapters
        import viral_radar.analysis as analysis
        import viral_radar.app as app
        import viral_radar.processing as processing

        assert adapters and analysis and app and processing
        assert viral_radar.__version__

    def test_version_is_semver(self):
        import viral_radar

        parts = viral_radar.__version__.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_arch_boundary_pass_on_current_tree(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_arch.py")],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
