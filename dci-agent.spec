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
Source3:        dci_agent.yaml
Source4:        dci_agent.conf.d/ansible.conf.sample
Source5:        dci_agent.conf.d/email.conf.sample
Source6:        dci_agent.conf.d/file.conf.sample
Source7:        dci_agent.conf.d/irc.conf.sample
Source8:        dci_agent.conf.d/mirror.conf.sample
Source9:        dci_agent.conf.d/tests.conf.sample
Source10:       dci_agent.conf.d/sosreport.conf.sample
Source11:       dci_agent.conf.d/tripleocollectlogs.conf.sample
Source12:       dci_agent.conf.d/certification.conf.sample
Source13:       dci_agent.conf.d/git.conf.sample

BuildArch:      noarch
Autoreq: 0

BuildRequires:  postgresql-server
BuildRequires:  python-psycopg2
BuildRequires:  python-pip
BuildRequires:  python-rpm-macros
BuildRequires:  python2-rpm-macros
BuildRequires:  systemd
BuildRequires:  systemd-units
BuildRequires:  python2-devel
BuildRequires:  libffi-devel
BuildRequires:  openssl-devel

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
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.timer

install -p -D -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/dci/dci_agent.conf
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d/ansible.conf.sample
install -p -D -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d/email.conf.sample
install -p -D -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d/file.conf.sample
install -p -D -m 644 %{SOURCE7} %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d/irc.conf.sample
install -p -D -m 644 %{SOURCE8} %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d/mirror.conf.sample
install -p -D -m 644 %{SOURCE9} %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d/tests.conf.sample
install -p -D -m 644 %{SOURCE10} %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d/sosreport.conf.sample
install -p -D -m 644 %{SOURCE11} %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d/tripleocollectlogs.conf.sample
install -p -D -m 644 %{SOURCE12} %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d/certification.conf.sample
install -p -D -m 644 %{SOURCE13} %{buildroot}%{_sysconfdir}/dci/dci_agent.conf.d/git.conf.sample

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
%config(noreplace) %{_sysconfdir}/*

%changelog
* Fri Aug 26 2016 Gonéri Le Bouder <goneri@redhat.com> - 0.0.1-1
- Initial release
