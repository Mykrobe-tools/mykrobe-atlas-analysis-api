from pytest import fixture

from helpers.parsers.samtools_stats import SamtoolsStatsParser


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
    parser = SamtoolsStatsParser(content.splitlines())
    values = parser.get(['key1', 'key3'])

    assert values == {
        'key1': 'value1',
        'key3': 'value3'
    }


def test_parser_exist_as_soon_as_all_keys_are_gathered(content):
    parser = SamtoolsStatsParser(content.splitlines())
    values = parser.get(['key1'])

    assert values == {
        'key1': 'value1'
    }
