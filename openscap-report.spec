%global pymodule_name openscap_report

Name:           openscap-report
Version:        0.0.0
Release:        0%{?dist}
Summary:        A tool for generating human-readable reports from (SCAP) XCCDF and ARF results

# The entire source code is LGPL-2.1+ and GPL-2.0+ and MIT except schemas/ and assets/, which are Public Domain
License:        LGPLv2+ and GPLv2+ and MIT and Public Domain
URL:            https://github.com/OpenSCAP/%{name}
Source0:        https://github.com/OpenSCAP/%{name}/releases/download/v%{version}/%{pymodule_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-pytest
BuildRequires:  python3-sphinx
BuildRequires:  python3-sphinx_rtd_theme

Provides:       bundled(patternfly) = 4

Requires:       python3-lxml
Recommends:     redhat-display-fonts
Recommends:     redhat-text-fonts

%global _description %{expand:
This package provides a command-line tool for generating
human-readable reports from SCAP XCCDF and ARF results.}

%description %_description


%prep
%autosetup -p1 -n %{name}-%{version}


%generate_buildrequires
%pyproject_buildrequires
# test requirement listed only in tox.ini
echo "%{py3_dist jsonschema}"


%build
%pyproject_wheel
sphinx-build -b man docs _build_docs



%install
%pyproject_install
%pyproject_save_files %{pymodule_name}
install -m 0644 -Dt %{buildroot}%{_mandir}/man1 _build_docs/oscap-report.1


%check
# test_store_file fails with FileNotFoundError: [Errno 2] No such file or directory: '/tmp/oscap-report-tests_result.html'
%pytest -k "not test_store_file"

%files -f %{pyproject_files}
%{_mandir}/man1/oscap-report.*
%{_bindir}/oscap-report
%exclude %{python3_sitelib}/tests/
%license LICENSE


%changelog
* Mon Jun 06 2022 Jan Rodak <jrodak@redhat.com> - 0.0.0-0
- Initial version of the package.
