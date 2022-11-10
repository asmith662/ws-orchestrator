import re


class DocOpt:
    def __init__(self, option_description):
        self.data = self.parse(option_description)
        self.description = self.data['desc']
        self.arg_types = self.data['arg_types']
        self.arg_type = self.data['arg_type']
        self.arg = self.data['arg']
        self.value = None if self.data['default'] is False and self.arg else self.data['default']
        self.keys = self.data['keys']
        self.key = self.data['key']
        self.aliases = self.data['aliases']
        self.alias = self.data['alias']
        self.options = {self.key: self.arg}

    @classmethod
    def parse(cls, option_description):
        option_description = option_description.strip().split(' : ')
        opt, desc = option_description[0], option_description[1]
        arg_types = a[0][1:-1] and (opt := re.sub('[ =]<.+>', '', opt)) if (a := re.findall('<.+>', opt)) else None
        arg_type = arg_types[0] if arg_types else None
        arg = True if arg_types else False
        default = None
        if arg and (defaults := re.findall('default: ([A-Za-z0-9 ]+)', desc, flags=re.I)):
            default = defaults[0].strip()
        keys = [k for k in re.findall('--[A-Za-z0-9]+|-[A-Za-z0-9]+', opt)]
        key = keys[0] if keys else None
        aliases = [key for key in keys[1:] if len(keys) > 1]
        alias = aliases[0] if aliases else None
        return {'desc': desc, 'arg_types': arg_types, 'arg_type': arg_type, 'arg': arg, 'default': default,
                'keys': keys, 'key': key, 'aliases': aliases, 'alias': alias}

    def options(self):
        return self.options

    # @property
    # def name(self):
    #     return self.long or self.short
    #
    # def __repr__(self):
    #     return f'DocOpt(name={self.name},argcount={self.argcount},value={self.value})'


class Doc:
    """
        TO DO:
            - populate meta dict and return it along with kwargs
    """
    redir = '^(-|--)\\w+'
    sect = '(?<=\n).+(?=\n)'

    def __init__(self, docstring):
        self.docstring = docstring
        self.options = {DocOpt(o).key: DocOpt(o).arg for o in self._split(docstring) if o.startswith('-')}
        self.args = self.args(docstring)
        self.kwargs = self.kwargs(docstring)
        # self.dict = {self.args: self.kwargs}
        # print({self.args: self.kwargs})

    @classmethod
    def _split(cls, docstring):
        split = re.split(r'\n *(<\S+?>|-\S+?)', docstring)[1:]
        return [s1 + s2 for s1, s2 in zip(split[::2], split[1::2])]

    @staticmethod
    def args(docstring):
        sections = [s.strip() for s in re.findall(Doc.sect, docstring)]
        usage = [s for s in sections if re.search(r'^[U|u]sage:\s', s)][0]
        section, name, args = usage.replace('[options] ', '').split(' ', 2)
        return [a[1:-1] for a in re.findall(r'<.+>|[.+]', args)]

    @staticmethod
    def kwargs(docstring):
        sections = [s.strip() for s in re.findall(Doc.sect, docstring)]
        meta, kwargs = [], []
        for row, opt in enumerate([s for s in sections if re.search(Doc.redir, s)]):
            cmds = opt.split(' : ')
            cmd, desc = cmds[0].strip(), cmds[1]
            arg = a[0][1:-1] if (a := re.findall('<.+>', cmd)) else None
            key_type = ktype and (cmd := re.sub('-\\w+$', '', cmd)) \
                if (ktype := re.search(Doc.redir + '-', cmd)) else None
            cmd = re.sub('((\\s|=)<.+>|(\\s|=)[.+])', '', cmd)

            if re.search(Doc.redir + '\\sor\\s', cmd):
                kwargs += [{kwarg: arg} for kwarg in list(cmd.split(' or '))]
                for kwarg in list(cmd.split(' or ')):
                    kwargs += [{kwarg: arg}]
                    # meta += [{k: args, 'type': key_type, 'description': desc}]
            else:
                kwargs += [{cmd: arg}]
        return kwargs
