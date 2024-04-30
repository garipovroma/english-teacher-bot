import re


class AndPatternsComparator:

    def __init__(self, *regexes: re.Pattern):
        self.regexes = regexes

    def __eq__(self, other):
        if not isinstance(other, str):
            return False

        for regex in self.regexes:
            if not regex.search(other):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f'<PatternComparator[self.regexes={self.regexes}]>'
