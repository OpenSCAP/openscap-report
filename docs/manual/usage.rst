Usage
=====

.. _generate_report:

Generate report
---------------

This command consumes the ARF file, which is one of 
the possible standardized formats for the results of 
SCAP-compliant scanners. You can read about 
generating ARF report files using OpenSCAP in the 
OpenSCAP User Manual. Or you can use test ARF 
files from repository `/tests/test_data`.

.. code-block:: console

    oscap-report ssg-fedora-ds-arf.xml > report.html

More information about command line usage in :ref:`man page` man page.
