from typing import Dict, List, Optional, Union, Any
import pytest
from unittest.mock import patch


def test_matplotlib_import_success():
    with patch("matplotlib.use") as mock_use:
        pass
        mock_use.assert_called_once_with("Agg")


def test_matplotlib_import_failure():
    with patch.dict("sys.modules", {"matplotlib": None}):
        with pytest.raises(SystemExit) as exc_info:
            with patch("builtins.print") as mock_print:
                import importlib
                import src.config.config
                importlib.reload(src.config.config)

        assert exc_info.value.code == 1
        mock_print.assert_called_once_with(
            "Error: matplotlib is not installed. Please run: pip install matplotlib"
        )
