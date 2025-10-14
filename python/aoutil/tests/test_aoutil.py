import pytest
from unittest.mock import patch
from aoutil import aoutil

@pytest.fixture
def mock_aolog():
    with patch('aolog.AoLog') as MockAoLog:
        instance = MockAoLog.return_value
        instance.has_errors = False
        yield instance

def test_row_hash_comparison_lists_equal(mock_aolog):
    row1 = [1, 2, 3]
    row2 = [1, 2, 3]
    log, areSame = aoutil.row_hash_comparison(row1, row2)
    assert areSame is True

def test_row_hash_comparison_lists_unequal_1(mock_aolog):
    row1 = [1, 2, 3]
    row2 = [4, 5, 6]
    log, areSame = aoutil.row_hash_comparison(row1, row2)
    assert areSame is False

def test_row_hash_comparison_lists_unequal_2(mock_aolog):
    row1 = [1, 2, 3]
    row2 = [3, 2, 1]
    log, areSame = aoutil.row_hash_comparison(row1, row2)
    assert areSame is False

def test_row_hash_comparison_dicts_equal(mock_aolog):
    row1 = {'a': 1, 'b': 2}
    row2 = {'b': 2, 'a': 1}
    log, areSame = aoutil.row_hash_comparison(row1, row2)
    assert areSame is True

def test_row_hash_comparison_dicts_key_mismatch(mock_aolog):
    row1 = {'a': 1}
    row2 = {'b': 1}
    log, areSame = aoutil.row_hash_comparison(row1, row2)
    assert areSame is False
    mock_aolog.log_warning.assert_called()

def test_detect_deltas_lists_with_deltas(mock_aolog):
    c1 = [[1, 2], [3, 4]]
    c2 = [[1, 2], [4, 3]]
    log, errors, deltas = aoutil.detect_deltas(c1, c2, None)
    assert errors == []
    assert deltas[0] == 1
    assert isinstance(deltas[1], list)

def test_detect_deltas_dicts_with_key_diff(mock_aolog):
    c1 = {'a': [1, 2], 'b': [3, 4]}
    c2 = {'a': [1, 2], 'c': [3, 4]}
    log, errors, deltas = aoutil.detect_deltas(c1, c2, None)
    assert {'b', 'c'} in deltas

def test_detect_deltas_type_mismatch(mock_aolog):
    c1 = [1, 2]
    c2 = {'a': 1}
    log, errors, deltas = aoutil.detect_deltas(c1, c2, None)
    mock_aolog.log_error.assert_called()

def test_detect_deltas_error_threshold_exceeded(mock_aolog):
    mock_aolog.has_errors = True
    c1 = [[1], [2], [3], [4], [5], [6]]
    c2 = [[1], [2], [3], [4], [5], [6]]
    log, errors, deltas = aoutil.detect_deltas(c1, c2, None, error_threshold=2)
    assert len(errors) > 2
    mock_aolog.log_error.assert_called()