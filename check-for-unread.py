class CBOR:

    @staticmethod
    def _error(message):
        raise Exception(message)
    
    @staticmethod
    def _is_int(value):
        if not isinstance(value, int): CBOR._error("'int' expected")
        return value

    class CborObject:

        def __init__(self):
            self.read_flag = False

        def read_primitive(self):
            if not self._is_primitive():
                CBOR._error("Unexpected: {0}".format(type(self).__name__))
            self.read_flag = True
            return self.value

        def check_for_unread(self):
            self._traverse(None)

        def _conditionally_read(self, object):
            if not object._is_primitive(): object.read_flag = True
            return object

        def _traverse(self, parent):
            match type(self).__name__:
                case "Map":
                    for entry in self.entries: entry.value._traverse(self)
                case "Array":
                    for element in self.elements: element._traverse(self)
                case "Tag":
                    self.object._traverse(self)

            if not self.read_flag and (self._is_primitive() or parent is not None):
                culprit = "Object '{0}' not read".format(type(self).__name__)
                if self._is_primitive():
                    culprit += ", value='{0}'".format(self.value)
                if parent:
                    culprit += ", holder='{0}'".format(type(parent).__name__)
                CBOR._error(culprit)

        def _is_primitive(self):
            return isinstance(self, CBOR.Primitive)

    class Map(CborObject):
        def __init__(self):
            super().__init__()
            self.entries = list()

        def set(self, key, object):
            self.entries.append(CBOR.Map.Entry(CBOR._is_int(key), object))
            return self

        def get(self, key):
            CBOR._is_int(key)
            for i in self.entries:
                if i.key == key:
                    return self._conditionally_read(i.value)

        class Entry:
            def __init__(self, key, value):
                self.key = key
                self.value = value

    class Array(CborObject):
        def __init__(self):
            super().__init__()
            self.elements = list()

        def add(self, object):
            self.elements.append(object)
            return self

        def get(self, index):
            return self._conditionally_read(self.elements[CBOR._is_int(index)])
                
    class Tag(CborObject):
        def __init__(self, tag_number, object):
            super().__init__()
            self.tag_number = tag_number
            self.object = object

        def get(self):
            return self._conditionally_read(self.object)

    class Primitive(CborObject):
        def __init__(self, value):
            super().__init__()
            if not (isinstance(value, int) or isinstance(value, str)):
                CBOR._error("'int' or 'str' primitive expected")
            self.value = value


def test(statement, access, ok=False):
    res = eval(statement)
    try:
        res.check_for_unread()
        assert access is None and ok
    except Exception as e:
        assert access or not ok
        assert repr(e).find("never read") < 0
    if access:
        try:
            eval("res." + access)
            res.check_for_unread()
            assert ok
        except Exception as e:
            assert not ok
            assert repr(e).find("never read") < 0

test("CBOR.Array()", None, True)
test("CBOR.Map()", None, True)
test("CBOR.Tag(45, CBOR.Map())", "get()", True)
test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Primitive(6)))", "get().get(1)", False)
test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Primitive(6)))", "get().get(1).read_primitive()", True)
test("CBOR.Array().add(CBOR.Tag(45, CBOR.Map()))", "get(0)", False)
test("CBOR.Array().add(CBOR.Tag(45, CBOR.Map()))", "get(0).get()", True)
test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Primitive(6)))", "get().get(1).read_primitive()", True)
test("CBOR.Array().add(CBOR.Array())", "get(0)", True)
test("CBOR.Array().add(CBOR.Array())", None, False)
test("CBOR.Primitive(6)", "read_primitive()", True)

res = CBOR.Map().set(2, CBOR.Array()).set(1, CBOR.Primitive("Hi!"))
res.get(2).add(CBOR.Primitive(700))
res.get(1)
assert res.get(2).get(0).read_primitive() == 700
assert res.get(1).read_primitive() == "Hi!"
res.check_for_unread()
