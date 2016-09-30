
Name:           dciagent
Version:        0.0.VERS
Release:        1%{?dist}

Summary:        DCI agent
License:        ASL 2.0
URL:            https://github.com/Spredzy/agent2

Source0:        dciagent-%{version}.tgz
Source1:        dci_agent.conf
Source2:        dci_agent.conf.d/ansible.conf.sample
Source3:        dci_agent.conf.d/email.conf.sample
Source4:        dci_agent.conf.d/file.conf.sample
Source5:        dci_agent.conf.d/irc.conf.sample
Source6:        dci_agent.conf.d/mirror.conf.sample
Source7:        dci_agent.conf.d/tests.conf.sample

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-tox
BuildRequires:  python-requests
BuildRequires:  libffi-devel

Requires:       ansible
Requires:       python-click
Requires:       python-requests
Requires:       python-dciclient
Requires:       python-jinja2
Requires:       PyYAML


%description
DCI agent

%prep -a
%setup -qc

%build
%py2_build

%install
%py2_install

mkdir -p %{buildroot}%{_sysconfdir}/dci_agent.conf.d

install -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}
install -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/dci_agent.conf.d/
install -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/dci_agent.conf.d/
install -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/dci_agent.conf.d/
install -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/dci_agent.conf.d/
install -m 0644 %{SOURCE6} %{buildroot}%{_sysconfdir}/dci_agent.conf.d/
install -m 0644 %{SOURCE7} %{buildroot}%{_sysconfdir}/dci_agent.conf.d/

%check

%files
%doc
%{python2_sitelib}/*
%config(noreplace) %{_sysconfdir}/*
%{_bindir}/dci-agent


%changelog
* Tue Sep 06 2016 Yanis Guenane <yguenane@redhat.com> 0.1-1
- Initial commit
