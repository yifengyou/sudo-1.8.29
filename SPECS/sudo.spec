Summary: Allows restricted root access for specified users
Name: sudo
Version: 1.8.29
Release: 8%{?dist}
License: ISC
Group: Applications/System
URL: https://www.sudo.ws/

Source0: https://www.sudo.ws/dist/%{name}-%{version}.tar.gz
Source1: sudoers
Source2: sudo-ldap.conf
Source3: sudo.conf

Requires: /etc/pam.d/system-auth
Requires: /usr/bin/vi
Requires(post): /bin/chmod

BuildRequires: /usr/sbin/sendmail
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: bison
BuildRequires: flex
BuildRequires: gettext
BuildRequires: groff
BuildRequires: libtool
BuildRequires: audit-libs-devel
BuildRequires: libcap-devel
BuildRequires: libgcrypt-devel
BuildRequires: libselinux-devel
BuildRequires: openldap-devel
BuildRequires: pam-devel
BuildRequires: zlib-devel

# don't strip
Patch1: sudo-1.6.7p5-strip.patch
# 881258 - rpmdiff: added missing sudo-ldap.conf manpage
Patch2: sudo-1.8.23-sudoldapconfman.patch
# env debug patch
Patch3: sudo-1.7.2p1-envdebug.patch
# 1247591 - Sudo taking a long time when user information is stored externally.
Patch4: sudo-1.8.23-legacy-group-processing.patch
# 840980 - sudo creates a new parent process
# Adds cmnd_no_wait Defaults option
Patch5: sudo-1.8.23-nowaitopt.patch
# 1312486 - RHEL7 sudo logs username "root" instead of realuser in /var/log/secure
Patch6: sudo-1.8.6p7-logsudouser.patch
# 1786987 - CVE-2019-19232 sudo: attacker with access to a Runas ALL sudoer account
# can impersonate a nonexistent user [rhel-8]
Patch7: sudo-1.8.29-CVE-2019-19232.patch
# 1796518 - [RFE] add optional check for the target user shell
Patch8: sudo-1.8.29-CVE-2019-19234.patch
# 1798093 - CVE-2019-18634 sudo: Stack based buffer overflow in when pwfeedback is enabled [rhel-8.2.0]
Patch9: sudo-1.8.29-CVE-2019-18634.patch

# 1815164 - sudo allows privilege escalation with expire password
Patch10: sudo-1.8.29-expired-password-part1.patch
Patch11: sudo-1.8.29-expired-password-part2.patch

# 1917734 - EMBARGOED CVE-2021-3156 sudo: Heap-buffer overflow in argument parsing [rhel-8.4.0]
Patch12: sudo-1.8.31-CVE-2021-3156.patch
# 1916434 - CVE-2021-23239 sudo: possible directory existence test due to race condition in sudoedit [rhel-8]
Patch13: sudo-1.9.5-CVE-2021-23239.patch
# 1917038 - CVE-2021-23240 sudo: symbolic link attack in SELinux-enabled sudoedit [rhel-8]
Patch14: sudo-1.9.5-CVE-2021-23240-1.patch
Patch15: sudo-1.9.5-CVE-2021-23240-2.patch
Patch16: sudo-1.9.5-CVE-2021-23240-3.patch
Patch17: sudo-1.9.5-CVE-2021-23240-4.patch
Patch18: sudo-1.9.5-CVE-2021-23240-5.patch

# 2029551 - sudoedit does not work with selinux args
Patch19: sudo-1.9.5-sudoedit-selinux.patch
# 1999751 - Request to backport https://www.sudo.ws/repos/sudo/rev/b4c91a0f72e7 to RHEL 8
Patch20: sudo-1.9.7-sigchild.patch
# 1917379 - [RFE] pass KRB5CCNAME to pam_authenticate environment if available
Patch21: sudo-1.9.7-krb5ccname.patch
# 1986572 - utmp resource leak in sudo
Patch22: sudo-1.9.7-utmp-leak.patch

%description
Sudo (superuser do) allows a system administrator to give certain
users (or groups of users) the ability to run some (or all) commands
as root while logging all commands and arguments. Sudo operates on a
per-command basis.  It is not a replacement for the shell.  Features
include: the ability to restrict what commands a user may run on a
per-host basis, copious logging of each command (providing a clear
audit trail of who did what), a configurable timeout of the sudo
command, and the ability to use the same configuration file (sudoers)
on many different machines.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description    devel
The %{name}-devel package contains header files developing sudo
plugins that use %{name}.

%prep
%setup -q

%patch1 -p1 -b .strip
%patch2 -p1 -b .sudoldapconfman
%patch3 -p1 -b .env-debug
%patch4 -p1 -b .legacy-processing
%patch5 -p1 -b .nowait
%patch6 -p1 -b .logsudouser
%patch7 -p1 -b .CVE-2019-19232
%patch8 -p1 -b .target-shell
%patch9 -p1 -b .CVE-2019-18634

%patch10 -p1 -b .expired1
%patch11 -p1 -b .expired2

%patch12 -p1 -b .heap-buffer

%patch13 -p1 -b .sudoedit-race

%patch14 -p1 -b .symbolic-link-attack-1
%patch15 -p1 -b .symbolic-link-attack-2
%patch16 -p1 -b .symbolic-link-attack-3
%patch17 -p1 -b .symbolic-link-attack-4
%patch18 -p1 -b .symbolic-link-attack-5

%patch19 -p1 -b .sudoedit-selinux

%patch20 -p1 -b .sigchild
%patch21 -p1 -b .krb5ccname
%patch22 -p1 -b .utmp-leak

