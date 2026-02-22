<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/cbor-core.dark.svg">
  <img alt="CBOR is Great!" src="assets/cbor-core.svg">
</picture>

This repository contains resources associated with the `CBOR::Core` project.

## Design Rationale

The purpose of `CBOR::Core` is providing a specification that
can be implemented on quite different platforms, while still maintaining a high level of interoperability.
`CBOR::Core` has also been described as "a better JSON".

Interoperability is achieved by:
- Strict adherance to the CBOR base specification [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949.html)
- Fixed (deterministic) _encoding_ scheme, while optionally offering _decoding_ support for "legacy" CBOR systems
- A base for creating simple but powerful APIs, limiting the need for developers to be experts in low-level details like serialization

## Current Draft

The most recent draft can be found at:
https://datatracker.ietf.org/doc/draft-rundgren-cbor-core/

## Examples

The following examples are supposed to give an idea of how `CBOR::Core` is to be used.
Although the examples build a JavaScript implementation,
other implementations are supposed to be quite similar with respect to usage.

### Encoding Example

```javascript
let cbor = CBOR.Map()
               .set(CBOR.Int(1), CBOR.Float(45.7))
               .set(CBOR.Int(2), CBOR.String("Hi there!")).encode();

console.log(CBOR.toHex(cbor));
------------------------------
a201fb4046d9999999999a0269486920746865726521
```
Note: there are no requirements "chaining" objects as shown above.

### Decoding Example

```javascript
let map = CBOR.decode(cbor);
console.log(map.toString());  // Diagnostic notation
----------------------------------------------------
{
  1: 45.7,
  2: "Hi there!"
}

console.log('Value=' + map.get(CBOR.Int(1)).getFloat64());
----------------------------------------------------------
Value=45.7
```

### Diagnostic Notation Support

To simplify _logging_, _documentation_, and _debugging_, a conforming
`CBOR::Core` implementation should also include support for the
text-based CBOR-format known as "Diagnostic&nbsp;Notation".

However, diagnostic notation can also be used as _input_ for creating CBOR based _test data_ and
_configuration files_ from text:
```javascript
let cbor = CBOR.fromDiagnostic(`{
# Comments are also permitted
  1: 45.7,
  2: "Hi there!"
}`).encode();

console.log(CBOR.toHex(cbor));
------------------------------
a201fb4046d9999999999a0269486920746865726521
```

### On-line Testing

On https://cyberphone.github.io/CBOR.js/doc/playground.html you will find a simple Web application,
permitting testing the encoder, decoder, and diagnostic notation implementation.

### NPM Version

For usage with Node.js and Deno, an NPM version is available at https://npmjs.com/package/cbor-core 

### Deterministic Encoding

For maintaining cross-platform interoperability, CBOR.js implements
[Deterministic&nbsp;Encoding](https://cyberphone.github.io/CBOR.js/doc/index.html#main.deterministic).

To shield developers from having to know the inner workings of deterministic encoding, CBOR.js performs
all necessary transformations _automatically_.  This for example means that if the 
[set()](https://cyberphone.github.io/CBOR.js/doc/#cbor.map.set) operations
in the [Encoding&nbsp;Example](#encoding-example) were swapped, the generated CBOR would still be the same.

### Diagnostic Notation Support

To simplify _logging_, _documentation_, and _debugging_, CBOR.js includes support for
[Diagnostic&nbsp;Notation](https://cyberphone.github.io/CBOR.js/doc/index.html#main.diagnostic).

However, diagnostic notation can also be used as _input_ for creating CBOR based _test data_ and
_configuration files_ from text:
```python
cbor = CBOR.from_diagnostic("""{
# Comments are also permitted
  1: 45.7,
  2: "Hi there!"
}""").encode()

print(cbor.hex())
--------------------------------------------
a201fb4046d9999999999a0269486920746865726521
```
Aided by the model used for deterministic encoding, diagnostic notation becomes _bidirectional,_
while remaining faithful to the native CBOR representation.

### Other Compatible Implementations

|Language|URL|
|-|-|
|JDK&nbsp;21+|https://github.com/cyberphone/openkeystore|
|Android/Java|https://github.com/cyberphone/android-cbor|
|JavaScript|https://github.com/cyberphone/CBOR.js#cborjs|

Updated: 2026-02-20






























