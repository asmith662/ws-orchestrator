class Fmt:
    @staticmethod
    def tab(s: str or object, indent_num: int = 1):
        return s if indent_num == 0 else indent_num * '    ' + s

    # a paragraph
    @staticmethod
    def msg(*args, orientation: str = 'vert'):
        if orientation == 'vert':
            return '\n'.join(args)
        elif orientation == 'horz':
            return ' | '.join(args)

    # aliases
    t = tab
    m = msg

