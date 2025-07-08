# `LEAP`: Learning Event-recording Automata Passively

This repository implements the passive learning algorithm `LEAP` for Event-Recording Automata (ERA) that is proposed in the following paper.

> **Learning Event-recording Automata Passively** \
> Anirban Majumdar, Sayan Mukherjee, and Jean-François Raskin\
> to appear, in the proceedings of [ATVA 2025](https://conf.researchr.org/home/atva-2025/)

## 1. Dependencies

Our tool relies on the following tool:

- [Z3](https://github.com/Z3Prover/z3): we use the [Python API of Z3](https://github.com/Z3Prover/z3?tab=readme-ov-file#python) to check if a symbolic word is empty 

## 2. Downloading the tool

The source code of our tool can be downloded by cloning [this repository](https://github.com/anirban11/leap).

```
git clone https://github.com/anirban11/leap.git
```

## 3. Instructions for running the tool on an example

The directory `leap` contains all the necessary files
to execute the tool, and the directory `examples` contains a few example sample sets that can be given as input for learning ERA passively using our tool. The user needs to provide an input file containing the positive and negative samples.
This input file *must* follow the syntax described in [file-format.md](file-format.md).

One can then execute the file `main.py` (that lies inside the directory `leap`) to learn the new automaton by executing the following:

```
python3 leap/main.py --inp <filename>
```

The output of this command will be an `ERA` printed in the terminal, that is consistent with the input sample set.

It is possible to convert an input sample set into an equivalent sample set that only contains region words by using the flag `--rw`, and then providing the max-constant that will appear on the regions by using `--m`. For example,

```
python3 leap/main.py --inp <filename> --rw True --m 1
```



The tool has been tested on MacOS and Linux Fedora.


-----------------------------------------------------------------------

List of contributors (in alphabetical order) to the codebase of this tool:

- [Anirban Majumdar](https://anirban11.github.io/)
- [Sayan Mukherjee](https://mukherjee-sayan.github.io/)
