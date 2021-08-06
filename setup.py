
from setuptools import find_packages, setup

import oscap_report


def get_long_description():
    with open('README.md') as readme_file:
        return readme_file.read()


setup(name='oscap_report',
      version=oscap_report.__version__,
      description='Tool for generating report from results of oscap scan.',
      long_description=get_long_description(),
      long_description_content_type="text/markdown",
      url='',
      author='Jan Rodak',
      author_email='jrodak@redhat.com',
      license='',
      packages=find_packages(),
      install_requires=[],
      include_package_data=True,
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'oscap-report=oscap_report.cli:main',
          ],
      },
      python_requires='>=3.9',
      )
