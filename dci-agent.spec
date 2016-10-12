%if 0%{?fedora}
%global with_python3 1
%endif

Name:           dci-agent
Version:        0.0.VERS
Release:        1%{?dist}

Summary:        DCI Agent for DCI control server
License:        ASL 2.0
URL:            https://github.com/redhat-openstack/dci-agent

Source0:        %{name}-%{version}.tar.gz
Source1:        %{name}.service
Source2:        %{name}.timer

BuildArch:      noarch
Autoreq: 0

BuildRequires:  libffi-devel
BuildRequires:  openssl-devel
BuildRequires:  postgresql-server
BuildRequires:  python-click
BuildRequires:  python-psycopg2
BuildRequires:  python-rpm-macros
BuildRequires:  python-tripleo-helper
BuildRequires:  python2-dciclient
BuildRequires:  python2-devel
BuildRequires:  python2-rpm-macros
BuildRequires:  systemd
BuildRequires:  systemd-units
Requires:       PyYAML
Requires:       py-bcrypt
Requires:       python-click
Requires:       python-configparser
Requires:       python-prettytable
Requires:       python-requests
Requires:       python-setuptools
Requires:       python-simplejson
Requires:       python-six
Requires:       python2-dciclient

Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
DCI agent for DCI control server.

%prep
%autosetup -n %{name}-%{version}

%build
%py2_build

%install
%py2_install
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.timer

%check
%{__python2} setup.py test

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
            -c "DCI-Agent service" %{name}
exit 0

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files -n %{name}
%doc README.rst
%{python2_sitelib}/*
%{_bindir}/dci-agent
%{_unitdir}

%changelog
* Fri Aug 26 2016 Gonéri Le Bouder <goneri@redhat.com> - 0.0.1-1
- Initial release