%build
# Remove bundled copy of zlib
rm -rf zlib/
autoreconf -I m4 -fv --install

%ifarch s390 s390x sparc64
F_PIE=-fPIE
%else
F_PIE=-fpie
%endif

export CFLAGS="$RPM_OPT_FLAGS $F_PIE" LDFLAGS="-pie -Wl,-z,relro -Wl,-z,now"

%configure \
        --prefix=%{_prefix} \
        --sbindir=%{_sbindir} \
        --libdir=%{_libdir} \
        --docdir=%{_pkgdocdir} \
        --disable-root-mailer \
        --with-logging=syslog \
        --with-logfac=authpriv \
        --with-pam \
        --with-pam-login \
        --with-editor=/bin/vi \
        --with-env-editor \
        --with-ignore-dot \
        --with-tty-tickets \
        --with-ldap \
        --with-ldap-conf-file="%{_sysconfdir}/sudo-ldap.conf" \
        --with-selinux \
        --with-passprompt="[sudo] password for %p: " \
        --with-linux-audit \
        --with-sssd
#       --without-kerb5 \
#       --without-kerb4
make

%check
make check

%install
rm -rf $RPM_BUILD_ROOT

# Update README.LDAP (#736653)
sed -i 's|/etc/ldap\.conf|%{_sysconfdir}/sudo-ldap.conf|g' README.LDAP

