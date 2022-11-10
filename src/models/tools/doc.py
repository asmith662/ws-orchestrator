import re
import sys


class OptsParser:
    redir = '^(-|--)\\w+'
    sect = '(?<=\n).+(?=\n)'

    def __init__(self, docstring):
        self.docstring = docstring
        self.sections = self._section(docstring)
        self.args = self.args(docstring)
        self.kwargs = self.kwargs(docstring)
        self.dict = {'args': self.args, 'kwargs': self.kwargs}
        # self.name, self.args = self.usage(self._doc(docstring))
        # self.kwargs = self._options(self._doc(docstring))

    @classmethod
    def _section(cls, docstring):
        return [s.strip() for s in re.findall(OptsParser.sect, docstring)]

    @staticmethod
    def args(docstring):
        sections = [s.strip() for s in re.findall(OptsParser.sect, docstring)]
        usage = [s for s in sections if re.search(r'^(U|u)sage:\s', s)][0]
        section, name, args = usage.replace('[options] ', '').split(' ', 2)
        return [a[1:-1] for a in re.findall(r'<.+>|[.+]', args)]

    @staticmethod
    def kwargs(docstring):
        sections = [s.strip() for s in re.findall(OptsParser.sect, docstring)]
        meta, kwargs = {'keys': [], 'args': [], 'description': []}, []
        for row, opt in enumerate([s for s in sections if re.search(OptsParser.redir, s)]):
            cmds = opt.split(' : ')
            cmd, desc = cmds[0].strip(), cmds[1]
            args = a[0][1:-1] if (a := re.findall(r'<.+>|[.+]', cmd)) else None
            key_type = ktype and (cmd := re.sub('-\\w+$', '', cmd)) \
                if (ktype := re.search(OptsParser.redir + '-', cmd)) else None
            cmd = re.sub('((\\s|=)<.+>|(\\s|=)[.+])', '', cmd)
            if re.search(OptsParser.redir + '\\sor\\s', cmd):
                for k in list(cmd.split(' or ')):
                    kwargs += [{k: args}]
                    # meta += [{k: args, 'type': key_type, 'description': desc}]
            else:
                kwargs += [{cmd: args}]
        return kwargs

    # @classmethod
    # def _rows(cls, docstring):
    #     if not docstring:
    #         return ['']
    #     lines = docstring.expandtabs().splitlines()
    #     max_indent = sys.maxsize
    #     for line in lines:
    #         if stripped := line.strip():
    #             max_indent = min(max_indent, len(line) - len(stripped))
    #     return [line[max_indent:].strip() for line in lines] if max_indent < sys.maxsize else ['']
