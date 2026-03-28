# TigerC Compiler — Educational C23 Subset Compiler for Windows x64

## Dedication
This project is dedicated to the memory of **Dennis M. Ritchie**, the creator of the C programming language, whose work profoundly shaped modern computer science and software development.

## “C is quirky, flawed, and an enormous success…”
 — Dennis M. Ritchie, The Development of the C Language
   Source: Bell Labs paper on C language history.

---

## Purpose
TigerC is an educational, syntax-aware C23 compiler project designed to help programmers understand:
* how compilers work internally
* low-level programming concepts
* type systems and expression parsing
* linking and executable generation
* Windows PE (.exe / .dll) structure
* calling conventions and ABI behavior
* Windows x64 PE generation
* minimal custom linker (dynamic linking only)
* .exe and .dll output support
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

---


