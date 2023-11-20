class PlateConfig:

    def __init__(self, name: str, columns: int, rows: int, x_offset: int, y_offset: int, x_spacing: float, y_spacing: float):
        self.name: str = name
        self._columns: int = columns
        self._rows: int = rows
        self._x_offset: int = x_offset
        self._y_offset: int = y_offset
        self._x_spacing: float = x_spacing
        self._y_spacing: float = y_spacing

    @property
    def x_offset(self):
        return self._x_offset

    @x_offset.setter
    def x_offset(self, value):
        self._x_offset = value

    @property
    def x_spacing(self):
        return self._x_spacing

    @x_spacing.setter
    def x_spacing(self, value):
        self._x_spacing = value

    @property
    def y_offset(self):
        return self._y_offset

    @y_offset.setter
    def y_offset(self, value):
        self._y_offset = value

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        self._columns = value

    @property
    def y_spacing(self):
        return self._y_spacing

    @y_spacing.setter
    def y_spacing(self, value):
        self._y_spacing = value

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, value):
        self._rows = value


    def __str__(self) -> str:
        return f'''Plate {self.name}: [
                    rows = {self.rows},
                    columns = {self.columns},
                    spacing in X[mm] = {self.x_spacing},
                    spacing in Y[mm] = {self.y_spacing},
                    offset in X[mm] = {self.x_offset},
                    offset in Y[mm] = {self.y_offset}
                ]'''
