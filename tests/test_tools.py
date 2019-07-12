"""Tests the tools module"""

import copy

import pytest

import citationweb.tools as t


# Fixtures --------------------------------------------------------------------
@pytest.fixture
def testdict():
    """Create a nested test dictionary with mutable and immutable values"""
    return dict(foo="bar", bar=123.456,
                baz=dict(foo="more_bar", bar=456.123, baz=[1,2,dict(three=3)]),
                nothing=None, more_nothing=None)


# Function tests --------------------------------------------------------------

def test_recursive_update(testdict):
    """Testing if recursive update works as desired."""
    d = testdict
    u = copy.deepcopy(d)

    # Make some changes
    u['more_entries'] = dict(a=1, b=2)
    u['foo'] = "changed_bar"
    u['bar'] = 654.321
    u['baz'] = dict(another_entry="hello", foo="more_changed_bars",
                    nothing=dict(some="thing"))
    u['nothing'] = dict(some="thing")
    u['more_nothing'] = "something"

    assert d != u

    # Perform the update
    d = t.recursive_update(d, u)
    assert d['more_entries'] == dict(a=1, b=2)
    assert d['foo'] == "changed_bar"
    assert d['bar'] == 654.321
    assert d['baz'] == dict(another_entry="hello", foo="more_changed_bars",
                            bar=456.123, baz=[1,2,dict(three=3)],
                            nothing=dict(some="thing"))
    assert d['nothing'] == dict(some="thing")
    assert d['more_nothing'] == "something"
