from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def test_submodule_fallback_success(gw, tmp_path):
    ret = MagicMock(returncode=0, stderr="", stdout="")
    with patch("subprocess.run", return_value=ret) as m:
        gw.submodule_fallback(tmp_path)
    m.assert_called_once()
    args, kwargs = m.call_args
    assert args[0][:3] == ["git", "submodule", "update"]
    assert kwargs["cwd"] == tmp_path


def test_submodule_fallback_retries_without_recommend_shallow(gw, tmp_path):
    bad = MagicMock(returncode=1, stderr="unknown option", stdout="")
    ok = MagicMock(returncode=0, stderr="", stdout="")
    with patch("subprocess.run", side_effect=[bad, ok]) as m, patch.object(gw, "git_run") as gr:
        gw.submodule_fallback(tmp_path)
    assert m.call_count == 1
    gr.assert_called_once_with(
        ["submodule", "update", "--init", "--recursive"],
        cwd=tmp_path,
    )


def test_submodule_fallback_exits_on_hard_failure(gw, tmp_path):
    bad = MagicMock(returncode=7, stderr="fatal: no submodule mapping", stdout="")
    with patch("subprocess.run", return_value=bad), pytest.raises(SystemExit) as ei:
        gw.submodule_fallback(tmp_path)
    assert ei.value.code == 7
