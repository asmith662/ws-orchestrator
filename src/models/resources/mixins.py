class Fmt:
    @staticmethod
    def tab(s: str or object, indent_num: int = 1):
        return s if indent_num == 0 else indent_num * '    ' + s

    @staticmethod
    def msg(*args: [str]):
        return '\n'.join(args)

    t = tab
    m = msg


class BasicIterator:
    def __iter__(self):
        return self

    def __next__(self):
        return self
