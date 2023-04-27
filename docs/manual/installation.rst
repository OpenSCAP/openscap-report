Installation
============

.. _installation:

Fedora 35 and later
-------------------

.. code-block:: console

    sudo dnf install openscap-report

Enterprise Linux (EPEL)
------------------------

.. warning:: 
    Some Enterprise Linux needs to enable Extra Packages for Enterprise Linux (EPEL).
    Learn how to enable EPEL in `EPEL documentation`_.

RHEL 9
``````
.. note:: Extra packages must be enabled

.. code-block:: console

    sudo dnf install openscap-report

CentOS Stream 9
```````````````
.. note:: Extra packages must be enabled

.. code-block:: console

    sudo dnf install openscap-report

AlmaLinux 9, Rocky Linux 9
``````````````````````````
.. note:: Extra packages must be enabled

.. code-block:: console

    sudo dnf install openscap-report

Via `PyPi`_
-----------
.. code-block:: console

    # If you want to install openscap-report to $HOME/.local/bin, you have to run the below command:
    pip3 install --user openscap-report

    # If you want to install openscap-report globally instead, you have to run the below commands as admin, e.g. on Linux:
    sudo pip3 install openscap-report

Installation from source
------------------------

Requirements:

* Python 3.8+
* `lxml`_
* `jinja2`_

.. code-block:: console

    # Get repository with code
    git clone https://github.com/OpenSCAP/openscap-report.git
    cd openscap-report

    # Install
    sudo pip3 install .

    # Alternatively, you can use this command to install the project in editable mode for developer use.
    sudo pip3 install -e .

Build documentations
--------------------

Install requirements
````````````````````

.. code-block:: console

    sudo dnf install python3-sphinx python3-sphinx_rtd_theme

Build man page
``````````````

.. code-block:: console

    cd ./docs
    sphinx-build -b man . TARGET_DIR

Build this HTML docs
````````````````````
.. note:: The files in the "modules" directory were generated using the ``sphinx-apidoc openscap_report docs/modules`` command.

.. code-block:: console

    cd ./docs
    sphinx-build . TARGET_DIR

.. _PyPi: https://pypi.org/project/openscap-report/
.. _EPEL documentation: https://fedoraproject.org/wiki/EPEL
.. _jinja2 : https://jinja.palletsprojects.com/en/3.1.x/
.. _lxml : https://lxml.de/
