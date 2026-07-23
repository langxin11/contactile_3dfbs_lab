"""quick_read CLI 的无硬件测试。"""

import unittest

from typer.testing import CliRunner

from quick_read import app

runner = CliRunner()


class QuickReadCliTest(unittest.TestCase):
    def test_mock_defaults_to_no_bias(self) -> None:
        result = runner.invoke(app, ["--mock", "--count", "2"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("未执行初始硬件去皮", result.stdout)
        self.assertIn("使用模拟数据，不访问传感器", result.stdout)
        self.assertIn("读取 2 次传感器数据", result.stdout)

    def test_mock_bias_is_optional(self) -> None:
        result = runner.invoke(app, ["--mock", "--bias", "--count", "1"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("将执行初始硬件去皮", result.stdout)
        self.assertIn("读取 1 次传感器数据", result.stdout)

    def test_count_must_be_positive(self) -> None:
        result = runner.invoke(app, ["--mock", "--count", "0"])

        self.assertEqual(result.exit_code, 2)


if __name__ == "__main__":
    unittest.main()
