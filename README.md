# OpenSCAP Report Generator

Tool for generating report from results of oscap scan.

## Installation

### RHEL 9 / CentOS Stream 9 / Fedora 35 and later

> RHEL 9 and CentOS Stream 9 needs enable Extra Packages for Enterprise Linux (EPEL). Learn how to enable EPEL in [EPEL documentation](https://fedoraproject.org/wiki/EPEL).

```bash
sudo dnf install openscap-report
```

## Example usage

This command consumes the ARF file, which is one of the possible standardized formats for the results of SCAP-compliant scanners. You can read about generating ARF report files using OpenSCAP in the OpenSCAP User Manual. Or you can use test arf files from repository `/tests/test_data`.

```bash
oscap-report ssg-fedora-ds-arf.xml > report.html
```

More information about command line usage in man page (`man oscap-report`) or on [readthedocs](https://openscap-report.readthedocs.io/en/latest/)
