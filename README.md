# Chimps Compiler

**Authors:** Joshua Guzman, Allen Guevarra, Jose Bastidas
**Course:** COMP 430
**Target Language:** MIPS Assembly

---

## Overview

Chimps is a restricted, low-level programming language that compiles directly to MIPS assembly. The language is intentionally minimal, designed to explore how high-level constructs — including pointers, structs, and expressions — can be translated into assembly instructions. All memory is stack-allocated; there is no heap.

---

## Language Features

- **Integer arithmetic and relational expressions**
- **Boolean literals** (`true`, `false`)
- **Pointers** — address-of (`&`), dereference (`*`), and null
- **Structs** — user-defined record types with named fields
- **Functions** — with typed parameters and return types
- **Control flow** — `if`, `while`, `block`
- **Variable declarations** and assignments
- **Expression statements** and `println`
- **S-expression syntax** — the entire grammar is parenthesized

---

## Syntax Reference

### Types

```
type ::= int
       | void
       | structname
       | (* type)          ; pointer to type
```

### Struct Definitions

```
structdef ::= (struct structname param*)

param ::= (type var)
```

**Example:**
```
(struct Point (int x) (int y))
```

### Function Definitions

```
fdef ::= (func funcname (param*) type stmt*)
```

**Example:**
```
(func add ((int a) (int b)) int
  (return (+ a b)))
```

### Statements

| Statement | Syntax |
|-----------|--------|
| Variable declaration | `(vardec type var)` |
| Assignment | `(assign lhs exp)` |
| While loop | `(while exp stmt)` |
| If / if-else | `(if exp stmt [stmt])` |
| Return | `(return [exp])` |
| Block | `(block stmt*)` |
| Print | `(println exp)` |
| Expression statement | `(stmt exp)` |

### Left-Hand Side (Assignable Locations)

```
lhs ::= var                 ; variable
      | (. lhs var)         ; struct field access
      | (* lhs)             ; pointer dereference
```

### Expressions

```
exp ::= i                   ; integer literal
      | true | false        ; boolean literals
      | null                ; null pointer
      | lhs                 ; memory read
      | (& lhs)             ; address-of
      | (* exp)             ; dereference
      | (op exp exp)        ; binary operation
      | (call funcname exp*) ; function call
```

### Operators

| Operator | Meaning |
|----------|---------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `<` | Less than |
| `==` | Equal |
| `!=` | Not equal |

### Program Structure

```
program ::= structdef* fdef* stmt*
```

Top-level statements after all struct and function definitions serve as the program entry point.

---

## Compiler Phases

### 1. Lexer (10%)
Tokenizes the source into:
- Reserved words (`int`, `void`, `struct`, `func`, `if`, `while`, `return`, `block`, `vardec`, `assign`, `println`, `stmt`, `call`, `true`, `false`, `null`, `+`, `-`, `*`, `/`, `<`, `==`, `!=`, `&`, `.`)
- Identifiers (variable names, struct names, function names)
- Integer literals

No comment syntax is supported.

### 2. Parser (10%)
Produces an abstract syntax tree (AST) from the flat token stream. The grammar is fully parenthesized (S-expression style), making parsing straightforward and unambiguous without operator precedence rules.

### 3. Typechecker (15%)
Performs static type checking over the AST:
- Ensures operand types are compatible with operators
- Validates struct field accesses against struct definitions
- Tracks pointer types through address-of and dereference operations
- Checks function call argument counts and types against signatures
- Verifies that `null` is only assigned to pointer types
- Ensures `return` expressions match the declared function return type

### 4. Code Generator (65%)
Translates the typed AST to MIPS assembly:
- All variables are stack-allocated (no heap, no global data segment for variables)
- Arithmetic and relational expressions map to MIPS ALU instructions
- Struct layout is computed at compile time; field accesses compile to base-pointer-plus-offset loads and stores
- Pointers compile to address arithmetic on the stack frame
- Function calls follow a standard calling convention with stack frame setup and teardown
- `println` emits a MIPS syscall for integer output

---

## Memory Model

Chimps uses **stack-only allocation**. Every `vardec` reserves space on the current stack frame. Structs are laid out contiguously in memory with fields ordered as declared. Pointers hold raw stack addresses and are fully manipulable via `&` and `*`.

There is no garbage collection, no heap allocation, and no dynamic memory management.

---


## Project Structure

```
comp430/
├── README.md
├── main.py                     # Compiler entry point — chains all four phases
├── src/
│   ├── __init__.py
│   ├── lexer/
│   │   ├── __init__.py
│   │   ├── token.py            # Token dataclass and TokenType enum
│   │   └── lexer.py            # Tokenizer
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── ast_nodes.py        # AST node dataclasses (Exp, Stmt, Type, etc.)
│   │   └── parser.py           # Recursive descent parser
│   ├── typechecker/
│   │   ├── __init__.py
│   │   ├── types.py            # Type representations (IntType, PointerType, StructType...)
│   │   └── typechecker.py      # Type checking logic
│   └── codegen/
│       ├── __init__.py
│       ├── mips.py             # MIPS instruction helpers and emitter
│       └── codegen.py          # AST → MIPS assembly translation
└── tests/
    ├── test_lexer.py
    ├── test_parser.py
    ├── test_typechecker.py
    └── test_codegen.py
```

---

## Building and Running

**Requirements:** Python 3.10+

```bash
python main.py <input.chimps>
```

This will run the full compiler pipeline and produce a `<input.asm` MIPS assembly file.

**Running tests:**
```bash
python -m pytest tests/
```
