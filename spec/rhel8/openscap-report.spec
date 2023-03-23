%global pymodule_name openscap_report

Name:           openscap-report
Version:        0.0.0
Release:        0%{?dist}
Summary:        A tool for generating human-readable reports from (SCAP) XCCDF and ARF results

# The entire source code is LGPL-2.1+ and GPL-2.0+ and MIT except schemas/ and assets/, which are Public Domain
License:        LGPLv2+ and GPLv2+ and MIT and Public Domain
URL:            https://github.com/OpenSCAP/%{name}
Source0:        https://github.com/OpenSCAP/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python38-devel
BuildRequires:  python38-rpm-macros
BuildRequires:  python3-sphinx
BuildRequires:  python3-sphinx_rtd_theme

Provides:       bundled(patternfly) = 4

Requires:       python38-lxml
Requires:       python38-jinja2

%{?python_enable_dependency_generator}

%global _description %{expand:
This package provides a command-line tool for generating
human-readable reports from SCAP XCCDF and ARF results.}

%description %_description

%prep
%autosetup -p1 -n %{name}-%{version}


%build
%py3_build
sphinx-build -b man docs _build_docs



%install
%py3_install
install -m 0644 -Dt %{buildroot}%{_mandir}/man1 _build_docs/oscap-report.1



%files -n %{name}
%{_mandir}/man1/oscap-report.*
%{_bindir}/oscap-report
%{python3_sitelib}/%{pymodule_name}/
%{python3_sitelib}/%{pymodule_name}-%{version}*
%exclude %{python3_sitelib}/tests/
%license LICENSE


%changelog
* Mon Jun 06 2022 Jan Rodak <jrodak@redhat.com> - 0.0.0-0
- Initial version of the package.