make install DESTDIR="$RPM_BUILD_ROOT" install_uid=`id -u` install_gid=`id -g` sudoers_uid=`id -u` sudoers_gid=`id -g`
chmod 755 $RPM_BUILD_ROOT%{_bindir}/* $RPM_BUILD_ROOT%{_sbindir}/*
install -p -d -m 700 $RPM_BUILD_ROOT/var/db/sudo
install -p -d -m 700 $RPM_BUILD_ROOT/var/db/sudo/lectured
install -p -d -m 750 $RPM_BUILD_ROOT/etc/sudoers.d
install -p -c -m 0440 %{SOURCE1} $RPM_BUILD_ROOT/etc/sudoers
install -p -c -m 0640 %{SOURCE3} $RPM_BUILD_ROOT/etc/sudo.conf
install -p -c -m 0640 %{SOURCE2} $RPM_BUILD_ROOT/%{_sysconfdir}/sudo-ldap.conf

# Add sudo to protected packages
install -p -d -m 755 $RPM_BUILD_ROOT/etc/dnf/protected.d/
touch sudo.conf
echo sudo > sudo.conf
install -p -c -m 0644 sudo.conf $RPM_BUILD_ROOT/etc/dnf/protected.d/
rm -f sudo.conf

chmod +x $RPM_BUILD_ROOT%{_libexecdir}/sudo/*.so # for stripping, reset in %%files

# Don't package LICENSE as a doc
rm -rf $RPM_BUILD_ROOT%{_pkgdocdir}/LICENSE

# Remove examples; Examples can be found in man pages too.
rm -rf $RPM_BUILD_ROOT%{_datadir}/examples/sudo

# Remove all .la files
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

# Remove sudoers.dist
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/sudoers.dist

%find_lang sudo
%find_lang sudoers

cat sudo.lang sudoers.lang > sudo_all.lang
rm sudo.lang sudoers.lang

mkdir -p $RPM_BUILD_ROOT/etc/pam.d
cat > $RPM_BUILD_ROOT/etc/pam.d/sudo << EOF
#%%PAM-1.0
auth       include      system-auth
account    include      system-auth
password   include      system-auth
session    include      system-auth
EOF

cat > $RPM_BUILD_ROOT/etc/pam.d/sudo-i << EOF
#%%PAM-1.0
auth       include      sudo
account    include      sudo
password   include      sudo
session    optional     pam_keyinit.so force revoke
session    include      sudo
EOF


%clean
rm -rf $RPM_BUILD_ROOT

%files -f sudo_all.lang
%defattr(-,root,root)
%attr(0440,root,root) %config(noreplace) /etc/sudoers
%attr(0640,root,root) %config(noreplace) /etc/sudo.conf
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/sudo-ldap.conf
%attr(0750,root,root) %dir /etc/sudoers.d/
%config(noreplace) /etc/pam.d/sudo
%config(noreplace) /etc/pam.d/sudo-i
%attr(0644,root,root) %{_tmpfilesdir}/sudo.conf
%attr(0644,root,root) /etc/dnf/protected.d/sudo.conf
%dir /var/db/sudo
%dir /var/db/sudo/lectured
%attr(4111,root,root) %{_bindir}/sudo
%{_bindir}/sudoedit
%{_bindir}/cvtsudoers
%attr(0111,root,root) %{_bindir}/sudoreplay
%attr(0755,root,root) %{_sbindir}/visudo
%dir %{_libexecdir}/sudo
%attr(0755,root,root) %{_libexecdir}/sudo/sesh
%attr(0644,root,root) %{_libexecdir}/sudo/sudo_noexec.so
%attr(0644,root,root) %{_libexecdir}/sudo/sudoers.so
%attr(0644,root,root) %{_libexecdir}/sudo/group_file.so
%attr(0644,root,root) %{_libexecdir}/sudo/system_group.so
%attr(0644,root,root) %{_libexecdir}/sudo/libsudo_util.so.?.?.?
%{_libexecdir}/sudo/libsudo_util.so.?
%{_libexecdir}/sudo/libsudo_util.so
%{_mandir}/man5/sudoers.5*
%{_mandir}/man5/sudoers.ldap.5*
%{_mandir}/man5/sudo-ldap.conf.5*
%{_mandir}/man5/sudo.conf.5*
%{_mandir}/man8/sudo.8*
%{_mandir}/man8/sudoedit.8*
%{_mandir}/man8/sudoreplay.8*
%{_mandir}/man8/visudo.8*
%{_mandir}/man1/cvtsudoers.1*
%{_mandir}/man5/sudoers_timestamp.5*
%dir %{_pkgdocdir}/
%{_pkgdocdir}/*
%{!?_licensedir:%global license %%doc}
%license doc/LICENSE
%exclude %{_pkgdocdir}/ChangeLog


# Make sure permissions are ok even if we're updating
%post
/bin/chmod 0440 /etc/sudoers || :

%files devel
%defattr(-,root,root,-)
%doc plugins/sample/sample_plugin.c
%{_includedir}/sudo_plugin.h
%{_mandir}/man8/sudo_plugin.8*

%changelog
* Mon Dec 06 2021 Radovan Sroka <rsroka@redhat.com> - 1.8.29-8
RHEL 8.6.0 ERRATUM
- sudoedit does not work with selinux args
Resolves: rhbz#2029551
- Make sure SIGCHLD is not ignored when sudo is executed
Resolves: rhbz#1999751
- [RFE] pass KRB5CCNAME to pam_authenticate environment if available
Resolves: rhbz#1917379
- utmp resource leak in sudo
Resolves: rhbz#1986572

* Tue Feb 02 2021 Radovan Sroka <rsroka@redhat.com> - 1.8.29-7
- RHEL 8.4 ERRATUM
- CVE-2021-3156
Resolves: rhbz#1917734
- CVE-2021-23239 sudo: possible directory existence test due to race condition in sudoedit
Resolves: rhzb#1916434
- CVE-2021-23240 sudo: symbolic link attack in SELinux-enabled sudoedit
Resolves: rhbz#1917038
- updated upstream url
Resolves: rhbz#1923825

* Tue Apr 28 2020 Radovan Sroka <rsroka@redhat.com> - 1.8.29-6
- RHEL 8.3 ERRATUM
- sudo allows privilege escalation with expire password
Resolves: rhbz#1815164

* Wed Feb 05 2020 Radovan Sroka <rsroka@redhat.com> - 1.8.29-5
- RHEL 8.2 ERRATUM
- CVE-2019-18634
Resolves: rhbz#1798093

* Tue Jan 14 2020 Radovan Sroka <rsroka@redhat.com> - 1.8.29-4
- RHEL 8.2 ERRATUM
- CVE-2019-19232
Resolves: rhbz#1786987
Resolves: rhbz#1796518

* Wed Oct 30 2019 Radovan Sroka <rsroka@redhat.com> - 1.8.29-2
- RHEL 8.2 ERRATUM
- rebase to 1.8.29
Resolves: rhbz#1733961
Resolves: rhbz#1651662

* Fri Oct 25 2019 Radovan Sroka <rsroka@redhat.com> - 1.8.28p1-1
- RHEL 8.2 ERRATUM
- rebase to 1.8.28p1
Resolves: rhbz#1733961
- fixed man page for always_set_home
Resolves: rhbz#1576880
- sudo does not work with notbefore/after
Resolves: rhbz#1679508
- NOTBEFORE showing value of sudoNotAfter Ldap attribute
Resolves: rhbz#1715516
- CVE-2019-14287 sudo
- Privilege escalation via 'Runas' specification with 'ALL' keyword
Resolves: rhbz#1760697

* Fri Aug 16 2019 Radovan Sroka <rsroka@redhat.com> - 1.8.25-7
- RHEL 8.1 ERRATUM
- sudo ipa_hostname not honored
Resolves: rhbz#1738662

* Mon Aug 12 2019 Radovan Sroka <rsroka@redhat.com> - 1.8.25-6
- RHEL 8.1 ERRATUM
- Fixed The LDAP backend which is not properly parsing sudoOptions,
  resulting in selinux roles not being applied
Resolves: rhbz#1738326

* Tue May 28 2019 Radovan Sroka <rsroka@redhat.com> - 1.8.25-5
- RHEL 8.1 ERRATUM
- Fixed problem with sudo-1.8.23 and 'who am i'
Resolves: rhbz#1673886
- Backporting sudo bug with expired passwords
Resolves: rhbz#1676819

* Tue Dec 11 2018 Radovan Sroka <rsroka@redhat.com> - 1.8.25-4
- Fix most of the man page scans problems
- Resolves: rhbz#1613327

* Fri Oct 12 2018 Daniel Kopecek <dkopecek@redhat.com> - 1.8.25-3
- bump release for new build
Resolves: rhbz#1625683

* Thu Oct 11 2018 Daniel Kopecek <dkopecek@redhat.com> - 1.8.25-2
- Depend explicitly on /usr/sbin/sendmail instead of sendmail (rhel-7 sync)
- Simplified pam configuration file by removing duplicate pam stack entries
Resolves: rhbz#1633144

* Wed Sep 26 2018 Radovan Sroka <rsroka@redhat.com> - 1.8.25-1
- rebase to the new upstream version 1.8.25p1
- sync patches with rhel-7.6
- sync sudoers with rhel-7.6
  resolves: rhbz#1633144

* Mon Sep 10 2018 Radovan Sroka <rsroka@redhat.com> - 1.8.23-2
- install /etc/dnf/protected.d/sudo instead of /etc/yum/protected.d/sudo
  resolves: rhbz#1626972

* Thu May 17 2018 Daniel Kopecek <dkopecek@redhat.com> - 1.8.23-1
- Packaging update for RHEL 8.0 (sync with latest RHEL 7 state)

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.22-0.2.b1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Dec 14 2017 Radovan Sroka <rsroka@redhat.com> - 1.8.22b1-1
- update to 1.8.22b1
- Added /usr/local/sbin and /usr/local/bin to secure path rhbz#1166185

* Thu Sep 21 2017 Marek Tamaskovic <mtamasko@redhat.com> - 1.8.21p2-1
- update to 1.8.21p2
- Moved libsudo_util.so from the -devel sub-package to main package (1481225)

* Wed Sep 06 2017 Matthew Miller <mattdm@fedoraproject.org> - 1.8.20p2-4
- replace file-based requirements with package-level ones:
- /etc/pam.d/system-auth to 'pam'
- /bin/chmod to 'coreutils' (bug #1488934)
- /usr/bin/vi to vim-minimal
- ... and make vim-minimal "recommends" instead of "requires", because
  other editors can be configured.

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.20p2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.20p2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jun 01 2017 Daniel Kopecek <dkopecek@redhat.com> 1.8.20p2-1
- update to 1.8.20p2

* Wed May 31 2017 Daniel Kopecek <dkopecek@redhat.com> 1.8.20p1-1
- update to 1.8.20p1
- fixes CVE-2017-1000367
  Resolves: rhbz#1456884

* Fri Apr 07 2017 Jiri Vymazal <jvymazal@redhat.com> - 1.8.20-0.1.b1
- update to latest development version 1.8.20b1
- added sudo to dnf/yum protected packages
  Resolves: rhbz#1418756

* Mon Feb 13 2017 Tomas Sykora <tosykora@redhat.com> - 1.8.19p2-1
- update to 1.8.19p2

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.19-0.3.20161108git738c3cb
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Nov 08 2016 Daniel Kopecek <dkopecek@redhat.com> 1.8.19-0.2.20161108git738c3cb
- update to latest development version
- fixes CVE-2016-7076

* Fri Sep 23 2016 Radovan Sroka <rsroka@redhat.com> 1.8.19-0.1.20160923git90e4538
- we were not able to update from rc and beta versions to stable one
- so this is a new snapshot package which resolves it

* Wed Sep 21 2016 Radovan Sroka <rsroka@redhat.com> 1.8.18-1
- update to 1.8.18

* Fri Sep 16 2016 Radovan Sroka <rsroka@redhat.com> 1.8.18rc4-1
- update to 1.8.18rc4

* Wed Sep 14 2016 Radovan Sroka <rsroka@redhat.com> 1.8.18rc2-1
- update to 1.8.18rc2
- dropped sudo-1.8.14p1-ldapconfpatch.patch
  upstreamed --> https://www.sudo.ws/pipermail/sudo-workers/2016-September/001006.html

* Fri Aug 26 2016 Radovan Sroka <rsroka@redhat.com> 1.8.18b2-1
- update to 1.8.18b2
- added --disable-root-mailer as configure option
  Resolves: rhbz#1324091

* Fri Jun 24 2016 Daniel Kopecek <dkopecek@redhat.com> 1.8.17p1-1
- update to 1.8.17p1
- install the /var/db/sudo/lectured
  Resolves: rhbz#1321414

* Tue May 31 2016 Daniel Kopecek <dkopecek@redhat.com> 1.8.16-4
- removed INPUTRC from env_keep to prevent a possible info leak
  Resolves: rhbz#1340701

* Fri May 13 2016 Daniel Kopecek <dkopecek@redhat.com> 1.8.16-3
- fixed upstream patch for rhbz#1328735

* Thu May 12 2016 Daniel Kopecek <dkopecek@redhat.com> 1.8.16-2
- fixed invalid sesh argument array construction

* Mon Apr 04 2016 Daniel Kopecek <dkopecek@redhat.com> 1.8.16-1
- update to 1.8.16

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.15-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Nov  5 2015 Daniel Kopecek <dkopecek@redhat.com> 1.8.15-1
- update to 1.8.15
- fixes CVE-2015-5602

* Mon Aug 24 2015 Radovan Sroka <rsroka@redhat.com> 1.8.14p3-3
- enable upstream test suite

* Mon Aug 24 2015 Radovan Sroka <rsroka@redhat.com> 1.8.14p3-2
- add patch that resolves initialization problem before sudo_strsplit call
- add patch that resolves deadcode in visudo.c
- add patch that removes extra while in visudo.c and sudoers.c

* Mon Jul 27 2015 Radovan Sroka <rsroka@redhat.com> 1.8.14p3-1
- update to 1.8.14p3

* Mon Jul 20 2015 Radovan Sroka <rsroka@redhat.com> 1.8.14p1-1
- update to 1.8.14p1-1
- rebase sudo-1.8.14b3-ldapconfpatch.patch -> sudo-1.8.14p1-ldapconfpatch.patch
- rebase sudo-1.8.14b4-docpassexpire.patch -> sudo-1.8.14p1-docpassexpire.patch

* Tue Jul 14 2015 Radovan Sroka <rsroka@redhat.com> 1.8.12-2
- add patch3 sudo.1.8.14b4-passexpire.patch that makes change in documentation about timestamp_time
- Resolves: rhbz#1162070

* Fri Jul 10 2015 Radovan Sroka <rsroka@redhat.com> - 1.8.14b4-1
- Update to 1.8.14b4
- Add own %%{_tmpfilesdir}/sudo.conf

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Feb 18 2015 Daniel Kopecek <dkopecek@redhat.com> - 1.8.12
- update to 1.8.12
- fixes CVE-2014-9680

* Mon Nov  3 2014 Daniel Kopecek <dkopecek@redhat.com> - 1.8.11p2-1
- update to 1.8.11p2
- added patch to fix upstream bug #671 -- exiting immediately
  when audit is disabled

* Tue Sep 30 2014 Daniel Kopecek <dkopecek@redhat.com> - 1.8.11-1
- update to 1.8.11
- major changes & fixes:
  - when running a command in the background, sudo will now forward
    SIGINFO to the command
  - the passwords in ldap.conf and ldap.secret may now be encoded in base64.
  - SELinux role changes are now audited. For sudoedit, we now audit
    the actual editor being run, instead of just the sudoedit command.
  - it is now possible to match an environment variable's value as well as
    its name using env_keep and env_check
  - new files created via sudoedit as a non-root user now have the proper group id
  - sudoedit now works correctly in conjunction with sudo's SELinux RBAC support
  - it is now possible to disable network interface probing in sudo.conf by
    changing the value of the probe_interfaces setting
  - when listing a user's privileges (sudo -l), the sudoers plugin will now prompt
    for the user's password even if the targetpw, rootpw or runaspw options are set.
  - the new use_netgroups sudoers option can be used to explicitly enable or disable
    netgroups support
  - visudo can now export a sudoers file in JSON format using the new -x flag
- added patch to read ldap.conf more closely to nss_ldap
- require /usr/bin/vi instead of vim-minimal
- include pam.d/system-auth in PAM session phase from pam.d/sudo
- include pam.d/sudo in PAM session phase from pam.d/sudo-i

* Tue Aug  5 2014 Tom Callaway <spot@fedoraproject.org> - 1.8.8-6
- fix license handling

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat May 31 2014 Peter Robinson <pbrobinson@fedoraproject.org> 1.8.8-4
- Drop ChangeLog, we ship NEWS

* Mon Mar 10 2014 Daniel Kopecek <dkopecek@redhat.com> - 1.8.8-3
- remove bundled copy of zlib before compilation
- drop the requiretty Defaults setting from sudoers

* Sat Jan 25 2014 Ville Skyttä <ville.skytta@iki.fi> - 1.8.8-2
- Own the %%{_libexecdir}/sudo dir.

* Mon Sep 30 2013 Daniel Kopecek <dkopecek@redhat.com> - 1.8.8-1
- update to 1.8.8
- major changes & fixes:
  - LDAP SASL support now works properly with Kerberos
  - root may no longer change its SELinux role without entering a password
  - user messages are now always displayed in the user's locale, even when
    the same message is being logged or mailed in a different locale.
  - log files created by sudo now explicitly have the group set to group
    ID 0 rather than relying on BSD group semantics
  - sudo now stores its libexec files in a sudo subdirectory instead of in
    libexec itself
  - system_group and group_file sudoers group provider plugins are now
    installed by default
  - the paths to ldap.conf and ldap.secret may now be specified as arguments
    to the sudoers plugin in the sudo.conf file
  - ...and many new features and settings. See the upstream ChangeLog for the
    full list.
- several sssd support fixes
- added patch to make uid/gid specification parsing more strict (don't accept
  an invalid number as uid/gid)
- use the _pkgdocdir macro
  (see https://fedoraproject.org/wiki/Changes/UnversionedDocdirs)
- fixed several bugs found by the clang static analyzer
- added %%post dependency on chmod

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.6p7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 28 2013 Daniel Kopecek <dkopecek@redhat.com> - 1.8.6p7-1
- update to 1.8.6p7
- fixes CVE-2013-1775 and CVE-2013-1776
- fixed several packaging issues (thanks to ville.skytta@iki.fi)
  - build with system zlib.
  - let rpmbuild strip libexecdir/*.so.
  - own the %%{_docdir}/sudo-* dir.
  - fix some rpmlint warnings (spaces vs tabs, unescaped macros).
  - fix bogus %%changelog dates.

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.6p3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Nov 12 2012 Daniel Kopecek <dkopecek@redhat.com> - 1.8.6p3-2
- added upstream patch for a regression
- don't include arch specific files in the -devel subpackage
- ship only one sample plugin in the -devel subpackage

* Tue Sep 25 2012 Daniel Kopecek <dkopecek@redhat.com> - 1.8.6p3-1
- update to 1.8.6p3
- drop -pipelist patch (fixed in upstream)

* Thu Sep  6 2012 Daniel Kopecek <dkopecek@redhat.com> - 1.8.6-1
- update to 1.8.6

* Thu Jul 26 2012 Daniel Kopecek <dkopecek@redhat.com> - 1.8.5-4
- added patches that fix & improve SSSD support (thanks to pbrezina@redhat.com)
- re-enabled SSSD support
- removed libsss_sudo dependency

* Tue Jul 24 2012 Bill Nottingham <notting@redhat.com> - 1.8.5-3
- flip sudoers2ldif executable bit after make install, not in setup

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu May 17 2012 Daniel Kopecek <dkopecek@redhat.com> - 1.8.5-1
- update to 1.8.5
- fixed CVE-2012-2337
- temporarily disabled SSSD support

* Wed Feb 29 2012 Daniel Kopecek <dkopecek@redhat.com> - 1.8.3p1-6
- fixed problems with undefined symbols (rhbz#798517)

* Wed Feb 22 2012 Daniel Kopecek <dkopecek@redhat.com> - 1.8.3p1-5
- SSSD patch update

* Tue Feb  7 2012 Daniel Kopecek <dkopecek@redhat.com> - 1.8.3p1-4
- added SSSD support

* Thu Jan 26 2012 Daniel Kopecek <dkopecek@redhat.com> - 1.8.3p1-3
- added patch for CVE-2012-0809

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.3p1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Nov 10 2011 Daniel Kopecek <dkopecek@redhat.com> - 1.8.3p1-1
- update to 1.8.3p1
- disable output word wrapping if the output is piped

* Wed Sep  7 2011 Peter Robinson <pbrobinson@fedoraproject.org> - 1.8.1p2-2
- Remove execute bit from sample script in docs so we don't pull in perl

* Tue Jul 12 2011 Daniel Kopecek <dkopecek@redhat.com> - 1.8.1p2-1
- rebase to 1.8.1p2
- removed .sudoi patch
- fixed typo: RELPRO -> RELRO
- added -devel subpackage for the sudo_plugin.h header file
- use default ldap configuration files again

* Fri Jun  3 2011 Daniel Kopecek <dkopecek@redhat.com> - 1.7.4p5-4
- build with RELRO

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.4p5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 17 2011 Daniel Kopecek <dkopecek@redhat.com> - 1.7.4p5-2
- rebase to 1.7.4p5
- fixed sudo-1.7.4p4-getgrouplist.patch
- fixes CVE-2011-0008, CVE-2011-0010

* Tue Nov 30 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.4p4-5
- anybody in the wheel group has now root access (using password) (rhbz#656873)
- sync configuration paths with the nss_ldap package (rhbz#652687)

* Wed Sep 29 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.4p4-4
- added upstream patch to fix rhbz#638345

* Mon Sep 20 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.4p4-3
- added patch for #635250
- /var/run/sudo -> /var/db/sudo in .spec

* Tue Sep  7 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.4p4-2
- sudo now uses /var/db/sudo for timestamps

* Tue Sep  7 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.4p4-1
- update to new upstream version
- new command available: sudoreplay
- use native audit support
- corrected license field value: BSD -> ISC

* Wed Jun  2 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.2p6-2
- added patch that fixes insufficient environment sanitization issue (#598154)

* Wed Apr 14 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.2p6-1
- update to new upstream version
- merged .audit and .libaudit patch
- added sudoers.ldap.5* to files

* Mon Mar  1 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.2p5-2
- update to new upstream version

* Tue Feb 16 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.2p2-5
- fixed no valid sudoers sources found (#558875)

* Wed Feb 10 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.2p2-4
- audit related Makefile.in and configure.in corrections
- added --with-audit configure option
- removed call to libtoolize

* Wed Feb 10 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.2p2-3
- fixed segfault when #include directive is used in cycles (#561336)

* Fri Jan  8 2010 Ville Skyttä <ville.skytta@iki.fi> - 1.7.2p2-2
- Add /etc/sudoers.d dir and use it in default config (#551470).
- Drop *.pod man page duplicates from docs.

* Thu Jan 07 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.7.2p2-1
- new upstream version 1.7.2p2-1
- commented out unused aliases in sudoers to make visudo happy (#550239)

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.7.1-7
- rebuilt with new audit

* Thu Aug 20 2009 Daniel Kopecek <dkopecek@redhat.com> 1.7.1-6
- moved secure_path from compile-time option to sudoers file (#517428)

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 09 2009 Daniel Kopecek <dkopecek@redhat.com> 1.7.1-4
- moved the closefrom() call before audit_help_open() (sudo-1.7.1-auditfix.patch)
- epoch number sync

* Mon Jun 22 2009 Daniel Kopecek <dkopecek@redhat.com> 1.7.1-1
- updated sudo to version 1.7.1
- fixed small bug in configure.in (sudo-1.7.1-conffix.patch)

* Tue Feb 24 2009 Daniel Kopecek <dkopecek@redhat.com> 1.6.9p17-6
- fixed building with new libtool
- fix for incorrect handling of groups in Runas_User
- added /usr/local/sbin to secure-path

* Tue Jan 13 2009 Daniel Kopecek <dkopecek@redhat.com> 1.6.9p17-3
- build with sendmail installed
- Added /usr/local/bin to secure-path

* Tue Sep 02 2008 Peter Vrabec <pvrabec@redhat.com> 1.6.9p17-2
- adjust audit patch, do not scream when kernel is
  compiled without audit netlink support (#401201)

* Fri Jul 04 2008 Peter Vrabec <pvrabec@redhat.com> 1.6.9p17-1
- upgrade

* Wed Jun 18 2008 Peter Vrabec <pvrabec@redhat.com> 1.6.9p13-7
- build with newer autoconf-2.62 (#449614)

* Tue May 13 2008 Peter Vrabec <pvrabec@redhat.com> 1.6.9p13-6
- compiled with secure path (#80215)

* Mon May 05 2008 Peter Vrabec <pvrabec@redhat.com> 1.6.9p13-5
- fix path to updatedb in /etc/sudoers (#445103)

* Mon Mar 31 2008 Peter Vrabec <pvrabec@redhat.com> 1.6.9p13-4
- include ldap files in rpm package (#439506)

* Thu Mar 13 2008 Peter Vrabec <pvrabec@redhat.com> 1.6.9p13-3
- include [sudo] in password prompt (#437092)

* Tue Mar 04 2008 Peter Vrabec <pvrabec@redhat.com> 1.6.9p13-2
- audit support improvement

* Thu Feb 21 2008 Peter Vrabec <pvrabec@redhat.com> 1.6.9p13-1
- upgrade to the latest upstream release

* Wed Feb 06 2008 Peter Vrabec <pvrabec@redhat.com> 1.6.9p12-1
- upgrade to the latest upstream release
- add selinux support

* Mon Feb 04 2008 Dennis Gilmore <dennis@ausil.us> 1.6.9p4-6
- sparc64 needs to be in the -fPIE list with s390

* Mon Jan 07 2008 Peter Vrabec <pvrabec@redhat.com> 1.6.9p4-5
- fix complains about audit_log_user_command(): Connection
  refused (#401201)

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org> - 1.6.9p4-4
- Rebuild for deps

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org> - 1.6.9p4-3
- Rebuild for openssl bump

* Thu Aug 30 2007 Peter Vrabec <pvrabec@redhat.com> 1.6.9p4-2
- fix autotools stuff and add audit support

* Mon Aug 20 2007 Peter Vrabec <pvrabec@redhat.com> 1.6.9p4-1
- upgrade to upstream release

* Thu Apr 12 2007 Peter Vrabec <pvrabec@redhat.com> 1.6.8p12-14
- also use getgrouplist() to determine group membership (#235915)

* Mon Feb 26 2007 Peter Vrabec <pvrabec@redhat.com> 1.6.8p12-13
- fix some spec file issues

* Thu Dec 14 2006 Peter Vrabec <pvrabec@redhat.com> 1.6.8p12-12
- fix rpmlint issue

* Thu Oct 26 2006 Peter Vrabec <pvrabec@redhat.com> 1.6.8p12-11
- fix typo in sudoers file (#212308)

* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> - 1.6.8p12-10
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Thu Sep 21 2006 Peter Vrabec <pvrabec@redhat.com> 1.6.8p12-9
- fix sudoers file, X apps didn't work (#206320)

* Tue Aug 08 2006 Peter Vrabec <pvrabec@redhat.com> 1.6.8p12-8
- use Red Hat specific default sudoers file

* Sun Jul 16 2006 Karel Zak <kzak@redhat.com> 1.6.8p12-7
- fix #198755 - make login processes (sudo -i) initialise session keyring
  (thanks for PAM config files to David Howells)
- add IPv6 support (patch by Milan Zazrivec)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.6.8p12-6.1
- rebuild

* Mon May 29 2006 Karel Zak <kzak@redhat.com> 1.6.8p12-6
- fix #190062 - "ssh localhost sudo su" will show the password in clear

* Tue May 23 2006 Karel Zak <kzak@redhat.com> 1.6.8p12-5
- add LDAP support (#170848)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.6.8p12-4.1
- bump again for double-long bug on ppc(64)

* Wed Feb  8 2006 Karel Zak <kzak@redhat.com> 1.6.8p12-4
- reset env. by default

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.6.8p12-3.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Jan 23 2006 Dan Walsh <dwalsh@redhat.com> 1.6.8p12-3
- Remove selinux patch.  It has been decided that the SELinux patch for sudo is
- no longer necessary.  In tageted policy it had no effect.  In strict/MLS policy
- We require the person using sudo to execute newrole before using sudo.

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Nov 25 2005 Karel Zak <kzak@redhat.com> 1.6.8p12-1
- new upstream version 1.6.8p12

* Tue Nov  8 2005 Karel Zak <kzak@redhat.com> 1.6.8p11-1
- new upstream version 1.6.8p11

* Thu Oct 13 2005 Tomas Mraz <tmraz@redhat.com> 1.6.8p9-6
- use include instead of pam_stack in pam config

* Tue Oct 11 2005 Karel Zak <kzak@redhat.com> 1.6.8p9-5
- enable interfaces in selinux patch
- merge sudo-1.6.8p8-sesh-stopsig.patch to selinux patch

* Mon Sep 19 2005 Karel Zak <kzak@redhat.com> 1.6.8p9-4
- fix debuginfo

* Mon Sep 19 2005 Karel Zak <kzak@redhat.com> 1.6.8p9-3
- fix #162623 - sesh hangs when child suspends

* Mon Aug 1 2005 Dan Walsh <dwalsh@redhat.com> 1.6.8p9-2
- Add back in interfaces call, SELinux has been fixed to work around

* Tue Jun 21 2005 Karel Zak <kzak@redhat.com> 1.6.8p9-1
- new version 1.6.8p9 (resolve #161116 - CAN-2005-1993 sudo trusted user arbitrary command execution)

* Tue May 24 2005 Karel Zak <kzak@redhat.com> 1.6.8p8-2
- fix #154511 - sudo does not use limits.conf

* Mon Apr  4 2005 Thomas Woerner <twoerner@redhat.com> 1.6.8p8-1
- new version 1.6.8p8: new sudoedit and sudo_noexec

* Wed Feb  9 2005 Thomas Woerner <twoerner@redhat.com> 1.6.7p5-31
- rebuild

* Mon Oct  4 2004 Thomas Woerner <twoerner@redhat.com> 1.6.7p5-30.1
- added missing BuildRequires for libselinux-devel (#132883)

* Wed Sep 29 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-30
- Fix missing param error in sesh

* Mon Sep 27 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-29
- Remove full patch check from sesh

* Thu Jul 8 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-28
- Fix selinux patch to switch to root user

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Apr 13 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-26
- Eliminate tty handling from selinux

* Thu Apr  1 2004 Thomas Woerner <twoerner@redhat.com> 1.6.7p5-25
- fixed spec file: sesh in file section with selinux flag (#119682)

* Tue Mar 30 2004 Colin Walters <walters@redhat.com> 1.6.7p5-24
- Enhance sesh.c to fork/exec children itself, to avoid
  having sudo reap all domains.
- Only reinstall default signal handlers immediately before
  exec of child with SELinux patch

* Thu Mar 18 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-23
- change to default to sysadm_r
- Fix tty handling

* Thu Mar 18 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-22
- Add /bin/sesh to run selinux code.
- replace /bin/bash -c with /bin/sesh

* Tue Mar 16 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-21
- Hard code to use "/bin/bash -c" for selinux

* Tue Mar 16 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-20
- Eliminate closing and reopening of terminals, to match su.

* Mon Mar 15 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-19
- SELinux fixes to make transitions work properly

* Fri Mar  5 2004 Thomas Woerner <twoerner@redhat.com> 1.6.7p5-18
- pied sudo

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jan 27 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-16
- Eliminate interfaces call, since this requires big SELinux privs
- and it seems to be useless.

* Tue Jan 27 2004 Karsten Hopp <karsten@redhat.de> 1.6.7p5-15
- visudo requires vim-minimal or setting EDITOR to something useful (#68605)

* Mon Jan 26 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-14
- Fix is_selinux_enabled call

* Tue Jan 13 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-13
- Clean up patch on failure

* Tue Jan 6 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-12
- Remove sudo.te for now.

* Fri Jan 2 2004 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-11
- Fix usage message

* Mon Dec 22 2003 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-10
- Clean up sudo.te to not blow up if pam.te not present

* Thu Dec 18 2003 Thomas Woerner <twoerner@redhat.com>
- added missing BuildRequires for groff

* Tue Dec 16 2003 Jeremy Katz <katzj@redhat.com> 1.6.7p5-9
- remove left-over debugging code

* Tue Dec 16 2003 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-8
- Fix terminal handling that caused Sudo to exit on non selinux machines.

* Mon Dec 15 2003 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-7
- Remove sudo_var_run_t which is now pam_var_run_t

* Fri Dec 12 2003 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-6
- Fix terminal handling and policy

* Thu Dec 11 2003 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-5
- Fix policy

* Thu Nov 13 2003 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-4.sel
- Turn on SELinux support

* Tue Jul 29 2003 Dan Walsh <dwalsh@redhat.com> 1.6.7p5-3
- Add support for SELinux

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon May 19 2003 Thomas Woerner <twoerner@redhat.com> 1.6.7p5-1

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Nov 12 2002 Nalin Dahyabhai <nalin@redhat.com> 1.6.6-2
- remove absolute path names from the PAM configuration, ensuring that the
  right modules get used for whichever arch we're built for
- don't try to install the FAQ, which isn't there any more

* Thu Jun 27 2002 Bill Nottingham <notting@redhat.com> 1.6.6-1
- update to 1.6.6

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Apr 18 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.6.5p2-2
- Fix bug #63768

* Thu Mar 14 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.6.5p2-1
- 1.6.5p2

* Fri Jan 18 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.6.5p1-1
- 1.6.5p1
- Hope this "a new release per day" madness stops ;)

* Thu Jan 17 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.6.5-1
- 1.6.5

* Tue Jan 15 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.6.4p1-1
- 1.6.4p1

* Mon Jan 14 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.6.4-1
- Update to 1.6.4

* Mon Jul 23 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.6.3p7-2
- Add build requirements (#49706)
- s/Copyright/License/
- bzip2 source

* Sat Jun 16 2001 Than Ngo <than@redhat.com>
- update to 1.6.3p7
- use %%{_tmppath}

* Fri Feb 23 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.6.3p6, fixes buffer overrun

* Tue Oct 10 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.6.3p5

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Tue Jun 06 2000 Karsten Hopp <karsten@redhat.de>
- fixed owner of sudo and visudo

* Thu Jun  1 2000 Nalin Dahyabhai <nalin@redhat.com>
- modify PAM setup to use system-auth
- clean up buildrooting by using the makeinstall macro

* Tue Apr 11 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- initial build in main distrib
- update to 1.6.3
- deal with compressed man pages

* Tue Dec 14 1999 Preston Brown <pbrown@redhat.com>
- updated to 1.6.1 for Powertools 6.2
- config files are now noreplace.

* Thu Jul 22 1999 Tim Powers <timp@redhat.com>
- updated to 1.5.9p2 for Powertools 6.1

* Wed May 12 1999 Bill Nottingham <notting@redhat.com>
- sudo is configured with pam. There's no pam.d file. Oops.

* Mon Apr 26 1999 Preston Brown <pbrown@redhat.com>
- upgraded to 1.59p1 for powertools 6.0

* Tue Oct 27 1998 Preston Brown <pbrown@redhat.com>
- fixed so it doesn't find /usr/bin/vi first, but instead /bin/vi (always installed)

* Thu Oct 08 1998 Michael Maher <mike@redhat.com>
- built package for 5.2

* Mon May 18 1998 Michael Maher <mike@redhat.com>
- updated SPEC file

* Thu Jan 29 1998 Otto Hammersmith <otto@redhat.com>
- updated to 1.5.4

* Tue Nov 18 1997 Otto Hammersmith <otto@redhat.com>
- built for glibc, no problems

* Fri Apr 25 1997 Michael Fulbright <msf@redhat.com>
- Fixed for 4.2 PowerTools
- Still need to be pamified
- Still need to move stmp file to /var/log

* Mon Feb 17 1997 Michael Fulbright <msf@redhat.com>
- First version for PowerCD.
