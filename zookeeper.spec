%global _hardened_build 1
%global skiptests       1

Name:          zookeeper
Version:       3.5.6
Release:       1%{?dist}
Summary:       A high-performance coordination service for distributed applications
License:       ASL 2.0 and BSD
URL:           https://zookeeper.apache.org/
Source0:       https://www.apache.org/dist/%{name}/%{name}-%{version}/apache-%{name}-%{version}.tar.gz
Source1:       %{name}.service

Patch1:        %{name}-%{version}-ivy-build.patch

BuildRequires: ant
BuildRequires: ant-junit
BuildRequires: ant-findbugs
BuildRequires: apache-commons-parent
BuildRequires: apache-ivy
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: findbugs
BuildRequires: boost-devel
BuildRequires: dos2unix
BuildRequires: doxygen
BuildRequires: gcc-c++
BuildRequires: graphviz
BuildRequires: ivy-local
BuildRequires: java-devel
BuildRequires: java-javadoc
BuildRequires: javacc
BuildRequires: javapackages-local
BuildRequires: javapackages-tools
BuildRequires: jackson-databind
BuildRequires: jdiff
BuildRequires: jetty-server
BuildRequires: jetty-servlet
BuildRequires: jline1
BuildRequires: jpackage-utils
BuildRequires: json_simple
BuildRequires: jtoaster
BuildRequires: junit
BuildRequires: libtool
BuildRequires: libxml2-devel
BuildRequires: mockito
BuildRequires: mvn(org.slf4j:slf4j-log4j12)
BuildRequires: netty
BuildRequires: objectweb-pom
BuildRequires: pkgconfig(cppunit)
BuildRequires: python3-devel
BuildRequires: slf4j
BuildRequires: systemd
BuildRequires: xerces-j2
BuildRequires: xml-commons-apis
BuildRequires: yetus

Requires:      java
Requires:      jline1
Requires:      jpackage-utils
Requires:      jtoaster
Requires:      junit
Requires:      log4j12
Requires:      mockito
Requires:      netty3
Requires:      slf4j

%description
ZooKeeper is a centralized service for maintaining configuration information,
naming, providing distributed synchronization, and providing group services.

##############################################
%package devel
Summary:       Development files for the %{name} library
Requires:      %{name}%{?_isa} = %{version}-%{release}

%description devel
Development files for the ZooKeeper C client library.

##############################################
%package java
Summary:        Java interface for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description java
The %{name}-java package contains Java bindings for %{name}.

##############################################
%package javadoc
Summary:       Javadoc for %{name}
BuildArch:     noarch

%description javadoc
This package contains javadoc for %{name}.

%package -n python3-%{name}
%{?python_provide:%python_provide python3-%{name}}
Summary:       Python support for %{name}
Requires:      %{name}%{?_isa} = %{version}-%{release}

%description -n python3-%{name}
Python bindings for %{name}.

%prep
%autosetup -p1 -n apache-%{name}-%{version}

%build
%pom_remove_dep com.github.spotbugs:spotbugs-annotations ivy.xml
%pom_remove_dep com.github.spotbugs:spotbugs-annotations zookeeper-server/pom.xml

%ant -Divy.mode=local \
     -Dspotbugs.skip=true \
     -Dfindbugs.home=/usr/share/findbugs \
     -Djavac.args="-Xlint -Xmaxwarns 1000" \
     clean tar

%check
%if ! %skiptests
  %ant -Divy.mode=local test
%endif

%install

# install the java dependencies.
mkdir -p %{buildroot}%{_javadir}/%{name}
install -pm 644 build/%{name}-%{version}.jar %{buildroot}%{_javadir}/%{name}/%{name}.jar
install -pm 644 build/%{name}-%{version}-test.jar %{buildroot}%{_javadir}/%{name}/%{name}-tests.jar
install -pm 644 build/contrib/ZooInspector/%{name}-%{version}-ZooInspector.jar %{buildroot}%{_javadir}/%{name}/%{name}-ZooInspector.jar

