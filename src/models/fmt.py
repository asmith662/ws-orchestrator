class Fmt:
    @staticmethod
    def tab(s: str or object, indent_num: int = 0):
        return s if indent_num == 0 else indent_num * '    ' + s

    # a paragraph
    @staticmethod
    def msg(*args):
        return '\n'.join(args)

    # aliases
    t = tab
    m = msg
