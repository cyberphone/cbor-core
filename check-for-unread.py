class CBOR:

    @staticmethod
    def _error(message):
        raise Exception(message)
    
    @staticmethod
    def _is_int(value):
        if not isinstance(value, int): CBOR._error("'int' expected")
        return value

    class CborObject(object):

        # Public methods
        def read_primitive(self):
            if not isinstance(self, CBOR.Primitive):
                CBOR._error("Unexpected: {0}".format(type(self).__name__))
            self.read_flag = True
            return self.value

        def check_for_unread(self):
            self._traverse(None if isinstance(self, CBOR.Primitive) else self)

        # Constructor
        def __init__(self, read_flag=True):
            self.read_flag = read_flag

        # Private methods
        def _traverse(self, holding_object):
            match type(self).__name__:
                case "Map":
                    for entry in self.entries: entry.value._traverse(entry.key)
                case "Array":
                    for element in self.elements: element._traverse(self)
                case "Tag":
                    self.object._traverse(self)
            if not self.read_flag:
                primitive = "{0} with value={1}, was not read" \
                            .format(type(self).__name__, self.value)
                if holding_object:
                    if isinstance(holding_object, CBOR.Array):
                        holder = "Array element of type"
                    elif isinstance(holding_object, CBOR.Tag):
                        holder = "Tagged object {0} of type".format(
                            holding_object.tag_number)
                    else:
                        holder = "Map key {0} with argument".format(holding_object)
                    primitive = holder + " " + primitive
                CBOR._error(primitive)

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
                    return i.value

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
            return self.elements[CBOR._is_int(index)]
                
    class Tag(CborObject):
        def __init__(self, tag_number, object):
            super().__init__()
            self.tag_number = tag_number
            self.object = object

        def get(self):
            return self.object

    # Only int and tstr
    class Primitive(CborObject):
        def __init__(self, value):
            super().__init__(False)
            if not (isinstance(value, int) or isinstance(value, str)):
                CBOR._error("'int' or 'str' primitive expected")
            self.value = value


def test(statement, access, ok):
    res = eval(statement)
    try:
        res.check_for_unread()
        assert access is None and ok, statement
    except Exception as e:
        # print(statement + " " + repr(e))
        assert access or not ok, statement
        assert repr(e).find("never read") < 0
    if access:
        try:
            eval("res." + access)
            res.check_for_unread()
            assert ok, statement
        except Exception as e:
            # print(statement + " " + repr(e))
            assert not ok, statement
            assert repr(e).find("never read") < 0

test("CBOR.Array()", None, True)
test("CBOR.Map()", None, True)
test("CBOR.Tag(45, CBOR.Map())", "get()", True)
test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Primitive(6)))", "get().get(1)", False)
test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Primitive(6)))", "get().get(1).read_primitive()", True)
test("CBOR.Array().add(CBOR.Tag(45, CBOR.Map()))", "get(0)", False)
test("CBOR.Array().add(CBOR.Tag(45, CBOR.Map()))", "get(0).get()", True)
test("CBOR.Array().add(CBOR.Tag(45, CBOR.Primitive(6)))", "get(0).get()", False)
test("CBOR.Array().add(CBOR.Tag(45, CBOR.Primitive(6)))", "get(0).get().read_primitive()", True)
test("CBOR.Array().add(CBOR.Primitive(6))", "get(0)", False)
test("CBOR.Array().add(CBOR.Primitive(6))", "get(0).read_primitive()", True)
test("CBOR.Map().set(1, CBOR.Array())", None, False)
test("CBOR.Map().set(1, CBOR.Array())", "get(1)", True)
test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Primitive(6)))", "get().get(1).read_primitive()", True)
test("CBOR.Array().add(CBOR.Array())", "get(0)", True)
test("CBOR.Array().add(CBOR.Array())", None, False)
test("CBOR.Primitive(6)", "read_primitive()", True)

# a slightly more elaborate example
res = CBOR.Map().set(2, CBOR.Array()).set(1, CBOR.Primitive("Hi!"))
res.get(2).add(CBOR.Primitive(700))
assert res.get(2).get(0).read_primitive() == 700
assert res.get(1).read_primitive() == "Hi!"
res.check_for_unread() # all is good
