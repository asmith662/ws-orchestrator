class Indent:
    def __init__(self, in_str: str, indentation: int = 0, sensitive: bool = False):
        self.in_str = in_str
        self.indentation = self.set_indent(indentation, sensitive)
        self.out_str = self.indentation + self.in_str

    def __repr__(self):
        return repr(f'Msg("{self.in_str}")')

    def __str__(self):
        return self.out_str

    @classmethod
    def set_indent(cls, indentation, sensitive):
        return '' if not sensitive else ''.join(['    '] * (indentation if not sensitive else indentation * 4))




