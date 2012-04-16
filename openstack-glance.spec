%global with_doc 0
%global prj glance
%global short_name openstack-%{prj}
%global os_release essex

%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name:             %{short_name}-%{os_release}
Epoch:            1
Version:          2012.1
Release:          1
Summary:          OpenStack Image Registry and Delivery Service

Group:            Development/Languages
License:          ASL 2.0
Vendor:           Grid Dynamics Consulting Services, Inc.
URL:              http://%{prj}.openstack.org
Source0:          %{prj}-%{version}.tar.gz
Source1:          %{prj}-api.init
Source2:          %{prj}-registry.init
Source3:          %{short_name}-logging-api.conf
Source4:          %{short_name}-logging-registry.conf

BuildRoot:        %{_tmppath}/%{prj}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:        noarch
BuildRequires:    python-devel
BuildRequires:    python-setuptools

Requires(post):   chkconfig
Requires(postun): initscripts
Requires(preun):  chkconfig
Requires(pre):    shadow-utils
Requires:         python-%{prj}-%{os_release} = %{epoch}:%{version}-%{release}
Requires:         python-kombu >= 1.1.3
Requires:         start-stop-daemon

Conflicts: %{short_name} =< 2011.3.2

%description
The Glance project provides services for discovering, registering, and
retrieving virtual machine images. Glance has a RESTful API that allows
querying of VM image metadata as well as retrieval of the actual image.

This package contains the API server and a reference implementation registry
server, along with a client library.

%package -n       python-%{prj}-%{os_release}
Summary:          Glance Python libraries
Group:            Applications/System

Requires:         python-setuptools
Requires:         python-anyjson
Requires:         python-argparse
Requires:         python-boto >= 1.9b
Requires:         python-daemon = 1.5.5
Requires:         python-eventlet >= 0.9.12
Requires:         python-gflags >= 1.3
Requires:         python-greenlet >= 0.3.1
Requires:         python-lockfile >= 0.8
Requires:         python-mox >= 0.5.0
Requires:         python-paste-deploy >= 1.5.0
Requires:         python-routes
Requires:         python-sqlalchemy >= 0.6.3
Requires:         python-webob >= 1.0.8
Requires:         pyxattr >= 0.6.0

%description -n   python-%{prj}-%{os_release}
The Glance project provides services for discovering, registering, and
retrieving virtual machine images. Glance has a RESTful API that allows
querying of VM image metadata as well as retrieval of the actual image.

This package contains the project's Python library.

%if 0%{?with_doc}
%package doc-%{os_release}
Summary:          Documentation for OpenStack Glance
Group:            Documentation

BuildRequires:    python-sphinx
BuildRequires:    python-nose
# Required to build module documents
BuildRequires:    python-boto
BuildRequires:    python-daemon
BuildRequires:    python-eventlet
BuildRequires:    python-gflags
BuildRequires:    python-routes
BuildRequires:    python-sqlalchemy
BuildRequires:    python-webob

%description      doc-%{os_release}
The Glance project provides services for discovering, registering, and
retrieving virtual machine images. Glance has a RESTful API that allows
querying of VM image metadata as well as retrieval of the actual image.

This package contains documentation files for OpenStack Glance.

%endif

%prep
%setup -q -n %{prj}-%{version}

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests

%if 0%{?with_doc}
export PYTHONPATH="$( pwd ):$PYTHONPATH"
pushd doc
sphinx-build -b html source build/html
popd

# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo
%endif

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{prj}/images

# Config file
install -p -D -m 644 etc/%{prj}-api.conf %{buildroot}%{_sysconfdir}/%{prj}/%{prj}-api.conf
install -p -D -m 644 etc/%{prj}-registry.conf %{buildroot}%{_sysconfdir}/%{prj}/%{prj}-registry.conf
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/%{prj}/logging-api.conf
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/%{prj}/logging-registry.conf

# Initscripts
install -p -D -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/%{prj}-api
install -p -D -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/%{prj}-registry

# Install pid directory
install -d -m 755 %{buildroot}%{_localstatedir}/run/%{prj}

# Install log directory
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{prj}

%clean
rm -rf %{buildroot}

%pre
getent group %{prj} >/dev/null || groupadd -r %{prj}
getent passwd %{prj} >/dev/null || \
useradd -r -g %{prj} -d %{_sharedstatedir}/%{prj} -s /sbin/nologin \
-c "OpenStack Glance Daemons" %{prj}
exit 0

