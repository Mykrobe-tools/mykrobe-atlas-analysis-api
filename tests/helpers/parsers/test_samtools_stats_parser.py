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
""".encode()


def test_get_values(content):
    parser = SamtoolsStatsParser(content)
    values = parser.get(['key1', 'key3'])

    assert values == {
        'key1': 'value1',
        'key3': 'value3'
    }
