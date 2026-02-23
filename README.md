<a id="main"></a>
&nbsp;

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/cbor-core.dark.svg">
  <img alt="CBOR is Great!" src="assets/cbor-core.svg">
</picture>

This repository contains resources associated with the `CBOR::Core` project.

## Design Rationale

The purpose of `CBOR::Core` is providing a specification that
can be supported by quite different platforms, while maintaining a high level of interoperability,
including with respect to API.
`CBOR::Core` has also been described as "a better JSON" 😊

Interoperability is achieved by:
- Compatibility with the CBOR base specification: [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949.html)
- Deterministic _encoding_, while optionally offering _decoding_ support for "legacy" CBOR
- Strict _type-checking_ at the API level as well as by the decoding process

## Current Draft

The most recent draft can be found at:
https://datatracker.ietf.org/doc/draft-rundgren-cbor-core/

## Examples

The following _simple_ examples are supposed to give an idea of how `CBOR::Core` is to be used.
Although the examples build on a JavaScript implementation,
other implementations are supposed to be quite similar with respect to usage.

### Encoding

```javascript
const TEMPERATURE_KEY = CBOR.Int(1);
const GREETINGS_KEY = CBOR.Int(2);

let cbor = CBOR.Map()
               .set(TEMPERATURE_KEY, CBOR.Float(45.7))
               .set(GREETINGS_KEY, CBOR.String("Hi there!")).encode();

console.log(CBOR.toHex(cbor));
------------------------------
a201fb4046d9999999999a0269486920746865726521
```
Note: there are no requirements "chaining" objects like above.

### Decoding

```javascript
let map = CBOR.decode(cbor);  // cbor: from the encoding example
console.log(map.toString());  // Diagnostic notation
----------------------------------------------------
{
  1: 45.7,
  2: "Hi there!"
}

console.log('Value=' + map.get(TEMPERATURE_KEY).getFloat64());
--------------------------------------------------------------
Value=45.7
```

### Using Diagnostic Notation

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

## On-line Testing

On https://cyberphone.github.io/cbor-core/playground/ you will find a simple Web application,
permitting testing a conformant encoder, decoder, and diagnostic notation implementation.

## Deterministic Encoding

For maintaining cross-platform interoperability, `CBOR::Core` mandates
a fixed (aka "deterministic") encoding of CBOR objects.

To shield developers from having to know the inner workings of deterministic encoding,
conforming `CBOR::Core` implementations perform
all necessary transformations _automagically_.  This for example means that if the 
`set()` operations
in the [Encoding&nbsp;Example](#encoding) were swapped, the generated CBOR would remain the same.

## Known CBOR::Core Implementations

|Language|URL|
|-|-|
|JDK&nbsp;21+|https://github.com/cyberphone/openkeystore|
|Android/Java|https://github.com/cyberphone/android-cbor|
|JavaScript|https://github.com/cyberphone/CBOR.js#cborjs|
|Python 3|https://github.com/cyberphone/CBOR.py#cborpy|

Updated: 2026-02-22









