%preun
if [ $1 = 0 ] ; then
    /sbin/service %{prj}-api stop
    /sbin/service %{prj}-registry stop
fi

%files
%defattr(-,root,root,-)
%doc README.rst
%{_bindir}/%{prj}
%{_bindir}/%{prj}-api
%{_bindir}/%{prj}-control
%{_bindir}/%{prj}-manage
%{_bindir}/%{prj}-registry
%{_bindir}/%{prj}-cache-prefetcher
%{_bindir}/%{prj}-cache-pruner
%{_bindir}/%{prj}-cache-manage
%{_bindir}/%{prj}-cache-cleaner
%{_bindir}/%{prj}-scrubber
%{_initrddir}/%{prj}-api
%{_initrddir}/%{prj}-registry
%defattr(-,%{prj},nobody,-)
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-api.conf
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-registry.conf
%config(noreplace) %{_sysconfdir}/%{prj}/logging-api.conf
%config(noreplace) %{_sysconfdir}/%{prj}/logging-registry.conf
%{_sharedstatedir}/%{prj}
%dir %attr(0755, %{prj}, nobody) %{_localstatedir}/log/%{prj}
%dir %attr(0755, %{prj}, nobody) %{_localstatedir}/run/%{prj}

%files -n python-%{prj}-%{os_release}
%{python_sitelib}/%{prj}
%{python_sitelib}/%{prj}-%{version}-*.egg-info

%if 0%{?with_doc}
%files doc-%{os_release}
%defattr(-,root,root,-)
%doc ChangeLog
%doc doc/build/html
%endif

%changelog
* Mon Mar 12 2012 Sergey Kosyrev <skosyrev@griddynamics.com> - 2011.3
- Added missing dependencies: python-setuptools and start-stop-daemon
* Fri Dec 16 2011 Boris Filippov <bfilippov@griddynamics.com> - 2011.3
- Remove meaningless Jenkins changelog entries
- Make init scripts LSB conformant
- Rename init scripts
- Disable services autorun

* Fri Apr 15 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.3-0.1.bzr116
- Diablo versioning

* Thu Mar 31 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.18.bzr100
- Added missed files

* Thu Mar 31 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.17.bzr100
- Added new initscripts
- Changed default logging configuration

* Thu Mar 31 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.16.bzr100
- fixed path to SQLite db in default config

* Tue Mar 29 2011 Mr. Jenkins GD <openstack@griddynamics.net> - 2011.2-0.15.bzr100
- Update to bzr100

* Tue Mar 29 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.14.bzr99
- Uncommented Changelog back

* Tue Mar 29 2011 Mr. Jenkins GD <openstack@griddynamics.net> - 2011.2-0.13.bzr99
- Update to bzr99

* Fri Mar 25 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.12.bzr96
- Update to bzr96
- Temporary commented Changelog in %doc

* Thu Mar 24 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.11.bzr95
- Update to bzr95

* Mon Mar 21 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.10.bzr93
- Added /var/lib/glance and subdirs to include images in package

* Mon Mar 21 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.9.bzr93
- Update to bzr93

* Mon Mar 21 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.8.bzr92
- Update to bzr92

* Thu Mar 17 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.7.bzr90
- Added ChangeLog

* Thu Mar 17 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.6.bzr90
- Update to bzr90

* Wed Mar 16 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.5.bzr88
- Update to bzr88

* Wed Mar 16 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.4.bzr87
- Default configs patched

* Wed Mar 16 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.3.bzr87
- Added new config files

* Wed Mar 16 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.2.bzr87
- Config file moved from /etc/nova to /etc/glance

* Wed Mar 16 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 2011.2-0.1.bzr87
- pre-Cactus version

* Mon Feb 07 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 0.1.7-1
- Release 0.1.7

* Thu Jan 27 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 0.1.5-1
- Release 0.1.5

* Wed Jan 26 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 0.1.4-1
- Release 0.1.4

* Mon Jan 24 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 0.1.3-2
- Changed description (thanks to Jay Pipes)
- Added python-argparse to deps, required by /usr/bin/glance-upload

* Mon Jan 24 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 0.1.3-1
- Release 0.1.3
- Added glance-upload to openstack-glance package

* Fri Jan 21 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 0.1.2-3
- Added pid directory
- Relocated log to /var/log/glance/glance.log

* Fri Jan 21 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 0.1.2-2
- Changed permissions on initscript

* Thu Jan 20 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> - 0.1.2-1
- Initial build
