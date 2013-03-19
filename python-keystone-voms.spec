# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%global commit 94adcbd255c50b9d4a7fa0784bffc4ce4a1f48bf
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           python-keystone-voms
Version:        1.0
Release:        1%{?dist}
Summary:        VOMS module for OpenStack Keystone

License:        APLv2
URL:            https://github.com/IFCA/keystone-voms
Source0:        https://github.com/alvarolopez/keystone-voms/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel

%description
Virtual Organization Membership Service external authentication module
for use with OpenStack Keystone (Grizzly).

%prep
%setup -qn %{name}-%{commit}


%build
# Remove CFLAGS=... for noarch packages (unneeded)
CFLAGS="%{optflags}" %{__python} setup.py build


%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

 
%files
%doc
# For noarch packages: sitelib
%{python_sitelib}/*
# For arch-specific packages: sitearch
%{python_sitearch}/*


%changelog
* Tue Mar 19 2013 Adam Huffman <a.huffman@imperial.ac.uk> - 1.0-1
- initial version

