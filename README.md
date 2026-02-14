# TigerC-Compiler
TigerC Compiler - In memory of Dennis Ritchie
Minimal C compiler experiment written from scratch.

## Current Features
- Tokenizer
- Expression parser
- Shunting Yard algorithm
- Bytecode evaluator

## Roadmap
- C23 keywords
- PE32+ EXE generation
- Minimal runtime


# TigerC Compiler — Educational C23 Compiler for Windows x64

## Dedication

This project is dedicated to the memory of **Dennis M. Ritchie**, the creator of the C programming language, whose work profoundly shaped modern computer science and software development.

---

## Purpose

TigerC is an educational, syntax-aware C23 compiler project designed to help programmers understand:

* how compilers work internally
* low-level programming concepts
* type systems and expression parsing
* linking and executable generation
* Windows PE (.exe / .dll) structure
* calling conventions and ABI behavior

This project is built **for learning and research purposes** — not as a production replacement for established compilers such as GCC or Clang.

---

## Historical Context

C evolved from earlier typeless languages such as **BCPL** and **B**.
The B language treated variables as machine words without explicit types, which limited safety and expressiveness.

C introduced:
* explicit data types
* structured data (`struct`)
* function prototypes
* file inclusion model
* pointer-based abstractions
* better memory control
* modular compilation

These innovations made C both close to hardware and expressive enough for large systems.

> “C is quirky, flawed, and an enormous success…”
> — Dennis M. Ritchie, *The Development of the C Language*

Source: Bell Labs paper on C language history.
---
## Project Scope
TigerC currently focuses on:
* C23 syntax awareness
* educational type system modeling
* readable internal type descriptions
  (e.g. `int (*fptr)(int)` → “pointer to function returning int taking int”)
* enhanced error reporting using type description strings
* expression parsing and precedence handling
* include guard handling
* Windows x64 PE generation
* minimal custom linker (dynamic linking only)
* .exe and .dll output support
* Windows x64 calling convention usage
* UCRT-based runtime targeting
---
## Design Philosophy
TigerC prioritizes:
* clarity over performance
* inspectable internal representations
* transparent type diagnostics
* minimal but understandable linking
* educational compiler architecture

![foto](https://github.com/user-attachments/assets/27636fd5-a1cb-48e9-8492-3e2c28403612)


