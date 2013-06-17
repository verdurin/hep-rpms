#
# Copyright (c) 2003 FreeIPMI Core Team
#

Release: 3%{?dist}

Name: freeipmi
Version: 1.2.7
License: GPLv2+
Group: Applications/System
URL: http://www.gnu.org/software/freeipmi/
Source: ftp://ftp.gluster.com/pub/freeipmi/%{version}/%{name}-%{version}.tar.gz
Source1: ipmidetectd.conf
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libgcrypt-devel texinfo
Requires(pre): chkconfig
Requires(post): chkconfig
Requires(preun): chkconfig
# for /sbin/service 
Requires(preun): initscripts
Requires(post): info
Requires(preun): info
# Necessary as only those archs implement iopl and friends (#368541)
ExclusiveArch: %{ix86} x86_64 ia64 alpha
Summary: IPMI remote console and system management software
%description
The FreeIPMI project provides "Remote-Console" (out-of-band) and
"System Management Software" (in-band) based on Intelligent
Platform Management Interface specification.

%package devel
Summary: Development package for FreeIPMI
Group: Development/System
Requires: freeipmi = %{version}-%{release}
%description devel
Development package for FreeIPMI.  This package includes the FreeIPMI
header files and libraries.

%package bmc-watchdog
Summary: IPMI BMC watchdog
Group: Applications/System
Requires: freeipmi = %{version}-%{release}
Requires(post): chkconfig
Requires(preun): chkconfig
Requires: logrotate
%description bmc-watchdog
Provides a watchdog daemon for OS monitoring and recovery.

%package ipmidetectd
Summary: IPMI node detection monitoring daemon
Group: Applications/System
Requires: freeipmi = %{version}-%{release}
Requires(post): chkconfig
Requires(preun): chkconfig
%description ipmidetectd
Provides a tool and a daemon for IPMI node detection.

%package ipmiseld
Summary: IPMI SEL syslog logging daemon
Group: Applications/System
Requires: freeipmi = %{version}-%{release}
%description ipmiseld
IPMI SEL syslog logging daemon.


%if %{?_with_debug:1}%{!?_with_debug:0}
  %define _enable_debug --enable-debug --enable-trace --enable-syslog
%endif

%prep
%setup -q

