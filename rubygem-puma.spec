%global gem_name puma
%bcond_with ragel
Name:                rubygem-%{gem_name}
Version:             3.12.4
Release:             1
Summary:             A simple, fast, threaded, and highly concurrent HTTP 1.1 server
License:             BSD
URL:                 http://puma.io
Source0:             https://rubygems.org/gems/%{gem_name}-%{version}.gem
Source1:             https://github.com/puma/%{gem_name}/archive/v%{version}.tar.gz
# Set the default cipher list "PROFILE=SYSTEM".
# https://fedoraproject.org/wiki/Packaging:CryptoPolicies
Patch2:              rubygem-puma-3.6.0-fedora-crypto-policy-cipher-list.patch
BuildRequires:       openssl-devel ruby(release) rubygems-devel ruby-devel rubygem(rack)
BuildRequires:       rubygem(minitest)
%if %{with ragel}
BuildRequires:       %{_bindir}/ragel
%endif
BuildRequires:       gcc
%description
A simple, fast, threaded, and highly concurrent HTTP 1.1 server for
Ruby/Rack applications.

%package doc
Summary:             Documentation for %{name}
Requires:            %{name} = %{version}-%{release}
BuildArch:           noarch
%description doc
Documentation for %{name}.

%prep
%setup -q -n  %{gem_name}-%{version} -b 1
%patch2 -p1
%if %{with ragel}
rm -f ext/puma_http11/http11_parser.c
ragel ext/puma_http11/http11_parser.rl -C -G2 -I ext/puma_http11 \
  -o ext/puma_http11/http11_parser.c
%endif

%build
gem build ../%{gem_name}-%{version}.gemspec
%gem_install

%install
mkdir -p %{buildroot}%{gem_dir}
cp -a .%{gem_dir}/* \
        %{buildroot}%{gem_dir}/
mkdir -p %{buildroot}%{gem_extdir_mri}/puma
cp -a .%{gem_extdir_mri}/gem.build_complete %{buildroot}%{gem_extdir_mri}/
cp -a .%{gem_extdir_mri}/puma/*.so %{buildroot}%{gem_extdir_mri}/puma
rm -rf %{buildroot}%{gem_instdir}/ext/
mkdir -p %{buildroot}%{_bindir}
cp -a .%{_bindir}/* \
        %{buildroot}%{_bindir}/
find %{buildroot}%{gem_instdir}/bin -type f | xargs chmod a+x
find %{buildroot}%{gem_instdir}/bin -type f | \
  xargs sed -i 's|^#!/usr/bin/env ruby$|#!/usr/bin/ruby|'

%check
pushd .%{gem_instdir}
ln -s %{_builddir}/%{gem_name}-%{version}/test test
ln -s %{_builddir}/%{gem_name}-%{version}/examples examples
sed -i "/require 'minitest\/retry'/ s/^/#/" test/helper.rb
sed -i "/Minitest::Retry/ s/^/#/" test/helper.rb
sed -i '/^  def test_timeout_in_data_phase$/a\
    skip "Unstable test"' test/test_puma_server.rb
sed -i '/^  def test_control_url$/a\
    skip "Unstable test"' test/test_pumactl.rb
sed -i '/^  def test_ssl_v3_rejection$/a\
    skip' test/test_puma_server_ssl.rb
sed -i '/^  def test_term_signal_exit_code_in_clustered_mode$/a\
    skip "Clustered server does not stop properly"' test/test_integration.rb
RUBYOPT="-Ilib:$(dirs +1 -l)%{gem_extdir_mri}" CI=1 ruby \
  -e 'Dir.glob "./test/**/test_*.rb", &method(:require)' \
  -- -v
RUBYOPT="-I$(dirs +1 -l)%{gem_extdir_mri}" ruby test/shell/run.rb
popd

%files
%dir %{gem_instdir}
%{_bindir}/puma
%{_bindir}/pumactl
%{gem_extdir_mri}
%license %{gem_instdir}/LICENSE
%{gem_instdir}/bin
%{gem_libdir}
%exclude %{gem_cache}
%{gem_spec}

%files doc
%doc %{gem_docdir}
%doc %{gem_instdir}/History.md
%doc %{gem_instdir}/README.md
%doc %{gem_instdir}/docs
%{gem_instdir}/tools

%changelog
* Thu Aug 20 2020 luoshengwei <luoshengwei@huawei.com> - 3.12.4-1
- package init
