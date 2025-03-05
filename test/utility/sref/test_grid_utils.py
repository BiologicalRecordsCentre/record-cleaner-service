import pytest

from app.utility.sref.grid_utils import GridUtils


class TestGbGrid:
    def test_get_letter_index(self):
        utils = GridUtils()

        index = utils.get_letter_index('V')
        assert index == (0, 0)

        index = utils.get_letter_index('A')
        assert index == (4, 0)

        index = utils.get_letter_index('Z')
        assert index == (0, 4)

        index = utils.get_letter_index('E')
        assert index == (4, 4)

    def test_get_offset_letter(self):
        utils = GridUtils()

        letter, offset = utils.get_offset_letter('N', (0, 0))
        assert letter == 'N'
        assert offset == (0, 0)

        letter, offset = utils.get_offset_letter('N', (1, 1))
        assert letter == 'J'
        assert offset == (0, 0)

        letter, offset = utils.get_offset_letter('N', (2, 2))
        assert letter == 'E'
        assert offset == (0, 0)

        letter, offset = utils.get_offset_letter('N', (3, 3))
        assert letter == 'V'
        assert offset == (1, 1)

        letter, offset = utils.get_offset_letter('N', (-1, -1))
        assert letter == 'R'
        assert offset == (0, 0)

        letter, offset = utils.get_offset_letter('N', (-2, -2))
        assert letter == 'V'
        assert offset == (0, 0)

        letter, offset = utils.get_offset_letter('N', (-3, -3))
        assert letter == 'E'
        assert offset == (-1, -1)

    def test_get_offset_km100(self):
        utils = GridUtils()

        # UK style
        # https://en.wikipedia.org/wiki/Ordnance_Survey_National_Grid#/media/File:British_National_Grid.svg
        assert utils.get_offset_km100('TL', (1, 0)) == 'TF'
        assert utils.get_offset_km100('TL', (-1, 0)) == 'TQ'
        assert utils.get_offset_km100('TL', (0, -1)) == 'SP'
        assert utils.get_offset_km100('TL', (0, 1)) == 'TM'

        # Irish style
        # https://en.wikipedia.org/wiki/Irish_grid_reference_system#/media/File:Irish_Grid.svg
        assert utils.get_offset_km100('N', (1, 1)) == 'J'
        assert utils.get_offset_km100('N', (-1, 1)) == 'T'
        assert utils.get_offset_km100('N', (-1, -1)) == 'R'
        assert utils.get_offset_km100('N', (1, -1)) == 'G'

    def test_get_offset_km10(self):
        utils = GridUtils()

        assert utils.get_offset_km10('TL00', (1, 0)) == 'TL01'
        assert utils.get_offset_km10('TL00', (-1, 0)) == 'TQ09'
        assert utils.get_offset_km10('TL00', (0, -1)) == 'SP90'
        assert utils.get_offset_km10('TL00', (0, 1)) == 'TL10'

    def test_get_surrounding_km10s(self):
        utils = GridUtils()

        km10s = utils.get_surrounding_km10s('TL55', 1)
        assert len(km10s) == 8
        expected = ['TL44', 'TL54', 'TL64',
                    'TL45', 'TL65',
                    'TL46', 'TL56', 'TL66']
        assert km10s == expected
