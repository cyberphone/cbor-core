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
- Strict type-checking at the API level as well as during decoding

## Current Draft

The most recent draft can be found at:
https://datatracker.ietf.org/doc/draft-rundgren-cbor-core/

## Examples

The following simple examples are supposed to give you an idea of how `CBOR::Core` is to be used.
Although the examples build on a JavaScript implementation,
other implementations are supposed to be quite similar with respect to usage.

As can be seen from the examples, there is rarely any need for developers to be experts in low-level details like CBOR serialization.

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
let map = CBOR.decode(cbor);  // cbor: from the encoding example
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

## On-line Testing

On https://cyberphone.github.io/CBOR.js/doc/playground.html you will find a simple Web application,
permitting testing the encoder, decoder, and diagnostic notation implementation.

## Deterministic Encoding

For maintaining cross-platform interoperability, `CBOR::Core` mandates
fixed (aka "deterministic") encoding of CBOR objects.

To shield developers from having to know the inner workings of deterministic encoding,
a conforming `CBOR::Core` implementation performs
all necessary transformations _automatically_.  This for example means that if the 
`set()` operations
in the [Encoding&nbsp;Example](#encoding-example) were swapped, the generated CBOR would still be the same.

## Known Compatible Implementations

|Language|URL|
|-|-|
|JDK&nbsp;21+|https://github.com/cyberphone/openkeystore|
|Android/Java|https://github.com/cyberphone/android-cbor|
|JavaScript|https://github.com/cyberphone/CBOR.js#cborjs|
|Python 3|https://github.com/cyberphone/CBOR.py#cborpy|

Updated: 2026-02-20
































