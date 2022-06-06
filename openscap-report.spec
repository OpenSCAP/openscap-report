%global pymodule_name openscap_report

Name:           openscap-report
Version:        0.0.0
Release:        0%{?dist}
Summary:        A tool for generating human-readable reports from (SCAP) XCCDF and ARF results

# The entire source code is LGPL-2.1+ and GPL-2.0+ except schemas/ and assets/, which are Public Domain
License:        LGPLv2+ and GPLv2+ and Public Domain
URL:            https://github.com/OpenSCAP/%{name}
Source0:        %pypi_source

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-sphinx
BuildRequires:  python3-sphinx_rtd_theme

%global _description %{expand:
A tool for generating human-readable reports from SCAP XCCDF and ARF results.}

%description %_description


%prep
%autosetup -p1 -n %{name}-%{version}


%generate_buildrequires
%pyproject_buildrequires -t


%build
%pyproject_wheel
sphinx-build -b man docs _build_docs



%install
%pyproject_install
%pyproject_save_files %{pymodule_name}
install -Dt %{buildroot}%{_mandir}/man8 _build_docs/oscap-report.8


%check
%tox


%files -f %{pyproject_files}
%{_mandir}/man8/oscap-report.*
%{_bindir}/oscap-report
%exclude %{python3_sitelib}/tests/


%changelog
