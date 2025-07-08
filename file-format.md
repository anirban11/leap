# LEAP: Learn Event-recording Automata Passively

## 1. File format.

The `leap` file format describes a sample set containing a number of symbolic words with their corresponding labels -- `pos` or `neg` -- representing whether the word is accepted or rejected by the target `ERA`.

One first declares the [events](#the-event-declaration) that will be used in the symbolic words, and then declares a set [symbolic words](#the-symbolic-word-declaration) with their corresponding labels.


## The `events` declaration 

```
events:a,b,c
```
declares a set of events consisting of `a`, `b` and `c`. Only the declared events can be used in the symbolic words.
The events should be separated by a comma `,`.

## The `symbolic word` declaration

Each `symbolic word` is a sequence of `symbolic events` written in seperate lines, each line ending with a semicolon `;`. Each symbolic word is then followed by a `label`. Every labeled symbolic word is written within a pair of square brackets `[]`, again separated by a line. For example, a *positive* symbolic word `(a₁,g₁)(a₂,g₂)` can be expressed as

```
[
(a₁,g₁);
(a₂,g₂);
pos
]
```
Here, `a₁` and `a₂` are events that must have been declared in the `events` declaration, and `g₁` and `g₂` are `guards` that are [expressions](#expressions) defined below. The possible labels are defined in the [labels](#labels) section below.


### Expressions

An `expression` is a conjunction of simple expressions.
A `simple expression` compares an event-clock with a non-negative integer.
Formally, expressions are formed using the following grammar:

```
expr ::= simple_expr 
         | simple_expr && expr

simple_expr ::= true_expr
                | clock_expr < int_expr
                | clock_expr > int_expr
                | clock_expr <= int_expr
                | clock_expr >= int_expr
                | clock_expr == int_expr
                
true_expr ::= True
int_expr ::= INTEGER
clock_expr ::= event_id
```

where `event_id` is an `id` of an event that has been already declared.

**NOTE:** The syntax of expressions defined above does not allow expressions like `2<a<3`, 
however, this can be written as follows: `a>2&&a<3` that has the same semantics as above.


### Labels
- `pos`: declares a `positive` sample
- `neg`: declares a `negative` sample
