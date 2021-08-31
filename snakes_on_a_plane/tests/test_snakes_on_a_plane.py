"""
Unit and regression test for the snakes_on_a_plane package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import snakes_on_a_plane


def test_snakes_on_a_plane_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "snakes_on_a_plane" in sys.modules
