%if 0%{?fedora}
%global with_python3 1
%endif

Name:           dci-agent
Version:        0.0.VERS
Release:        1%{?dist}

Summary:        DCI Agent for DCI control server
License:        ASL 2.0
URL:            https://github.com/redhat-openstack/dci-agent

Source0:        dci-agent-%{version}.tar.gz

BuildArch:      noarch
Autoreq: 0

BuildRequires:  postgresql-server
BuildRequires:  python-psycopg2
BuildRequires:  python-pip

Requires:       python-prettytable
Requires:       py-bcrypt
Requires:       python-click
Requires:       PyYAML
Requires:       python-requests
Requires:       python-simplejson
Requires:       python-six
Requires:       python-configparser
Requires:       python2-dciclient
Requires:       python-setuptools
Requires:       python-tripleo-helper

%description
DCI agent for DCI control server.

%prep
%autosetup -n %{name}-%{version}

%build
%py2_build

%install
%py2_install

%check
%{__python2} setup.py test

%files -n %{name}
%doc README.rst
%{python2_sitelib}/*
%{_bindir}/dci-agent

%changelog
* Fri Aug 26 2016 Gonéri Le Bouder <goneri@redhat.com> - 0.0.1-1
- Initial release
