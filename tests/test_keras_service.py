import pytest
from services.keras_service import KerasService


def test_scores_between_zero_and_one_become_percentages():
    assert KerasService.scores_to_percentages([0.04, 0.91, 0.05]) == [4.0, 91.0, 5.0]


def test_percentages_are_not_multiplied_twice():
    assert KerasService.scores_to_percentages([4, 91, 5]) == [4.0, 91.0, 5.0]


def test_invalid_scores_are_rejected():
    with pytest.raises(ValueError):
        KerasService.scores_to_percentages([])
