# ReSpeC: Reactive Specification Compiler

[![Build Status][build_img]][travis]
[![Coverage Status][coverage]][coveralls]

## About

ReSpeC (`respec`) is a Python framework for composing reactive Linear Temporal Logic (LTL) specifications for use in the synthesis of high-level robot controllers.

### What ReSpeC is NOT meant for:
- It is not an executive for high-level robot control. For that, see [`LTLMoP`](https://github.com/LTLMoP/LTLMoP), [`SMACH`](http://wiki.ros.org/smach), and [`FlexBE`](https://github.com/team-vigir/flexbe_behavior_engine).
- It is not a structured or natural language parser for robotics. For that, see [`LTLMoP`](https://github.com/LTLMoP/LTLMoP) and [`SLURP`](https://github.com/PennNLP/SLURP).
- It does not have a graphical user interface. For that, see [`LTLMoP`](https://github.com/LTLMoP/LTLMoP) and the [`FlexBE app`](https://github.com/pschillinger/flexbe_chrome_app).
- It does not synthesize a robot controller (finite-state machine). However, its output can be readily used with the [`slugs`](https://github.com/LTLMoP/slugs) GR(1) synthesizer. Also see [`gr1c`](https://github.com/slivingston/gr1c) and [`openpromela`](https://github.com/johnyf/openpromela).

### Maintainers:
- Spyros Maniatopoulos <sm2296@cornell.edu>

## Examples
coming soon!

## Publications
coming soon!

## License
[BSD-3](http://opensource.org/licenses/BSD-3-Clause) (see [`LICENSE`](https://raw.githubusercontent.com/LTLMoP/ReSpeC/master/LICENSE) file)

[build_img]: https://travis-ci.org/LTLMoP/ReSpeC.svg?branch=master
[travis]: https://travis-ci.org/LTLMoP/ReSpeC
[coverage]: https://coveralls.io/repos/LTLMoP/ReSpeC/badge.svg?branch=master
[coveralls]: https://coveralls.io/r/LTLMoP/ReSpeC?branch=master
