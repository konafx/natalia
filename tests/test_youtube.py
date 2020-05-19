from cogs.youtube import chatcolor

import pytest


class TestChatcolor(object):
    @pytest.mark.parametrize(
        ('tip', 'color'), [
            (199, 'BLUE'),
            (200, 'AQUA'),
            (499, 'AQUA'),
            (500, 'GREEN'),
            (999, 'GREEN'),
            (1000, 'YELLOW'),
            (1999, 'YELLOW'),
            (2000, 'ORANGE'),
            (4999, 'ORANGE'),
            (5000, 'MAGENTA'),
            (9999, 'MAGENTA'),
            (10000, 'RED'),
            (50000, 'RED'),
        ]
    )
    def test_GREEN(self, tip, color):
        assert chatcolor(tip) == color

    def test_RED_under(self):
        with pytest.raises(ValueError):
            chatcolor(0)

    def test_RED_over(self):
        with pytest.raises(ValueError):
            chatcolor(50001)
