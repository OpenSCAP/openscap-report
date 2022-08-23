# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from setuptools import find_packages, setup


def get_long_description():
    with open("README.md", "r", encoding="utf-8") as readme_file:
        return readme_file.read()


setup(name='openscap-report',
      version='0.1.3',
      description='Tool for generating report from results of oscap scan.',
      long_description=get_long_description(),
      long_description_content_type="text/markdown",
      url='https://github.com/OpenSCAP/oscap-report',
      author='Jan Rodak',
      author_email='jrodak@redhat.com',
      license='LGPL-2.1 License',
      packages=find_packages(),
      install_requires=[
          "lxml",
          "jinja2"
      ],
      include_package_data=True,
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'oscap-report=openscap_report.cli:main',
          ],
      },
      python_requires='>=3.9',
      )
