#!/bin/bash
set -eux
PROJ_NAME=dci-agent
DATE=$(date +%Y%m%d%H%M)
SHA=$(git rev-parse HEAD | cut -c1-8)

# Create the proper filesystem hierarchy to proceed with srpm creatioon
#
rm -rf ${HOME}/rpmbuild
mock --clean
rpmdev-setuptree
cp ${PROJ_NAME}.spec ${HOME}/rpmbuild/SPECS/
git archive HEAD --format=tgz --output=${HOME}/rpmbuild/SOURCES/${PROJ_NAME}-0.0.${DATE}git${SHA}.tgz
cp  conf/dci_agent.conf ${HOME}/rpmbuild/SOURCES/
cp  conf/dci_agent.conf.d/* ${HOME}/rpmbuild/SOURCES/
sed -i "s/VERS/${DATE}git${SHA}/g" ${HOME}/rpmbuild/SPECS/${PROJ_NAME}.spec
rpmbuild -bs ${HOME}/rpmbuild/SPECS/${PROJ_NAME}.spec

for arch in fedora-23-x86_64 fedora-24-x86_64 epel-7-x86_64; do
    rpath=$(echo ${arch}|sed s,-,/,g|sed 's,epel,el,')

    mkdir -p ${HOME}/.mock
    cp /etc/mock/${arch}.cfg ${HOME}/.mock/${arch}-with-extras.cfg

    RPATH='el/7/x86_64'
    head -n -1 /etc/mock/${arch}.cfg > ${HOME}/.mock/${arch}-with-extras.cfg
    cat <<EOF >> ${HOME}/.mock/${arch}-with-extras.cfg
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
EOF

    # Build the RPMs in a clean chroot environment with mock to detect missing
    # BuildRequires lines.
    mkdir -p development
    mock -r ${HOME}/.mock/${arch}-with-extras.cfg rebuild --resultdir=development/${RPATH} ${HOME}/rpmbuild/SRPMS/${PROJ_NAME}*
done
