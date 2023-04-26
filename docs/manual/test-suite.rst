Test suite
==========

.. _test_suite:

The tox test suite
------------------

Install tox test suite requirements
```````````````````````````````````
Requirements are `tox`_ and `eslint`_ tools. The eslint tool is optional.
Here are commands for installation of tools:

.. code-block:: console
    
    sudo dnf install python3-tox
    
    # Optional installation of eslint
    sudo dnf install npm
    sudo npm i -g eslint

Run tox test suite
``````````````````
.. code-block:: console

    tox

The tmt test suite
------------------

Install tmt test suite requirements
```````````````````````````````````
Requirement is `tmt`_.
Here is command for installation of tool:

.. code-block:: console

    sudo dnf install tmt-all

Run tmt test suite
``````````````````
.. code-block:: console

    tmt -c distro=fedora run --all provision --how=virtual --image=fedora

.. _tmt: https://tmt.readthedocs.io/en/stable/overview.html#install
.. _tox: https://tox.wiki/en/latest/installation.html
.. _eslint: https://eslint.org/docs/latest/use/getting-started#global-install
