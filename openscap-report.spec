Name:           openscap-report
Version:        0.0.0
Release:        0%{?dist}
Summary:        A tool for generating human-readable reports from (SCAP) XCCDF and ARF results

License:        LGPL-2.1
URL:            https://github.com/OpenSCAP/oscap-report
Source0:        https://github.com/OpenSCAP/oscap-report/releases/download/%{version}/oscap-report-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
A tool for generating human-readable reports from (SCAP) XCCDF and ARF results.}

%description %_description

Summary:        %{summary}


%prep
%autosetup -p1 -n openscap-report-%{version}


%generate_buildrequires
%pyproject_buildrequires -t


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files oscap_report


%check
%tox


%files -f %{pyproject_files}
%doc README.md
%{_bindir}/oscap-report
%exclude %{python3_sitelib}/tests/


%changelog

