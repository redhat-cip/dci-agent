#!/bin/bash
set -eux
PROJ_NAME=dci-agent
DATE=$(date +%Y%m%d%H%M)
SHA=$(git log -1 --pretty=tformat:%h)

# Configure rpmmacros to enable signing packages
#
echo '%_signature gpg' >> ~/.rpmmacros
echo '%_gpg_name Distributed-CI' >> ~/.rpmmacros

# Create the proper filesystem hierarchy to proceed with srpm creatioon
#
rm -rf ${HOME}/rpmbuild
rpmdev-setuptree
sed -i "s,version = '\(.*\)',version = '0.0.${DATE}git${SHA}'," dci_agent/__init__.py
python setup.py sdist
cp -v dist/* ${HOME}/rpmbuild/SOURCES/
cp -v dci_agent/systemd/* ${HOME}/rpmbuild/SOURCES/
cp -v conf/dci_agent.conf ${HOME}/rpmbuild/SOURCES/
cp -v conf/dci_agent.conf.d/* ${HOME}/rpmbuild/SOURCES/
sed "s/VERS/${DATE}git${SHA}/g" ${PROJ_NAME}.spec > ${HOME}/rpmbuild/SPECS/${PROJ_NAME}.spec

rpmbuild -bs ${HOME}/rpmbuild/SPECS/${PROJ_NAME}.spec

# Build the RPMs in a clean chroot environment with mock to detect missing
# BuildRequires lines.
for arch in fedora-23-x86_64 fedora-24-x86_64 epel-7-x86_64; do
    rpath=$(echo ${arch}|sed s,-,/,g|sed 's,epel,el,')

    # NOTE(spredzy): Include the dci repo in mock env
    mkdir -p ${HOME}/.mock development
    # NOTE(Gonéri): We ignore the last """ from the last line to be able to concat
    # our stuff
    head -n -1 /etc/mock/${arch}.cfg > ${HOME}/.mock/${arch}-with-dci-repo.cfg
    cat <<EOF >> ${HOME}/.mock/${arch}-with-dci-repo.cfg
[dci-devel]
name="Distributed CI - Devel - CentOS 7"
baseurl=http://packages.distributed-ci.io/repos/development/el/7/x86_64/
gpgcheck=0
enabled=1

[dci-extras]
name="Distributed CI - No upstream package - CentOS 7"
baseurl=http://packages.distributed-ci.io/repos/extras/el/7/x86_64/
gpgcheck=0
enabled=1
"""
# NOTE(spredzy) Add signing options
#
config_opts['plugin_conf']['sign_enable'] = True
config_opts['plugin_conf']['sign_opts'] = {}
config_opts['plugin_conf']['sign_opts']['cmd'] = 'rpmsign'
config_opts['plugin_conf']['sign_opts']['opts'] = '--addsign %(rpms)s'
EOF
    mock -r ${HOME}/.mock/${arch}-with-dci-repo.cfg --no-clean --rebuild --resultdir=development/${rpath} ${HOME}/rpmbuild/SRPMS/${PROJ_NAME}*
done
