class CBOR {

    static #error(message) {
        throw new Error(message);
    }
    
    static #isInt(value) {
        if (!Number.isSafeInteger(value)) CBOR.#error("'integer' expected");
        return value;
    }

    static #typeCheck(object, expected) {
        if (typeof object == expected) {
            return object;
        }
        CBOR.#error("'" + expected + "' expected ");
    }

    static CborObject = class {
        constructor() {
            this._readFlag = false;
        }

        // Common methods
        checkForUnread() {
            this._markAsRead(this);
            this.#traverse(null);
        }

        // Private methods
        _markAsRead(object) {
            if (!this._is_primitive(object)) {
                object._readFlag = true;
            }
            return object;
        }

        _is_primitive(object) {
            return object instanceof CBOR.Int || object instanceof CBOR.String;
        }

        #traverse(holding_object) {
            switch (this.constructor.name) {
                case "Map":
                    this._entries.forEach(entry => {
                        entry.value.#traverse(entry.key);
                    });
                    break;
                case "Array":
                    this._objects.forEach(object => {
                         object.#traverse(this);
                    });
                    break;
                case "Tag":
                    this._object.#traverse(this);
                    break;
            }
            if (!this._readFlag) {
                let problem_item = this.constructor.name;
                if (this._is_primitive(this)) { 
                    problem_item += " with value=" + this.value;
                }
                problem_item += " was never read";
                let holder;
                if (holding_object) {
                    if (holding_object instanceof CBOR.Array) {
                        holder = "Array element of type";
                    } else if (holding_object instanceof CBOR.Tag) {
                        holder = "Tagged object " + holding_object._tag_number + " of type";
                    } else {
                        holder = "Map key " + holding_object + " with argument";
                    }
                    problem_item = holder + " " + problem_item;
                }
                CBOR.#error(problem_item);
            }
        }
    }

    static Map = class extends CBOR.CborObject {
        constructor() {
            super();
            this._entries = [];
        }

        set(key, value) {
            this._entries.push(new CBOR.Map.Entry(CBOR.#isInt(key), value));
            return this;
        }

        get(key) {
            CBOR.#isInt(key);
            for (let i = 0; i < this._entries.length; i++) {
                if (this._entries[i].key == key) {
                    return this._markAsRead(this._entries[i].value);
                }
            }
            CBOR.#error("Key " + key + " not found");
        }

        static Entry = class {
            constructor(key, value) {
                this.key = key;
                this.value = value;
            }
        }
    }

    static Array = class extends CBOR.CborObject {
        constructor() {
            super();
            this._objects = [];
        }

        add(object) {
            this._objects.push(object);
            return this;
        }

        get(index) {
            return this._markAsRead(this._objects[CBOR.#isInt(index)]);
        }
    }
                
    static Tag = class extends CBOR.CborObject {
        constructor(tag_number, object) {
            super();
            this._tag_number = tag_number;
            this._object = object;
        }

        get() {
            return this._markAsRead(this._object);
        }
    }

    static String = class extends CBOR.CborObject {
        constructor(string) {
            super();
            this.string = CBOR.#typeCheck(string, "string");
        }

        getString() {
            this._readFlag = true;
            return this.string;
        }
    }
        
    static Int = class extends CBOR.CborObject {
        constructor(value) {
            super();
            this.value = CBOR.#isInt(value);
        }

        getInt() {
            this._readFlag = true;
            return this.value;
        }
    }

    // The Proxy concept enables checks for invocation by "new" and number of arguments.
    static #handler = class {

        constructor(numberOfArguments) {
            this.numberOfArguments = numberOfArguments;
        }

        apply(target, thisArg, argumentsList) {
            if (argumentsList.length != this.numberOfArguments) {
                CBOR.#error("CBOR." + target.name + " expects " + 
                    this.numberOfArguments + " argument(s)");
            }
            return new target(...argumentsList);
        }

        construct(target, args) {
            CBOR.#error("CBOR." + target.name + " does not permit \"new\"");
        }
    }

    static Array = new Proxy(CBOR.Array, new CBOR.#handler(0));
    static Map = new Proxy(CBOR.Map, new CBOR.#handler(0));
    static Tag = new Proxy(CBOR.Tag, new CBOR.#handler(2));
    static Int = new Proxy(CBOR.Int, new CBOR.#handler(1));
    static String = new Proxy(CBOR.String, new CBOR.#handler(1));
}

//////////////////////////////
//          TEST            //
//////////////////////////////

function assertTrue(expression, explanation) {
    if (!expression) {
        throw new Error(explanation);
    }
}

function test(statement, access, message) {
    // console.log(":" + statement);
    let fail = message != null;
    let error = "";
    let res = eval(statement);
    try {
        res.checkForUnread();
        assertTrue(!access && !fail, statement);
    } catch (e) {
        error = e.toString();
        // console.log(statement + " " + error);
        assertTrue(access || fail, statement);
        assertTrue(error.includes("never read"));
    }
    if (access) {
        try {
            eval("res." + access)
            res.checkForUnread();
            assertTrue(!fail, statement);
        } catch (e) {
            error = e.toString();
            // console.log(statement + " " + error)
            assertTrue(fail, statement);
            assertTrue(error.includes("never read"));
        }
    }
    if (!message && error.includes(message)) {
        assertTrue(false, "not" + message + error);
    }
}

test("CBOR.Array()", null)
test("CBOR.Map()", null)
test("CBOR.Tag(45, CBOR.Map())", "get()")

test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Int(6)))", "get().get(1)",
     "Map key 1 with argument Int with value=6 was never read")

test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Int(6)))", "get().get(1).getInt()")
test("CBOR.Array().add(CBOR.Tag(45, CBOR.Map()))", "get(0)",
     "Tagged object 45 of type Map was never read")

test("CBOR.Array().add(CBOR.Tag(45, CBOR.Map()))", "get(0).get()")

test("CBOR.Array().add(CBOR.Tag(45, CBOR.Int(6)))", "get(0).get()",
     "Tagged object 45 of type Int with value=6 was never read")

test("CBOR.Array().add(CBOR.Tag(45, CBOR.Int(6)))", "get(0).get().getInt()")

test("CBOR.Array().add(CBOR.String('Hi!'))", "get(0)",
     "Array element of type String with value=Hi! was never read")

test("CBOR.Array().add(CBOR.Int(6))", "get(0).getInt()")

test("CBOR.Map().set(1, CBOR.Array())", null,
     "Map key 1 with argument Array was never read")

test("CBOR.Map().set(1, CBOR.Array())", "get(1)")

test("CBOR.Tag(45, CBOR.Map().set(1, CBOR.Int(6)))", "get().get(1).getInt()")

test("CBOR.Array().add(CBOR.Array())", "get(0)")

test("CBOR.Array().add(CBOR.Array())", null,
     "Array element of type Array was never read")

test("CBOR.Int(6)", "getInt()")

// a slightly more elaborate example
res = CBOR.Map().set(2, CBOR.Array()).set(1, CBOR.String("Hi!"))
res.get(2).add(CBOR.Int(700))
assertTrue(res.get(2).get(0).getInt() == 700)
assertTrue(res.get(1).getString() == "Hi!")
res.checkForUnread() // all is good
