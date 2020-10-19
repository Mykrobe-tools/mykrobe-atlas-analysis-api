from pytest import fixture

from helpers.grepers import grep_samstats


@fixture
def content():
    return \
"""
# header
SN\tkey1:\tvalue1\tcomment
SN\tkey2:\tvalue2\tcomment
SN\tkey3:\tvalue3\tcomment
random\tline
"""


def test_get_values(content):
    values = grep_samstats(content.splitlines(), ['key1', 'key3'])

    assert values == {
        'key1': 'value1',
        'key3': 'value3'
    }


def test_greper_exists_as_soon_as_all_keys_are_gathered(content):
    values = grep_samstats(content.splitlines(), ['key1'])

    assert values == {
        'key1': 'value1'
    }