%build
export CFLAGS="-D_GNU_SOURCE $RPM_OPT_FLAGS"
%configure --program-prefix=%{?_program_prefix:%{_program_prefix}} \
           %{?_enable_debug} --disable-static
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
DESTDIR="$RPM_BUILD_ROOT" make install
# fix coherance problems with associated script filenames
mkdir -p $RPM_BUILD_ROOT/%{_initrddir}/
# if check needed for SLES systems
if [[ "%{_sysconfdir}/init.d" != "%{_initrddir}" ]]
then
mv $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/bmc-watchdog $RPM_BUILD_ROOT/%{_initrddir}/bmc-watchdog
mv $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/ipmidetectd $RPM_BUILD_ROOT/%{_initrddir}/ipmidetectd
mv $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/ipmiseld $RPM_BUILD_ROOT/%{_initrddir}/ipmiseld
fi
rm -f %{buildroot}%{_infodir}/dir
# kludge to get around rpmlint complaining about 0 length semephore file
echo freeipmi > %{buildroot}%{_localstatedir}/lib/freeipmi/ipckey
# Remove .la files
rm -rf $RPM_BUILD_ROOT/%{_libdir}/*.la


cp %SOURCE1 $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/install-info %{_infodir}/freeipmi-faq.info.gz %{_infodir}/dir &>/dev/null || :
/sbin/ldconfig

%preun
if [ $1 = 0 ]; then
    /sbin/install-info --delete %{_infodir}/freeipmi-faq.info.gz %{_infodir}/dir &>/dev/null || :
fi

%postun -p /sbin/ldconfig

%post bmc-watchdog
/sbin/chkconfig --add bmc-watchdog

%preun bmc-watchdog
if [ "$1" = 0 ]; then
    /sbin/service bmc-watchdog stop >/dev/null 2>&1
    /sbin/chkconfig --del bmc-watchdog
fi

%postun bmc-watchdog
if [ "$1" -ge "1" ] ; then
    /sbin/service bmc-watchdog condrestart >/dev/null 2>&1 || :
fi

%post ipmiseld
/sbin/chkconfig --add ipmiseld

%preun ipmiseld
if [ "$1" = 0 ]; then
    /sbin/service ipmiseld stop >/dev/null 2>&1
    /sbin/chkconfig --del ipmiseld
fi


%post ipmidetectd
/sbin/chkconfig --add ipmidetectd

%preun ipmidetectd
if [ "$1" = 0 ]; then
    /sbin/service ipmidetectd stop >/dev/null 2>&1
    /sbin/chkconfig --del ipmidetectd
fi

%postun ipmidetectd
if [ "$1" -ge "1" ] ; then
    /sbin/service/ipmidetectd condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root)
%dir %{_sysconfdir}/freeipmi/
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/freeipmi_interpret_sensor.conf
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/freeipmi.conf
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/libipmiconsole.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/freeipmi_interpret_sel.conf
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/ipmidetect.conf
%doc %{_datadir}/doc/%{name}/AUTHORS
%doc %{_datadir}/doc/%{name}/COPYING
%doc %{_datadir}/doc/%{name}/ChangeLog
%doc %{_datadir}/doc/%{name}/ChangeLog.0
%doc %{_datadir}/doc/%{name}/INSTALL
%doc %{_datadir}/doc/%{name}/NEWS
%doc %{_datadir}/doc/%{name}/README
%doc %{_datadir}/doc/%{name}/README.argp
%doc %{_datadir}/doc/%{name}/README.build
%doc %{_datadir}/doc/%{name}/TODO
%doc %{_infodir}/*
%doc %{_datadir}/doc/%{name}/COPYING.ipmiping
%doc %{_datadir}/doc/%{name}/COPYING.ipmipower
%doc %{_datadir}/doc/%{name}/COPYING.ipmiconsole
%doc %{_datadir}/doc/%{name}/COPYING.ipmimonitoring
%doc %{_datadir}/doc/%{name}/COPYING.pstdout
%doc %{_datadir}/doc/%{name}/COPYING.ipmidetect
%doc %{_datadir}/doc/%{name}/COPYING.ipmi-fru
%doc %{_datadir}/doc/%{name}/COPYING.ipmi-dcmi
%doc %{_datadir}/doc/%{name}/COPYING.sunbmc
%doc %{_datadir}/doc/%{name}/COPYING.ZRESEARCH
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiping
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmipower
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiconsole
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmi-dcmi
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmimonitoring
%doc %{_datadir}/doc/%{name}/DISCLAIMER.pstdout
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmidetect
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmi-fru
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiping.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmipower.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiconsole.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmimonitoring.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.pstdout.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmidetect.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmi-fru.UC
%doc %{_datadir}/doc/%{name}/README.openipmi
%doc %{_datadir}/doc/%{name}/freeipmi-design.txt
%doc %{_datadir}/doc/%{name}/freeipmi-coding.txt
%doc %{_datadir}/doc/%{name}/freeipmi-hostrange.txt
%doc %{_datadir}/doc/%{name}/freeipmi-libraries.txt
%doc %{_datadir}/doc/%{name}/freeipmi-bugs-issues-and-workarounds.txt
%doc %{_datadir}/doc/%{name}/freeipmi-testing.txt
%doc %{_datadir}/doc/%{name}/freeipmi-oem-documentation-requirements.txt
%dir %{_datadir}/doc/%{name}
%dir %{_datadir}/doc/%{name}/contrib
%dir %{_datadir}/doc/%{name}/contrib/ganglia
%doc %{_datadir}/doc/%{name}/contrib/ganglia/*
%dir %{_datadir}/doc/%{name}/contrib/nagios
%doc %{_datadir}/doc/%{name}/contrib/nagios/*
%dir %{_datadir}/doc/%{name}/contrib/pet
%doc %{_datadir}/doc/%{name}/contrib/pet/*
%{_libdir}/libipmiconsole*so.*
%{_libdir}/libfreeipmi*so.*
%{_libdir}/libipmidetect*so.*
%{_libdir}/libipmimonitoring.so.*
%{_localstatedir}/lib/*
%{_sbindir}/bmc-config
%{_sbindir}/bmc-info
%{_sbindir}/bmc-device
%{_sbindir}/ipmi-fru
%{_sbindir}/ipmi-locate
%{_sbindir}/ipmi-oem
%{_sbindir}/ipmi-pef-config
%{_sbindir}/pef-config
%{_sbindir}/ipmi-raw
%{_sbindir}/ipmi-sel
%{_sbindir}/ipmi-sensors
%{_sbindir}/ipmi-sensors-config
%{_sbindir}/ipmiping
%{_sbindir}/ipmi-ping
%{_sbindir}/ipmipower
%{_sbindir}/ipmi-power
%{_sbindir}/rmcpping
%{_sbindir}/rmcp-ping
%{_sbindir}/ipmiconsole
%{_sbindir}/ipmi-console
%{_sbindir}/ipmimonitoring
%{_sbindir}/ipmi-chassis
%{_sbindir}/ipmi-chassis-config
%{_sbindir}/ipmi-dcmi
%{_sbindir}/ipmi-pet
%{_sbindir}/ipmidetect
%{_sbindir}/ipmi-detect
%{_mandir}/man8/bmc-config.8*
%{_mandir}/man5/bmc-config.conf.5*
%{_mandir}/man8/bmc-info.8*
%{_mandir}/man8/bmc-device.8*
%{_mandir}/man8/ipmi-fru.8*
%{_mandir}/man8/ipmi-locate.8*
%{_mandir}/man8/pef-config.8*
%{_mandir}/man8/ipmi-oem.8*
%{_mandir}/man8/ipmi-pef-config.8*
%{_mandir}/man8/ipmi-raw.8*
%{_mandir}/man8/ipmi-sel.8*
%{_mandir}/man8/ipmi-sensors.8*
%{_mandir}/man8/ipmi-sensors-config.8*
%{_mandir}/man8/ipmiping.8*
%{_mandir}/man8/ipmi-ping.8*
%{_mandir}/man8/ipmipower.8*
%{_mandir}/man8/ipmi-power.8*
%{_mandir}/man5/ipmipower.conf.5*
%{_mandir}/man8/rmcpping.8*
%{_mandir}/man8/rmcp-ping.8*
%{_mandir}/man8/ipmiconsole.8*
%{_mandir}/man8/ipmi-console.8*
%{_mandir}/man5/ipmiconsole.conf.5*
%{_mandir}/man8/ipmimonitoring.8*
%{_mandir}/man5/ipmi_monitoring_sensors.conf.5*
%{_mandir}/man5/ipmimonitoring_sensors.conf.5*
%{_mandir}/man5/ipmimonitoring.conf.5*
%{_mandir}/man5/freeipmi_interpret_sel.conf.5*
%{_mandir}/man5/freeipmi_interpret_sensor.conf.5*
%{_mandir}/man5/libipmimonitoring.conf.5*
%{_mandir}/man8/ipmi-chassis.8*
%{_mandir}/man8/ipmi-chassis-config.8*
%{_mandir}/man8/ipmi-dcmi.8*
%{_mandir}/man8/ipmi-pet.8*
%{_mandir}/man8/ipmidetect.8*
%{_mandir}/man8/ipmi-detect.8*
%{_mandir}/man5/freeipmi.conf.5*
%{_mandir}/man5/ipmidetect.conf.5*
%{_mandir}/man5/libipmiconsole.conf.5*
%{_mandir}/man7/freeipmi.7*
%dir %{_localstatedir}/cache/ipmimonitoringsdrcache


%files devel
%defattr(-,root,root)
%dir %{_datadir}/doc/%{name}/contrib/libipmimonitoring
%doc %{_datadir}/doc/%{name}/contrib/libipmimonitoring/*
%{_libdir}/libipmiconsole.so
%{_libdir}/libfreeipmi.so
%{_libdir}/libipmidetect.so
%{_libdir}/libipmimonitoring.so
%dir %{_includedir}/freeipmi
%dir %{_includedir}/freeipmi/api
%dir %{_includedir}/freeipmi/cmds
%dir %{_includedir}/freeipmi/debug
%dir %{_includedir}/freeipmi/driver
%dir %{_includedir}/freeipmi/fiid
%dir %{_includedir}/freeipmi/interface
%dir %{_includedir}/freeipmi/locate
%dir %{_includedir}/freeipmi/record-format
%dir %{_includedir}/freeipmi/spec
%dir %{_includedir}/freeipmi/util
%{_includedir}/ipmiconsole.h
%{_includedir}/ipmidetect.h
%{_includedir}/ipmi_monitoring*.h
%{_includedir}/freeipmi/*.h
%{_includedir}/freeipmi/api/*.h
%{_includedir}/freeipmi/cmds/*.h
%{_includedir}/freeipmi/debug/*.h
%{_includedir}/freeipmi/driver/*.h
%{_includedir}/freeipmi/fiid/*.h
%{_includedir}/freeipmi/fru/*.h
%{_includedir}/freeipmi/interface/*.h
%{_includedir}/freeipmi/interpret/*.h
%{_includedir}/freeipmi/locate/*.h
%{_includedir}/freeipmi/payload/*.h
%{_includedir}/freeipmi/record-format/*.h
%{_includedir}/freeipmi/sdr/*.h
%{_includedir}/freeipmi/sel/*.h
%{_includedir}/freeipmi/sensor-read/*.h
%{_includedir}/freeipmi/spec/*.h
%{_includedir}/freeipmi/templates/*.h
%{_includedir}/freeipmi/util/*.h
%{_mandir}/man3/*
%{_libdir}/pkgconfig/*

%files bmc-watchdog
%defattr(-,root,root)
%doc %{_datadir}/doc/%{name}/COPYING.bmc-watchdog
%doc %{_datadir}/doc/%{name}/DISCLAIMER.bmc-watchdog
%doc %{_datadir}/doc/%{name}/DISCLAIMER.bmc-watchdog.UC
%{_initrddir}/bmc-watchdog
%config(noreplace) %{_sysconfdir}/sysconfig/bmc-watchdog
%{_sbindir}/bmc-watchdog
%{_mandir}/man8/bmc-watchdog.8*


%files ipmidetectd
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/ipmidetectd.conf
%{_initrddir}/ipmidetectd
%{_sbindir}/ipmidetectd
%{_mandir}/man5/ipmidetectd.conf.5*
%{_mandir}/man8/ipmidetectd.8*

%files ipmiseld
%doc %{_datadir}/doc/%{name}/COPYING.ipmiseld
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiseld
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/ipmiseld.conf
%{_sbindir}/ipmiseld
%{_mandir}/man5/ipmiseld.conf.5*
%{_mandir}/man8/ipmiseld.8*
%dir %{_localstatedir}/cache/ipmiseld
%{_initrddir}/ipmiseld

%changelog
* Mon Jun 17 2013 Adam Huffman <a.huffman@imperial.ac.uk> - 1.2.7-3
- add more missing files from Fedora 1.2.4 spec

* Fri Jun 14 2013 Adam Huffman <a.huffman@imperial.ac.uk> - 1.2.7-2
- remove obsolete prefix removal actions

* Fri Jun 14 2013 Adam Huffman <a.huffman@imperial.ac.uk> - 1.2.7-1
- Update to 1.2.7

* Mon May  3 2010 Jan Safranek <jsafrane@redhat.com> - 0.7.16-3
- Add sample /etc/ipmidetectd.conf configuration file (#587636)

* Tue Mar 30 2010 Jan Safranek <jsafrane@redhat.com> - 0.7.16-2
- Fix the ipmievd initscript to actually start the service and better
  LSB compatibility (#578172). As consequence, the init scripts were
  renamed to ipmidetectd and bmc-watchdog (was: freeipmi-ipmidetectd
  and freeipmi-bmc-watchdog).

* Tue Dec  1 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.16-1
- Update to freeipmi-0.7.16

* Mon Oct  5 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.12-4
- Fix package source URL

* Mon Sep 14 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.12-3
- Fix init scripts to be LSB compliant and return correct exit codes
  and provide mandatory actions (#523169, #523177)

* Wed Sep  9 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.12-2
- Update to freeipmi-0.7.12

* Thu Aug  6 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.11-2
- Fix installation with --excludedocs option (#515926)

* Wed Jul 29 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.11-1
- Update to freeipmi-0.7.11

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jun 29 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.10-2
- Fix (de-)installation scripts

* Wed Jun 17 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.10-1
- Update to freeipmi-0.7.10

* Mon May 18 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.9-1
- Update to freeipmi-0.7.9

* Thu Apr 16 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.8-2
- Fix compilation flags, debuginfo package is correctly generated now

* Tue Apr 14 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.8-1
- Update to freeipmi-0.7.8

* Thu Apr  9 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.7-1
- Update to freeipmi-0.7.7

* Tue Mar 10 2009 Jesse Keating <jkeating@redhat.com> - 0.7.6-2
- Fix the bad dist macro
- Remove version define, that's what the Version line is for
- Remove name define, that's what the Name line is for
- Use the real Release line in the if debug statement

* Mon Mar  9 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.6-1
- Update to freeipmi-0.7.6

* Tue Feb 24 2009 Jan Safranek <jsafrane@redhat.com> - 0.7.5-1
- Update to freeipmi-0.7.5

* Thu Jan 22 2009 Karsten Hopp <karsten@redhat.com> 0.6.4-2
- fix ipmiconsole log directory

* Mon Jul 28 2008 Phil Knirsch <pknirsch@redhat.com> - 0.6.4-1
- Update to freeipmi-0.6.4
- Fixed unecessary logrotate message for bmc-watchdog (#456648)

* Wed Feb 27 2008 Phil Knirsch <pknirsch@redhat.com> - 0.5.1-3
- Fix GCC 4.3 rebuild problems

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.5.1-2
- Autorebuild for GCC 4.3

* Tue Dec 18 2007 Phil Knirsch <pknirsch@redhat.com> 0.5.1-1
- Update to freeipmi-0.5.1

* Wed Nov 19 2007 Albert Chu <chu11@llnl.gov> 0.5.0
- Remove ipmimonitoring subpackage.  Merge into head package.

* Wed Nov 07 2007 Phil Knirsch <pknirsch@redhat.com> 0.4.6-3.fc7
- More fixes for Fedora Review:
 o Added ExclusiveArch due to missing lopl (#368541)

* Tue Nov 06 2007 Phil Knirsch <pknirsch@redhat.com> 0.4.6-2.fc7
- Several fixes due to Fedora package review:
 o Fixed Group for all subpackages
 o Added missng Requires(Post|Preun) for several packages
 o Removed static libraries and .la files
 o Fixed open bug (missing mode for O_CREATE)
 o Fixed incorrect options for bmc-watchdog daemon

* Mon Nov 05 2007 Phil Knirsch <pknirsch@redhat.com> 0.4.6-1.fc7
- Specfile cleanup for Fedora inclusion
- Fixed several rpmlint warnings and errors:
 o Moved all devel libs to proper package

* Wed Aug 01 2007 Troy Telford <ttelford@lnxi.com> 0.4.0
- Some package cleanup so it builds on SLES

* Wed Jun 13 2007 Phil Knirsch <pknirsch@redhat.com> 0.4.beta0-1
- Some package cleanup and split of configuration and initscript

* Fri Feb 28 2007 Albert Chu <chu11@llnl.gov> 0.4.beta0-1
- Add ipmidetectd subpackage.

* Fri Feb 16 2007 Albert Chu <chu11@llnl.gov> 0.4.beta0-1
- Add ipmimonitoring subpackage.

* Sun Jul 30 2006 Albert Chu <chu11@llnl.gov> 0.3.beta0-1
- Re-architect for 0.3.X

* Mon May 15 2006 Albert Chu <chu11@llnl.gov> 0.3.beta0-1
- Fixed up spec file to pass rpmlint
