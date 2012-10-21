%define _noarch_libdir /usr/lib 

%define rel_ver 0.7.2

Summary: A high-throughput distributed messaging system.
Name: kafka
Version: %{rel_ver}
Release: 1
License: Apache License v2.0
Group: Applications/Databases
URL: http://incubator.apache.org/kafka/
Source0: http://skottler.fedorapeople.org/kafka-%{rel_ver}.tar.gz
Source1: kafka.init
Source2: log4j.properties
Source3: server.properties
Source4: sysconfig
BuildRoot: %{_tmppath}/%{name}-%{rel_ver}-%{release}-root
BuildRequires: java-1.7.0-openjdk-devel
Requires: java-1.7.0-openjdk
Requires(post): chkconfig initscripts
Requires(pre): chkconfig initscripts
AutoReqProv: no

%description

Apache Kafka is a distributed publish-subscribe messaging system. It
is designed to support the following:

* Persistent messaging with O(1) disk structures that provide constant
  time performance even with many TB of stored messages.

* High-throughput: even with very modest hardware Kafka can support
  hundreds of thousands of messages per second.

* Explicit support for partitioning messages over Kafka servers and
  distributing consumption over a cluster of consumer machines while
  maintaining per-partition ordering semantics.

* Support for parallel data load into Hadoop.

Kafka provides a publish-subscribe solution that can handle all
activity stream data and processing on a consumer-scale web site. This
kind of activity (page views, searches, and other user actions) are a
key ingredient in many of the social feature on the modern web. This
data is typically handled by "logging" and ad hoc log aggregation
solutions due to the throughput requirements. This kind of ad hoc
solution is a viable solution to providing logging data to an offline
analysis system like Hadoop, but is very limiting for building
real-time processing. Kafka aims to unify offline and online
processing by providing a mechanism for parallel load into Hadoop as
well as the ability to partition real-time consumption over a cluster
of machines.

The use for activity stream processing makes Kafka comparable to
Facebook's Scribe or Apache Flume (incubating), though the
architecture and primitives are very different for these systems and
make Kafka more comparable to a traditional messaging system. See our
design page for more details.

%define _kafka_noarch_libdir %{_noarch_libdir}/kafka

%prep
%setup -q -n kafka-%{rel_ver}

%build
./sbt update
./sbt package

head -n -1 bin/kafka-run-class.sh > run-class.sh
echo "exec \$JAVA \$KAFKA_OPTS \$KAFKA_JMX_OPTS -cp \$CLASSPATH \$@" >> run-class.sh
mv run-class.sh bin/kafka-run-class.sh
chmod +x bin/kafka-run-class.sh

%install
rm -rf %{buildroot}
install -p -d %{buildroot}%{_kafka_noarch_libdir}
cp -r bin core lib lib_managed project %{buildroot}%{_kafka_noarch_libdir}

mkdir -p %{buildroot}%{_sysconfdir}/kafka
install -p -D -m 755 %{S:1} %{buildroot}%{_initrddir}/kafka
install -p -D -m 644 %{S:2} %{buildroot}%{_sysconfdir}/kafka
install -p -D -m 644 %{S:3} %{buildroot}%{_sysconfdir}/kafka
install -p -D -m 644 %{S:4} %{buildroot}%{_sysconfdir}/sysconfig/kafka

install -d %{buildroot}%{_localstatedir}/lib/kafka
install -d %{buildroot}%{_localstatedir}/log/kafka

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README.md LICENSE NOTICE DISCLAIMER
%dir %attr(0750, kafka, kafka) %{_localstatedir}/lib/kafka
%dir %attr(0750, kafka, kafka) %{_localstatedir}/log/kafka
%{_kafka_noarch_libdir}
%{_initrddir}/kafka
%config(noreplace) %{_sysconfdir}/sysconfig/kafka
%config(noreplace) %{_sysconfdir}/kafka

%pre
getent group kafka >/dev/null || groupadd -r kafka
getent passwd kafka >/dev/null || useradd -r -g kafka -d / -s /sbin/nologin kafka
exit 0

%post
/sbin/chkconfig --add kafka

%preun
if [ $1 = 0 ] ; then
  /sbin/service kafka stop >/dev/null 2>&1
  /sbin/chkconfig --del kafka
fi

%postun
if [ "$1" -ge "1" ] ; then
  /sbin/service kafka condrestart >/dev/null 2>&1 || :
fi

%changelog
* Thu Oct 03 2012  Sam Kottler <sam@kottlerdevelopment.com> - 0.7.0-1
- Initial package creation.
