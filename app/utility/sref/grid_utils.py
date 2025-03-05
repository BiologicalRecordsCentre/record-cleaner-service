class GridUtils:
    """Class holding utility functions for grid-based calculations."""

    grid = ['VWXYZ', 'QRSTU', 'LMNOP', 'FGHJK', 'ABCDE']

    def get_letter_index(self, letter: str):
        """Determine index of letter in grid.

        Args:
            letter (str): The letter to look up.
        Returns:
            (int, int): The indices of the letter in the grid, row, col.
        """

        for i, v in enumerate(self.grid):
            if letter in v:
                row = i
                break
        for i, v in enumerate(self.grid[row]):
            if letter == v:
                col = i
                break
        return row, col

    def get_offset_letter(self, letter: str, offset: tuple[int, int]):
        """Find the grid letter that is offset from another letter.

        Args:
            letter (str): The initial letter.
            offset tuple[int, int]: The offset to apply (row, col)
        Returns:
            tuple[str, list[int, int]]: The letter followed by an offset in
            a parent grid."""
        letter_index = self.get_letter_index(letter)
        offset_letter_index = [0, 0]
        parent_offset = [0, 0]

        for i in range(0, 2):
            new_coord = letter_index[i] + offset[i]
            offset_letter_index[i] = new_coord % 5
            parent_offset[i] = new_coord // 5

        offset_letter = self.grid[offset_letter_index[0]
                                  ][offset_letter_index[1]]

        return (offset_letter, (parent_offset[0], parent_offset[1]))

    def get_offset_km100(self, km100: str, offset: tuple[int, int]):
        """Find the km100 that is offset from another.

        Args:
            km100 (str): Initial km100. E.g. single letter for Ireland or
            two letters for UK.
            offset tuple[int, int]: The offset to apply (north, east)
        Returns:
            str: Offset km100.
        """
        if offset == (0, 0):
            # Return original km100 if no offset.
            return km100

        mutable_offset = [offset[0], offset[1]]
        offset_km100 = ''

        for i in range(len(km100), 0, -1):
            # Loop through letters starting with least significant.
            offset_letter, parent_offset = self.get_offset_letter(
                km100[i-1:i], mutable_offset
            )

            offset_km100 = offset_letter + offset_km100
            mutable_offset = [parent_offset[0], parent_offset[1]]

        return offset_km100

    def get_offset_km10(self, km10: str, offset: tuple[int, int]):
        """Find the km10 that is offset from another.

        Args:
            km10 (str): Initial km10. E.g. S23 or TL32.
            offset tuple[int, int]: The offset to apply (north, east)
        Returns:
            str: Offset km10.
        """
        km10_len = len(km10)
        km100 = km10[0:km10_len-2]
        east = km10[km10_len-2: km10_len-1]
        north = km10[km10_len-1: km10_len]

        # Index is the [row, column] in the 10 x 10 numeric grid in a km100
        km10_index = [int(north), int(east)]
        offset_km10_index = [0, 0]
        parent_offset = [0, 0]

        for i in range(0, 2):
            new_coord = km10_index[i] + offset[i]
            offset_km10_index[i] = new_coord % 10
            parent_offset[i] = new_coord // 10

        offset_km100 = self.get_offset_km100(km100, parent_offset)

        offset_east = str(offset_km10_index[1])
        offset_north = str(offset_km10_index[0])
        offset_km10 = offset_km100 + offset_east + offset_north

        return offset_km10

    def get_surrounding_km10s(self, km10: str, proximity: int):
        """Get a list of km10s that are within proximity of a given km10.

        Args:
            km10 (str): The km10 to look around.
            proximity (int): The distance to look around. 1 gives the 
            surrounding 8 (3x3), 2 gives the surrounding 24 (5x5), etc.
        Returns:
            list[str]: The km10s within proximity of the given km10."""

        km10s = []

        for offset_north in range(-proximity, proximity + 1):
            for offset_east in range(-proximity, proximity + 1):
                offset_km10 = self.get_offset_km10(
                    km10, (offset_north, offset_east)
                )
                if not offset_km10 == km10:
                    # Exclude original km10.
                    km10s.append(offset_km10)

        return km10s
