"""
Unit and regression test for the soap package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import soap


def test_soap_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "soap" in sys.modules
