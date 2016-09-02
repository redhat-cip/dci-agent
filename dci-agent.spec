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
BuildRequires:  python-rpm-macros
BuildRequires:  python2-rpm-macros
BuildRequires:  systemd
BuildRequires:  systemd-units

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
# Install systemd units

install -p -D -m 644 dci_agent/systemd/dci-agent.service %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 644 dci_agent/systemd/dci-agent.timer %{buildroot}%{_unitdir}/%{name}.service


%check
%{__python2} setup.py test

%pre common
getent group %{name} >/dev/null || groupadd -r %{service}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d %{_sharedstatedir}/%{service} -s /sbin/nologin \
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

%changelog
* Fri Aug 26 2016 Gonéri Le Bouder <goneri@redhat.com> - 0.0.1-1
- Initial release
