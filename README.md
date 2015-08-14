# ReSpeC [![Build Status][build_img]][travis] [![Coverage Status][cover_img]][coveralls] [![Documentation Status][docs_img]][docs]
# Reactive Specification Construction kit

## About

ReSpeC (`respec`) is a Python framework for constructing Linear Temporal Logic (LTL) formulas and composing reactive LTL specifications for use in the synthesis of high-level robot controllers (aka reactive mission plans).

ReSpeC was first used in [Team ViGIR](http://www.teamvigir.org/)'s [Behavior Synthesis](https://github.com/team-vigir/vigir_behavior_synthesis) ROS stack to generate LTL specifications for an ATLAS humanoid robot, in the context of the 2015 DARPA Robotics Challenge (DRC).

### What ReSpeC is NOT meant for:
- It is not an executive for high-level robot control. For that, see [`LTLMoP`](https://github.com/VerifiableRobotics/LTLMoP), [`SMACH`](http://wiki.ros.org/smach), and [`FlexBE`](https://github.com/team-vigir/flexbe_behavior_engine).
- It is not a structured or natural language parser for robotics. For that, see [`LTLMoP`](https://github.com/VerifiableRobotics/LTLMoP) and [`SLURP`](https://github.com/PennNLP/SLURP).
- It does not have a graphical user interface. For that, see [`LTLMoP`](https://github.com/VerifiableRobotics/LTLMoP) and the [`FlexBE app`](https://github.com/pschillinger/flexbe_chrome_app).
- It does not synthesize a robot controller (finite-state machine). However, its output can be readily used with the [`slugs`](https://github.com/VerifiableRobotics/slugs) GR(1) synthesizer. Also see [`gr1c`](https://github.com/slivingston/gr1c) and [`openpromela`](https://github.com/johnyf/openpromela).

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
[BSD-3](http://opensource.org/licenses/BSD-3-Clause) (see [`LICENSE`](https://raw.githubusercontent.com/VerifiableRobotics/ReSpeC/master/LICENSE) file)

[build_img]: https://travis-ci.org/VerifiableRobotics/ReSpeC.svg?branch=master
[travis]: https://travis-ci.org/VerifiableRobotics/ReSpeC
[cover_img]: https://coveralls.io/repos/VerifiableRobotics/ReSpeC/badge.svg?branch=master&service=github
[coveralls]: https://coveralls.io/github/VerifiableRobotics/ReSpeC?branch=master
[docs_img]: https://readthedocs.org/projects/respec/badge/?version=latest
[docs]: https://readthedocs.org/projects/respec/?badge=latest
