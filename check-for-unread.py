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
        def check_for_unread(self):
            self._mark_as_read(self)
            self._traverse(None)

        # Constructor
        def __init__(self):
            self.read_flag = False

        # Private methods
        def _mark_as_read(self, object):
            if not isinstance(object, CBOR.Primitive):
                object.read_flag = True
            return object

        def _traverse(self, holding_object):
            match type(self).__name__:
                case "Map":
                    for entry in self.entries: entry.value._traverse(entry.key)
                case "Array":
                    for element in self.elements: element._traverse(self)
                case "Tag":
                    self.object._traverse(self)
            if not self.read_flag:
                primitive = type(self).__name__
                if isinstance(self, CBOR.Primitive):
                    primitive += " with value={}".format(self.value)
                primitive += " was not read"
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
                    return self._mark_as_read(i.value)

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
            return self._mark_as_read(self.elements[CBOR._is_int(index)])
                
    class Tag(CborObject):
        def __init__(self, tag_number, object):
            super().__init__()
            self.tag_number = tag_number
            self.object = object

        def get(self):
            return self._mark_as_read(self.object)

    # Only int and tstr
    class Primitive(CborObject):
        def __init__(self, value):
            super().__init__()
            if not (isinstance(value, int) or isinstance(value, str)):
                CBOR._error("'int' or 'str' primitive expected")
            self.value = value

        def read_primitive(self):
            self.read_flag = True
            return self.value



def test(statement, access, message=None):
    # print(":" + statement)
    fail = message is not None
    error = ""
    res = eval(statement)
    try:
        res.check_for_unread()
        assert access is None and not fail, statement
    except Exception as e:
        error = repr(e)
        # print(statement + " " + error)
        assert access or fail, statement
        assert error.find("never read") < 0
    if access:
        try:
            eval("res." + access)
            res.check_for_unread()
            assert not fail, statement
        except Exception as e:
            error = repr(e)
            # print(statement + " " + error)
            assert fail, statement
            assert error.find("never read") < 0
    if message is not None and (error.find(message) < 0):
        assert False, "not" + repr(message) + error


test("CBOR.Array()", None)
test("CBOR.Map()", None)
test("CBOR.Tag(45, CBOR.Map())", "get()")

test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Primitive(6)))", "get().get(1)",
     'Map key 1 with argument Primitive with value=6 was not read')

test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Primitive(6)))", "get().get(1).read_primitive()")
test("CBOR.Array().add(CBOR.Tag(45, CBOR.Map()))", "get(0)",
     'Tagged object 45 of type Map was not read')

test("CBOR.Array().add(CBOR.Tag(45, CBOR.Map()))", "get(0).get()")

test("CBOR.Array().add(CBOR.Tag(45, CBOR.Primitive(6)))", "get(0).get()",
     'Tagged object 45 of type Primitive with value=6 was not read')

test("CBOR.Array().add(CBOR.Tag(45, CBOR.Primitive(6)))", "get(0).get().read_primitive()")

test("CBOR.Array().add(CBOR.Primitive(6))", "get(0)",
     'Array element of type Primitive with value=6 was not read')

test("CBOR.Array().add(CBOR.Primitive(6))", "get(0).read_primitive()")

test("CBOR.Map().set(1, CBOR.Array())", None,
     'Map key 1 with argument Array was not read')

test("CBOR.Map().set(1, CBOR.Array())", "get(1)")

test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Primitive(6)))", "get().get(1).read_primitive()")

test("CBOR.Array().add(CBOR.Array())", "get(0)")

test("CBOR.Array().add(CBOR.Array())", None,
     'Array element of type Array was not read')

test("CBOR.Primitive(6)", "read_primitive()")

# a slightly more elaborate example
res = CBOR.Map().set(2, CBOR.Array()).set(1, CBOR.Primitive("Hi!"))
res.get(2).add(CBOR.Primitive(700))
assert res.get(2).get(0).read_primitive() == 700
assert res.get(1).read_primitive() == "Hi!"
res.check_for_unread() # all is good
