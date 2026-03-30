"""Tests for stdout log suppression while Rich Live runs."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import benchmark as benchmark_module


def test_suppress_stdout_info_restores_level():
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(logging.INFO)
    logging.root.addHandler(h)
    try:
        with benchmark_module._suppress_stdout_info_for_rich_live():
            assert h.level == logging.WARNING
        assert h.level == logging.INFO
    finally:
        logging.root.removeHandler(h)


def test_suppress_stdout_touches_only_stdout_handlers(tmp_path):
    """FileHandler levels stay unchanged; stdout StreamHandler is raised to WARNING."""

    out = logging.StreamHandler(sys.stdout)
    out.setLevel(logging.DEBUG)
    logging.root.addHandler(out)

    log_path = tmp_path / "extra.log"
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    logging.root.addHandler(fh)
    try:
        with benchmark_module._suppress_stdout_info_for_rich_live():
            assert out.level == logging.WARNING
            assert fh.level == logging.DEBUG
        assert out.level == logging.DEBUG
        assert fh.level == logging.DEBUG
    finally:
        logging.root.removeHandler(out)
        logging.root.removeHandler(fh)
        fh.close()
