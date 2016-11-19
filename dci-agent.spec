Name:           dci-agent
Version:        0.0.VERS
Release:        1%{?dist}
Summary:        DCI Agent for DCI control server
License:        ASL 2.0
URL:            https://github.com/redhat-openstack/dci-agent
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  dci-api
BuildRequires:  postgresql-server
# pifpaf runs: pg_config --bindir
BuildRequires:  postgresql-devel
BuildRequires:  python-click
BuildRequires:  python-dciclient
BuildRequires:  python-mock
BuildRequires:  python-pifpaf
BuildRequires:  python-psycopg2
BuildRequires:  python-pytest
BuildRequires:  python-rpm-macros
BuildRequires:  python-tripleo-helper
BuildRequires:  python2-dciclient
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
Requires:       python2-tripleo-helper

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
install -p -D -m 644 dci_agent/systemd/dci-agent.service %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 644 dci_agent/systemd/dci-agent.timer %{buildroot}%{_unitdir}/%{name}.timer
install -p -D -m 644 dci_agent/dci_agent.conf %{buildroot}%{_sysconfdir}/dci/dci_agent.conf
cp -rv conf/dci_agent.conf.d %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d
chmod 755 %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d
find %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d -type f -exec chmod 644 {} \;

%check
PYTHONPATH=%{buildroot}%{python2_sitelib} \
          DCI_SETTINGS_MODULE="dci_agent.tests.settings" \
          pifpaf run postgresql -- py.test -v dci_agent/tests

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
%config(noreplace) %{_sysconfdir}/*

%changelog
* Fri Aug 26 2016 Gonéri Le Bouder <goneri@redhat.com> - 0.0.1-1
- Initial release
