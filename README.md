# ReSpeC: Reactive Specification Compiler

[![Build Status][build_img]][travis]
[![Coverage Status][cover_img]][coveralls]
[![Documentation Status][docs_img]][docs]

## About

ReSpeC (`respec`) is a Python framework for composing reactive Linear Temporal Logic (LTL) specifications for use in the synthesis of high-level robot controllers.

ReSpeC is used as the specification compiler in [Team ViGIR](http://www.teamvigir.org/)'s [`Behavior Synthesis`](https://github.com/team-vigir/vigir_behavior_synthesis) ROS stack.

### What ReSpeC is NOT meant for:
- It is not an executive for high-level robot control. For that, see [`LTLMoP`](https://github.com/LTLMoP/LTLMoP), [`SMACH`](http://wiki.ros.org/smach), and [`FlexBE`](https://github.com/team-vigir/flexbe_behavior_engine).
- It is not a structured or natural language parser for robotics. For that, see [`LTLMoP`](https://github.com/LTLMoP/LTLMoP) and [`SLURP`](https://github.com/PennNLP/SLURP).
- It does not have a graphical user interface. For that, see [`LTLMoP`](https://github.com/LTLMoP/LTLMoP) and the [`FlexBE app`](https://github.com/pschillinger/flexbe_chrome_app).
- It does not synthesize a robot controller (finite-state machine). However, its output can be readily used with the [`slugs`](https://github.com/LTLMoP/slugs) GR(1) synthesizer. Also see [`gr1c`](https://github.com/slivingston/gr1c) and [`openpromela`](https://github.com/johnyf/openpromela).

### Maintainers:
- Spyros Maniatopoulos ([@spmaniato](https://github.com/spmaniato), sm2296@cornell.edu)

## Examples
* Run `python examples/atlas_specification.py`. You will see LTL terminal output.
* More examples of both individual formulas and full specifications coming soon!

## Documentation
[Read the Docs](http://respec.readthedocs.org/en/latest/) coming soon!

## Publications
coming soon!

## License
[BSD-3](http://opensource.org/licenses/BSD-3-Clause) (see [`LICENSE`](https://raw.githubusercontent.com/LTLMoP/ReSpeC/master/LICENSE) file)

[build_img]: https://travis-ci.org/LTLMoP/ReSpeC.svg?branch=master
[travis]: https://travis-ci.org/LTLMoP/ReSpeC
[cover_img]: https://coveralls.io/repos/LTLMoP/ReSpeC/badge.svg?branch=master&service=github
[coveralls]: https://coveralls.io/github/LTLMoP/ReSpeC?branch=master
[docs_img]: https://readthedocs.org/projects/respec/badge/?version=latest
[docs]: https://readthedocs.org/projects/respec/?badge=latest