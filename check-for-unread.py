class CBOR:

    @staticmethod
    def _error(message):
        raise Exception(message)
    
    @staticmethod
    def _is_int(value):
        if not isinstance(value, int): CBOR._error("'int' expected")
        return value

    class _CborObject(object):
        def __init__(self):
            self._read_flag = False

        # Common methods
        def check_for_unread(self):
            self._mark_as_read(self)
            self._traverse(None)

        # Private methods
        def _mark_as_read(self, object):
            if not self._is_primitive(object):
                object._read_flag = True
            return object
        
        def _is_primitive(self, object):
            return isinstance(object, CBOR.Int) or isinstance(object, CBOR.String)

        def _traverse(self, holding_object):
            match type(self).__name__:
                case "Map":
                    for entry in self._entries: entry.value._traverse(entry.key)
                case "Array":
                    for object in self._objects: object._traverse(self)
                case "Tag":
                    self._object._traverse(self)
            if not self._read_flag:
                problem_item = type(self).__name__
                if self._is_primitive(self):
                    problem_item += " with value={}".format(
                        self.value if isinstance(self, CBOR.Int) else self.string)
                problem_item += " was not read"
                if holding_object:
                    if isinstance(holding_object, CBOR.Array):
                        holder = "Array element of type"
                    elif isinstance(holding_object, CBOR.Tag):
                        holder = "Tagged object {0} of type".format(
                            holding_object._tag_number)
                    else:
                        holder = "Map key {0} with argument".format(holding_object)
                    problem_item = holder + " " + problem_item
                CBOR._error(problem_item)

    class Map(_CborObject):
        def __init__(self):
            super().__init__()
            self._entries = list()

        def set(self, key, object):
            self._entries.append(CBOR.Map.Entry(CBOR._is_int(key), object))
            return self

        def get(self, key):
            CBOR._is_int(key)
            for entry in self._entries:
                if entry.key == key:
                    return self._mark_as_read(entry.value)
            CBOR._error("Key {0} not found".format(key))

        class Entry:
            def __init__(self, key, value):
                self.key = key
                self.value = value

    class Array(_CborObject):
        def __init__(self):
            super().__init__()
            self._objects = list()

        def add(self, object):
            self._objects.append(object)
            return self

        def get(self, index):
            return self._mark_as_read(self._objects[CBOR._is_int(index)])
                
    class Tag(_CborObject):
        def __init__(self, tag_number, object):
            super().__init__()
            self._tag_number = tag_number
            self._object = object

        def get(self):
            return self._mark_as_read(self._object)

    class String(_CborObject):
        def __init__(self, string):
            super().__init__()
            if not isinstance(string, str):
                CBOR._error("'str' type expected")
            self.string = string

        def get_string(self):
            self._read_flag = True
            return self.string
        
    class Int(_CborObject):
        def __init__(self, value):
            super().__init__()
            if not isinstance(value, int):
                CBOR._error("'int' type expected")
            self.value = value

        def get_int(self):
            self._read_flag = True
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
        assert error.find("not read") > 0
    if access:
        try:
            eval("res." + access)
            res.check_for_unread()
            assert not fail, statement
        except Exception as e:
            error = repr(e)
            # print(statement + " " + error)
            assert fail, statement
            assert error.find("not read") > 0
    if message is not None and (error.find(message) < 0):
        assert False, "not" + repr(message) + error


test("CBOR.Array()", None)
test("CBOR.Map()", None)
test("CBOR.Tag(45, CBOR.Map())", "get()")

test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Int(6)))", "get().get(1)",
     "Map key 1 with argument Int with value=6 was not read")

test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Int(6)))", "get().get(1).get_int()")
test("CBOR.Array().add(CBOR.Tag(45, CBOR.Map()))", "get(0)",
     "Tagged object 45 of type Map was not read")

test("CBOR.Array().add(CBOR.Tag(45, CBOR.Map()))", "get(0).get()")

test("CBOR.Array().add(CBOR.Tag(45, CBOR.Int(6)))", "get(0).get()",
     "Tagged object 45 of type Int with value=6 was not read")

test("CBOR.Array().add(CBOR.Tag(45, CBOR.Int(6)))", "get(0).get().get_int()")

test("CBOR.Array().add(CBOR.String('Hi!'))", "get(0)",
     "Array element of type String with value=Hi! was not read")

test("CBOR.Array().add(CBOR.Int(6))", "get(0).get_int()")

test("CBOR.Map().set(1, CBOR.Array())", None,
     "Map key 1 with argument Array was not read")

test("CBOR.Map().set(1, CBOR.Array())", "get(1)")

test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Int(6)))", "get().get(1).get_int()")

test("CBOR.Array().add(CBOR.Array())", "get(0)")

test("CBOR.Array().add(CBOR.Array())", None,
     "Array element of type Array was not read")

test("CBOR.Int(6)", "get_int()")

# a slightly more elaborate example
res = CBOR.Map().set(2, CBOR.Array()).set(1, CBOR.String("Hi!"))
res.get(2).add(CBOR.Int(700))
assert res.get(2).get(0).get_int() == 700
assert res.get(1).get_string() == "Hi!"
res.check_for_unread() # all is good
