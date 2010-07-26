#!/usr/bin/env python
import binascii, zlib

def Compress(string):
    return binascii.b2a_base64(zlib.compress(string))[:-1]

def Decompress(string):
    return zlib.decompress(binascii.a2b_base64(string)[:-1])



class Node(list):

    def __init__(self, name=''):
        super(Node, self).__init__()
        self.name = name

    def __getitem__(self, key):
        if isinstance(key, basestring):
            for child in self:
                if isinstance(child, Node) and child.name == key:
                    if len(child) == 1:
                        return child[0]
                    else:
                        return child
            raise KeyError(key)
        else:
            return super(Node, self).__getitem__(key)

    def append(self, node):
        super(Node, self).append(node)
        return self

    def get(self, key, default=None):
        try:
            child = self[key]
            if len(child) == 1:
                return child[0]
            else:
                return child
        except KeyError:
            return default

    def get_all(self, key):
        children = Node()
        for child in self:
            if isinstance(child, Node) and child.name == key:
                children.append(child)
        return children

    def todict(self, flat=True, force=False):
        if flat:
            if len(self) == 1 and not isinstance(self[0], Node) and force == False:
                return self[0]
            else:
                result = {}
                for child in self:
                    if isinstance(child, Node):
                        result[child.name] = child.todict(flat)
                    else:
                        key = 'cdata'
                        i = 0
                        while key in result:
                            key = '_cdata%s' % i
                        result[key] = child
                return result
        else:
            L = []
            for node in self:
                if isinstance(node, Node):
                    L.append(node.todict(flat))
                else:
                    L.append(node)
            return {self.name: L}

    def __str__(self, indentlevel=0):
        indent = '\t' * indentlevel
        if not self:
            return '(%s)' % self.name
        elif len(self) == 1 and not isinstance(self[0], Node):
            return '(%s %s)' % (self.name, str(self[0]))
        else:
            children = '\n'
            for child in self:
                children += indent + '\t'
                try:
                    children += child.__str__(indentlevel + 1)
                except TypeError:
                    children += str(child)
                children += '\n'
            return '(%s %s%s)' % (self.name, children, indent)


class _Document(object):

    def __init__(self, source, decompress = False):
        super(_Document, self).__init__()
        self.__position = 0
        if isinstance(source, basestring):
            source = open(source)
        self.source = source.read()
        if decompress:
            self.source = Decompress(self.source)

    def get(self):
        self.__position += 1
        return self.source[self.__position - 1]

    def peek(self, symbol):
        return self.source[self.__position:
                           self.__position + len(symbol)] == symbol

    def __grab(self, symbols):
        locations = []
        for symbol in symbols:
            match = self.source[self.__position:].find(symbol)
            if match == -1:
                match = len(self.source)
            locations.append(match + len(symbol) - 1)
        return min(locations)

    def __grab_comment(self):
        old = self.__position
        self.__position += self.__grab(['--)']) + 1
        return self.source[old:self.__position]

    def __grab_identifier(self):
        old = self.__position
        self.__position += self.__grab(' \n\t()')
        return self.source[old:self.__position]

    def __grab_string(self):
        old = self.__position
        self.__position += self.__grab('()')
        return self.source[old:self.__position]

    def process(self):
        root = Node()
        L = [root]
        while self.__position < len(self.source):
            c = self.get()
            if c == '(':
                if self.peek('--'):
                    self.__grab_comment()
                else:
                    node = Node(self.__grab_identifier())
                    L[-1].append(node)
                    L.append(node)
            elif c == ')':
                assert len(L) > 1, \
                    'Malformed document: mismatched end parenthesis.'
                L.pop()
            elif not c.isspace():
                L[-1].append(c + self.__grab_string().rstrip())
        return root


def load(source, decompress = False):
    return _Document(source, decompress).process()
