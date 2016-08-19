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

%description
DCI agent for DCI control server.

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  postgresql
BuildRequires:  postgresql-devel
BuildRequires:  postgresql-server
BuildRequires:  python-psycopg2
BuildRequires:  python-tox
BuildRequires:  python-requests
BuildRequires:  python-six
BuildRequires:  gcc
BuildRequires:  libffi-devel

Requires:       python-prettytable
Requires:       py-bcrypt
Requires:       python-click
Requires:       PyYAML
Requires:       python-requests
Requires:       python-simplejson
Requires:       python-six
Requires:       python-configparser
Requires:       python2-dciclient
Requires:       python2-setuptools

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
* Tue Mar 08 2016 Brad Watkins <bwatkins@redhat.com> - 0.1-1
- Add dci-feeder-github sysconfig directory

* Mon Nov 16 2015 Yanis Guenane <yguenane@redhat.com> 0.1-1
- Initial commit