install -pm 755 bin/zkCleanup.sh %{buildroot}%{_bindir}
install -pm 755 bin/zkCli.sh %{buildroot}%{_bindir}
install -pm 755 bin/zkServer.sh %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libexecdir}

mkdir -p %{buildroot}%{_datadir}/maven-metadata
mkdir -p %{buildroot}%{_datadir}/maven-poms
install -pm 644 build/%{name}-%{version}/dist-maven/%{name}-%{version}.pom %{buildroot}%{_datadir}/maven-poms/%{name}-%{name}.pom

sed -i "s|@version@|%{version}|" %{buildroot}%{_datadir}/maven-poms/%{name}-%{name}-ZooInspector.pom
mkdir -p %{buildroot}%{_javadocdir}/%{name}
cp -pr build/docs/api/* %{buildroot}%{_javadocdir}/%{name}/

pushd src/contrib/zkpython
%set_build_flags
%{__python3} src/python/setup.py build --build-base=$PWD/build \
install --root=%{buildroot} ;\
chmod 0755 %{buildroot}%{python3_sitearch}/zookeeper.cpython-*.so
popd

find %{buildroot} -name '*.la' -exec rm -f {} ';'
find %{buildroot} -name '*.a' -exec rm -f {} ';'

mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sysconfdir}/zookeeper
mkdir -p %{buildroot}%{_localstatedir}/log/zookeeper
mkdir -p %{buildroot}%{_sharedstatedir}/zookeeper
mkdir -p %{buildroot}%{_sharedstatedir}/zookeeper/data
mkdir -p %{buildroot}%{_sharedstatedir}/zookeeper/log
install -p -m 0640 conf/log4j.properties %{buildroot}%{_sysconfdir}/zookeeper
install -p -m 0640 conf/zoo_sample.cfg %{buildroot}%{_sysconfdir}/zookeeper
touch %{buildroot}%{_sysconfdir}/zookeeper/zoo.cfg
touch %{buildroot}%{_sharedstatedir}/zookeeper/data/myid

%pre
getent group zookeeper >/dev/null || groupadd -r zookeeper
getent passwd zookeeper >/dev/null || \
    useradd -r -g zookeeper -d %{_sharedstatedir}/zookeeper -s /sbin/nologin \
    -c "ZooKeeper service account" zookeeper

%post
%systemd_post zookeeper.service

%preun
%systemd_preun zookeeper.service

%postun
%systemd_postun_with_restart zookeeper.service

%files
%{_bindir}/cli_mt
%{_bindir}/cli_st
%{_bindir}/load_gen
%{_bindir}/zk*.sh
%{_libexecdir}/zkEnv.sh
%{_libdir}/lib*.so.*

%attr(0755,root,root) %dir %{_sysconfdir}/zookeeper
%attr(0644,root,root) %ghost %config(noreplace) %{_sysconfdir}/zookeeper/zoo.cfg
%attr(0644,root,root) %{_sysconfdir}/zookeeper/zoo_sample.cfg
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/zookeeper/log4j.properties

%attr(0755,zookeeper,zookeeper) %dir %{_localstatedir}/log/zookeeper
%attr(0755,root,root) %dir %{_sharedstatedir}/zookeeper
%attr(0750,zookeeper,zookeeper) %dir %{_sharedstatedir}/zookeeper/data
%attr(0640,zookeeper,zookeeper) %ghost %{_sharedstatedir}/zookeeper/data/myid
%attr(0755,zookeeper,zookeeper) %dir %{_sharedstatedir}/zookeeper/log
%{_unitdir}/zookeeper.service
%doc CHANGES.txt LICENSE.txt NOTICE.txt README.txt

%files java
%dir %{_javadir}/%{name}
%{_javadir}/%{name}/%{name}.jar
%{_javadir}/%{name}/%{name}-tests.jar
%{_javadir}/%{name}/%{name}-ZooInspector.jar
%if 0%{?fedora} >= 21 || 0%{?rhel} > 7
%{_datadir}/maven-poms/%{name}-%{name}.pom
%{_datadir}/maven-poms/%{name}-%{name}-ZooInspector.pom
%{_datadir}/maven-metadata/%{name}.xml
%else
%{_mavendepmapfragdir}/%{name}
%{_mavenpomdir}/JPP.%{name}-%{name}.pom
%{_mavenpomdir}/JPP.%{name}-%{name}-ZooInspector.pom
%endif
%doc CHANGES.txt LICENSE.txt NOTICE.txt README.txt

%files devel
%{_includedir}/%{name}/
%{_libdir}/*.so
%doc src/c/LICENSE src/c/NOTICE.txt

%files javadoc
%{_javadocdir}/%{name}
%doc LICENSE.txt NOTICE.txt

%files -n python3-%{name}
%{python3_sitearch}/ZooKeeper-?.?-py%{python3_version}.egg-info
%{python3_sitearch}/zookeeper.cpython-*.so
%doc LICENSE.txt NOTICE.txt src/contrib/zkpython/README

%changelog
* Mon Oct 21 2019 Javi Roman <javiroman@apache.org> - 3.5.6-1
- Rebuilt and bump.

* Sat Jul 27 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.9-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.9-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Nov 28 2018 Petr Viktorin <pviktori@redhat.com> - 3.4.9-12
- Switch to Python 3
  https://bugzilla.redhat.com/show_bug.cgi?id=1630088

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.9-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Mar 27 2018 Iryna Shcherbina <ishcherb@redhat.com> - 3.4.9-10
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Thu Mar 08 2018 Christopher Tubbs <ctubbsii@fedoraproject.org> - 3.4.9-9
- Add gcc-c++ BuildRequires

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.9-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Sep 07 2017 Troy Dawson <tdawson@redhat.com> - 3.4.9-7
- Cleanup spec file conditionals

* Sat Aug 19 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 3.4.9-6
- Python 2 binary package renamed to python2-zookeeper
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.9-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.9-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.9-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jan 27 2017 Jonathan Wakely <jwakely@redhat.com> - 3.4.9-2
- Rebuilt for Boost 1.63

* Thu Dec 22 2016 Christopher Tubbs <ctubbsii@fedoraproject.org> - 3.4.9-1
- Update to 3.4.9; CVE-2016-5017 (bz#1377281)

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.6-17
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.6-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sat Jan 16 2016 Jonathan Wakely <jwakely@redhat.com> - 3.4.6-15
- Rebuilt for Boost 1.60

* Sun Nov 15 2015 Christopher Tubbs <ctubbsii-fedora@apache.org> - 3.4.6-14
- Remove duplicates and fix broken classpath items in zkEnv

* Tue Nov 03 2015 Christopher Tubbs <ctubbsii-fedora@apache.org> - 3.4.6-13
- Remove unused build dependency log4cxx

* Mon Oct 19 2015 Christopher Tubbs <ctubbsii-fedora@apache.org> - 3.4.6-12
- Fix bz#1272694 Remove precondition on myid file for standalone defaults

* Fri Oct 16 2015 Christopher Tubbs <ctubbsii-fedora@apache.org> - 3.4.6-11
- Fix bad rollback. Rollback to netty 3.6.6, not 3.7.0 (f21 only)

* Fri Oct 16 2015 Christopher Tubbs <ctubbsii-fedora@apache.org> - 3.4.6-10
- Rollback changes for netty 3.9.3 for f21 only

* Fri Oct 16 2015 Christopher Tubbs <ctubbsii-fedora@apache.org> - 3.4.6-9
- Update zkEnv.sh CLASSPATH to fix bz#1261458

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 3.4.6-8
- Rebuilt for Boost 1.59

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.6-7
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 3.4.6-6
- rebuild for Boost 1.58

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Feb 15 2015 Peter Robinson <pbrobinson@fedoraproject.org> 3.4.6-4
- Update netty3 patch for 3.9.3

* Tue Jan 27 2015 Petr Machata <pmachata@redhat.com> - 3.4.6-3
- Rebuild for boost 1.57.0

* Thu Oct 23 2014 Timothy St. Clair <tstclair@redhat.com> - 3.4.6-2
- Add back -java subpackage

* Tue Oct 21 2014 Timothy St. Clair <tstclair@redhat.com> - 3.4.6-1
- Update to latest stable series
- Cleanup and overhaul package
- Updated system integration

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.5-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.5-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 3.4.5-18
- Rebuild for boost 1.55.0

* Mon Feb 24 2014 Timothy St. Clair <tstclair@redhat.com> - 3.4.5-17
- Update due to cascading dependencies around java-headless

* Fri Jan 31 2014 Timothy St. Clair <tstclair@redhat.com> - 3.4.5-16
- Update of tests.jar due to netty3 compat packaging conflicts

* Fri Jan 24 2014 Timothy St. Clair <tstclair@redhat.com> - 3.4.5-15
- Update jline and netty3 for f21 builds

* Fri Oct 25 2013 Timothy St. Clair <tstclair@redhat.com> - 3.4.5-14
- Update dependencies to jline1

* Wed Sep 18 2013 Timothy St. Clair <tstclair@redhat.com> - 3.4.5-13
- Fixed the atomic patch which actually caused recursive crashing on zookeeper_close

* Tue Jul 30 2013 Petr Machata <pmachata@redhat.com> - 3.4.5-12
- Rebuild for boost 1.54.0

* Tue Jul 30 2013 gil cattaneo <puntogil@libero.it> 3.4.5-11
- fix changelog entries

* Mon Jul 22 2013 Timothy St. Clair <tstclair@redhat.com> - 3.4.5-10
- update permissions to be in line with default policies

* Mon Jul 22 2013 gil cattaneo <puntogil@libero.it> 3.4.5-9
- removed not needed %%defattr (only required for rpm < 4.4)
- removed not needed Group fields (new package guideline)
- fix directory ownership in java sub package

* Mon Jul 22 2013 Timothy St. Clair <tstclair@redhat.com> - 3.4.5-8
- cleanup file ownership properties.

* Sat Jun 15 2013 Jeffrey C. Ollie <jeff@ocjtech.us> - 3.4.5-7
- add server subpackage

* Fri Jun 14 2013 Dan Horák <dan[at]danny.cz> - 3.4.5-6
- use fetch_and_add from GCC, fixes build on non-x86 arches

* Tue Jun 11 2013  gil cattaneo <puntogil@libero.it> 3.4.5-5
- fixed zookeeper.so non-standard-executable-perm thanks to Björn Esser

* Tue Jun 11 2013  gil cattaneo <puntogil@libero.it> 3.4.5-4
- enabled hardened-builds
- fixed fully versioned dependency in subpackages (lib-devel and python)
- fixed License tag
- moved large documentation in lib-doc subpackage

* Sat Apr 27 2013 gil cattaneo <puntogil@libero.it> 3.4.5-3
- built ZooInspector
- added additional poms files

* Tue Apr 23 2013 gil cattaneo <puntogil@libero.it> 3.4.5-2
- building/packaging of the zookeeper-test.jar thanks to Robert Rati

* Sun Dec 02 2012 gil cattaneo <puntogil@libero.it> 3.4.5-1
- update to 3.4.5

* Tue Oct 30 2012 gil cattaneo <puntogil@libero.it> 3.4.4-3
- fix missing hostname

* Fri Oct 12 2012 gil cattaneo <puntogil@libero.it> 3.4.4-2
- add ant-junit as BR

* Fri Oct 12 2012 gil cattaneo <puntogil@libero.it> 3.4.4-1
- update to 3.4.4

* Fri May 18 2012 gil cattaneo <puntogil@libero.it> 3.4.3-1
- initial rpm
