class Node(object):
    pass

class DataNode(object):
    def __init__(self, name):
        self.name = name
        self.children = []

    def toString(self, indent = 0):
        i = '\t' * indent

        if len(self.children) == 0:
            children = ''
        elif len(self.children) == 1:
            c = self.children[0]
            if isinstance(c, DataNode):
                children = c.toString(indent + 1)
            else:
                children = str(c)
        else:
            children = '\n'
            for child in self.children:
                children += i + '\t'

                if isinstance(child, DataNode):
                    children += child.toString(indent+1)
                else:
                    children += str(child)

                children += '\n'

        return '(' + self.name + ' ' + children + i + ')'

    def addChild(self, child):
        self.children.append(child)
        return self

def _grabIdentifier(src, start):
    end = start
    while end < len(src):
        if src[end] in ' \n\t()':
            return end
        else:
            end += 1
    return len(src)

def _grabString(src, start):
    end = start
    while end < len(src):
        if src[end] not in '()':
            end += 1
        else:
            return end
    return len(src)

def readDocument(src):
    src = src.read()

    rootNode = DataNode('root')
    docStack = [ rootNode ]

    i = 0
    while i < len(src):
        assert len(docStack) > 0

        c = src[i]
        i += 1

        if c.isspace():
            continue

        elif c == '(':
            end = _grabIdentifier(src, i)
            newNode = DataNode(src[i:end])
            i = end
            docStack[-1].addChild(newNode)
            docStack.append(newNode)

        elif c == ')':
            if len(docStack) < 2:
                raise 'Malformed markup document: mismatched end parenth.'

            docStack.pop()

        else:
            end = _grabString(src, i)
            docStack[-1].addChild(c + src[i:end])
            i = end

    return rootNode

if __name__ == '__main__':
    if 1:
        foo = readDocument(file('town.ika-map'))
        print foo.toString()
    else:
        foo = (DataNode('test1')
                    .addChild(DataNode('test2')
                        .addChild('wee'))
                    .addChild('test3')
                    .addChild(DataNode('position')
                        .addChild('10')
                        .addChild('52')))

        print foo.toString()
