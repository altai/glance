%global with_doc 0
%global prj glance

%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name:             openstack-%{prj}
Epoch:            1
Version:          2012.1
Release:          1
Summary:          OpenStack Image Registry and Delivery Service

Group:            Development/Languages
License:          ASL 2.0
Vendor:           Grid Dynamics Consulting Services, Inc.
URL:              http://%{prj}.openstack.org
Source0:          %{name}-%{version}.tar.gz

BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}

BuildArch:        noarch
BuildRequires:    python-devel
BuildRequires:    python-setuptools
BuildRequires:    intltool

Requires(post):   chkconfig
Requires(postun): initscripts
Requires(preun):  chkconfig
Requires(pre):    shadow-utils
Requires:         python-%{prj} = %{epoch}:%{version}-%{release}
Requires:         start-stop-daemon

Obsoletes:        %{name}-essex

%description
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images. The Image Service API server
provides a standard REST interface for querying information about virtual disk
images stored in a variety of back-end stores, including OpenStack Object
Storage. Clients can register new virtual disk images with the Image Service,
query for information on publicly available disk images, and use the Image
Service client library for streaming virtual disk images.

This package contains the API and registry servers.

%package -n       python-%{prj}
Summary:          Glance Python libraries
Group:            Applications/System

Requires:         python-greenlet >= 0.3.1
Requires:         python-sqlalchemy >= 0.7
Requires:         python-anyjson
Requires:         python-eventlet >= 0.9.12
Requires:         python-paste-deploy
Requires:         python-routes
Requires:         python-webob = 1.0.8
Requires:         python-argparse
Requires:         python-boto >= 2.1.1
# = 2.1.1
Requires:         python-migrate >= 0.7
Requires:         python-httplib2
Requires:         pyxattr >= 0.6.0
Requires:         python-kombu
Requires:         python-pycrypto >= 2.1.0alpha1
#Requires:         python-pysendfile = 2.0.0
Requires:         python-iso8601 >= 0.1.4

Requires:         python-jsonschema

Obsoletes:        python-%{prj}-essex

%description -n   python-%{prj}
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images.

This package contains the glance Python library.

%if 0%{?with_doc}
%package doc
Summary:          Documentation for OpenStack Glance
Group:            Documentation

BuildRequires:    python-sphinx
BuildRequires:    graphviz

# Required to build module documents
BuildRequires:    python-boto
BuildRequires:    python-daemon
BuildRequires:    python-eventlet
BuildRequires:    python-gflags

%description      doc
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images.

This package contains documentation files for glance.

%endif

%prep
%setup -q 
sed '/pysendfile/d' tools/pip-requires


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
config_files="logging-api.conf
         logging-registry.conf
         glance-api-paste.ini
         glance-api.conf
         glance-cache-paste.ini
         glance-cache.conf
         glance-prefetcher.conf
         glance-pruner.conf
         glance-reaper.conf
         glance-registry-paste.ini
         glance-registry.conf
         glance-scrubber-paste.ini
         glance-scrubber.conf
         logging.cnf.sample
         policy.json"
for i in $config_files; do
    install -p -D -m 644 redhat/$i  %{buildroot}%{_sysconfdir}/%{prj}/$i
done

# Initscripts
for i in glance-api glance-registry; do
    install -p -D -m 755 redhat/${i}.init %{buildroot}%{_initrddir}/$i
done


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
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-api-paste.ini
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-api.conf
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-cache-paste.ini
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-cache.conf
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-prefetcher.conf
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-pruner.conf
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-reaper.conf
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-registry-paste.ini
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-registry.conf
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-scrubber-paste.ini
%config(noreplace) %{_sysconfdir}/%{prj}/%{prj}-scrubber.conf
%config(noreplace) %{_sysconfdir}/%{prj}/logging-api.conf
%config(noreplace) %{_sysconfdir}/%{prj}/logging-registry.conf
%config(noreplace) %{_sysconfdir}/%{prj}/logging.cnf.sample
%config(noreplace) %{_sysconfdir}/%{prj}/policy.json

%{_sharedstatedir}/%{prj}
%dir %attr(0755, %{prj}, nobody) %{_localstatedir}/log/%{prj}
%dir %attr(0755, %{prj}, nobody) %{_localstatedir}/run/%{prj}

%files -n python-%{prj}
%{python_sitelib}/*

%if 0%{?with_doc}
%files doc
%defattr(-,root,root,-)
%doc ChangeLog
%doc doc/build/html
%endif

%changelog
* Mon Oct 15 2012 Alessio Ababilov <aababilov@griddynamics.com> - 2011.3
- Cleanup the spec

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
