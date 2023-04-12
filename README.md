# OpenSCAP Report Generator

[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/OpenSCAP/openscap-report/badges/quality-score.png?b=main)](https://scrutinizer-ci.com/g/OpenSCAP/openscap-report/?branch=main) 
[![Build Status](https://scrutinizer-ci.com/g/OpenSCAP/openscap-report/badges/build.png?b=main)](https://scrutinizer-ci.com/g/OpenSCAP/openscap-report/build-status/main)
[![Code Coverage](https://scrutinizer-ci.com/g/OpenSCAP/openscap-report/badges/coverage.png?b=main)](https://scrutinizer-ci.com/g/OpenSCAP/openscap-report/?branch=main)
[![Code Intelligence Status](https://scrutinizer-ci.com/g/OpenSCAP/openscap-report/badges/code-intelligence.svg?b=main)](https://scrutinizer-ci.com/code-intelligence)

Tool for generating report from results of oscap scan.

## Installation

[Learn how to install tool in the documentation.](https://openscap-report.readthedocs.io/en/latest/manual/installation.html)

## Example usage

This command consumes the ARF file, which is one of the possible standardized formats for the results of SCAP-compliant scanners. You can read about generating ARF report files using OpenSCAP in the OpenSCAP User Manual. Or you can use test arf files from repository [`/tests/test_data`](https://github.com/OpenSCAP/openscap-report/tree/main/tests/test_data).

```bash
oscap-report < ssg-fedora-ds-arf.xml > report.html
```

More information about command line usage in [man page](https://openscap-report.readthedocs.io/en/latest/oscap-report.1.html) (`man oscap-report`) or on [readthedocs](https://openscap-report.readthedocs.io/en/latest/)
