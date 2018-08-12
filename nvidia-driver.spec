%global debug_package %{nil}
%global __strip /bin/true

# RHEL 6 does not have _udevrulesdir defined
%if 0%{?rhel} == 6
%global _udevrulesdir   %{_prefix}/lib/udev/rules.d/
%global _dracutopts     nouveau.modeset=0 rdblacklist=nouveau
%global _dracutopts_rm  nomodeset vga=normal
%global _dracut_conf_d  %{_sysconfdir}/dracut.conf.d
%global _modprobe_d     %{_sysconfdir}/modprobe.d/
%global _grubby         /sbin/grubby --grub --update-kernel=ALL

# Prevent nvidia-driver-libs being pulled in place of mesa
%{?filter_setup:
%filter_provides_in %{_libdir}/nvidia
%filter_requires_in %{_libdir}/nvidia
%filter_setup
}
%endif

%if 0%{?rhel} == 7
%global _dracutopts     nouveau.modeset=0 rd.driver.blacklist=nouveau
%global _dracutopts_rm  nomodeset gfxpayload=vga=normal
%global _dracut_conf_d  %{_prefix}/lib/dracut.conf.d
%global _modprobe_d     %{_prefix}/lib/modprobe.d/
%global _grubby         %{_sbindir}/grubby --update-kernel=ALL
%endif

# Fedora 25+ has a fallback service where it tries to load nouveau if nvidia is
# not loaded, so don't disable it. Just matching the driver with OutputClass in
# the X.org configuration is enough to load the whole Nvidia stack or the Mesa
# one.
%if 0%{?fedora}
%global _dracutopts     rd.driver.blacklist=nouveau
%global _dracutopts_rm  nomodeset gfxpayload=vga=normal nouveau.modeset=0
%global _dracut_conf_d  %{_prefix}/lib/dracut.conf.d
%global _modprobe_d     %{_prefix}/lib/modprobe.d/
%global _grubby         %{_sbindir}/grubby --update-kernel=ALL
%endif

Name:           nvidia-driver
Version:        340.107
Release:        1%{?dist}
Summary:        NVIDIA's proprietary display driver for NVIDIA graphic cards
Epoch:          2
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html
ExclusiveArch:  %{ix86} x86_64

Source0:        %{name}-%{version}-i386.tar.xz
Source1:        %{name}-%{version}-x86_64.tar.xz
# For servers up to 1.19.0-3
Source10:       99-nvidia-modules.conf
# For servers from 1.16 to 1.19.0-3
Source11:       10-nvidia-driver.conf
# For unreleased Fedora versions
Source12:       99-nvidia-ignoreabi.conf
# For servers 1.19.0-3+
Source13:       10-nvidia.conf

Source20:       nvidia.conf
Source21:       60-nvidia.rules
Source22:       60-nvidia-uvm.rules
Source23:       nvidia-uvm.conf

Source40:       com.nvidia.driver.metainfo.xml
Source41:       parse-readme.py

# Auto-fallback to nouveau, requires server 1.19.0-3+, glvnd enabled mesa
Source50:       nvidia-fallback.service
Source51:       95-nvidia-fallback.preset

Source99:       nvidia-generate-tarballs.sh

BuildRequires:  python

# For execstack removal
%if 0%{?fedora} >= 23 || 0%{?rhel} > 7
BuildRequires:  execstack
%else
BuildRequires:  prelink
%endif

%if 0%{?fedora} || 0%{?rhel} >= 7
# UDev rule location (_udevrulesdir) and systemd macros
BuildRequires:  systemd
%endif

%if 0%{?fedora}
# AppStream metadata generation
BuildRequires:  libappstream-glib%{?_isa} >= 0.6.3
%endif

Requires:       grubby
Requires:       nvidia-driver-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}
Requires:       nvidia-kmod = %{?epoch:%{epoch}:}%{version}
Provides:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
Requires:       libva-vdpau-driver%{?_isa}

%if 0%{?rhel} == 6
Requires:       xorg-x11-server-Xorg%{?_isa}
%endif

%if 0%{?rhel} == 7
# X.org "OutputClass"
Requires:       xorg-x11-server-Xorg%{?_isa} >= 1.16
%endif

%if 0%{?fedora} >= 25
# Extended "OutputClass" with device options
Requires:       xorg-x11-server-Xorg%{?_isa} >= 1.19.0-3
# For auto-fallback to nouveau systemd service
%{?systemd_requires}
%endif

Conflicts:      catalyst-x11-drv
Conflicts:      catalyst-x11-drv-legacy
Conflicts:      cuda-drivers
Conflicts:      fglrx-x11-drv
Conflicts:      nvidia-x11-drv
Conflicts:      nvidia-x11-drv-173xx
Conflicts:      nvidia-x11-drv-304xx
Conflicts:      nvidia-x11-drv-340xx
Conflicts:      xorg-x11-drv-nvidia
Conflicts:      xorg-x11-drv-nvidia-173xx
Conflicts:      xorg-x11-drv-nvidia-304xx
Conflicts:      xorg-x11-drv-nvidia-340xx

%description
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with NVIDIA chipsets GeForce8 series and newer.
GeForce5 and below are NOT supported by this release.

For the full product support list, please consult the release notes for driver
version %{version}.

%package libs
Summary:        Libraries for %{name}
Requires(post): ldconfig
Requires:       libvdpau%{?_isa} >= 0.5

Conflicts:      nvidia-x11-drv-libs
Conflicts:      nvidia-x11-drv-libs-96xx
Conflicts:      nvidia-x11-drv-libs-173xx
Conflicts:      nvidia-x11-drv-libs-304xx
Conflicts:      nvidia-x11-drv-libs-340xx
Conflicts:      xorg-x11-drv-nvidia-gl
Conflicts:      xorg-x11-drv-nvidia-libs
Conflicts:      xorg-x11-drv-nvidia-libs-173xx
Conflicts:      xorg-x11-drv-nvidia-libs-304xx
Conflicts:      xorg-x11-drv-nvidia-libs-340xx

%ifarch %{ix86}
Conflicts:      nvidia-x11-drv-32bit
Conflicts:      nvidia-x11-drv-32bit-96xx
Conflicts:      nvidia-x11-drv-32bit-173xx
Conflicts:      nvidia-x11-drv-32bit-304xx
Conflicts:      nvidia-x11-drv-32bit-340xx
%endif

%description libs
This package provides the shared libraries for %{name}.

%package cuda
Summary:        CUDA integration for %{name}
Conflicts:      xorg-x11-drv-nvidia-cuda
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}
Requires:       nvidia-persistenced = %{?epoch:%{epoch}:}%{version}
Requires:       opencl-filesystem
Requires:       ocl-icd

%description cuda
This package provides the CUDA integration components for %{name}.

%package cuda-libs
Summary:        Libraries for %{name}-cuda
Requires(post): ldconfig

%description cuda-libs
This package provides the CUDA libraries for %{name}-cuda.

%package NvFBCOpenGL
Summary:        NVIDIA OpenGL-based Framebuffer Capture libraries
Requires(post): ldconfig
# Loads libnvidia-encode.so at runtime
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description NvFBCOpenGL
This library provides a high performance, low latency interface to capture and
optionally encode the composited framebuffer of an X screen. NvFBC and NvIFR are
private APIs that are only available to NVIDIA approved partners for use in
remote graphics scenarios.

%package NVML
Summary:        NVIDIA Management Library (NVML)
Requires(post): ldconfig
Provides:       cuda-nvml%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description NVML
A C-based API for monitoring and managing various states of the NVIDIA GPU
devices. It provides a direct access to the queries and commands exposed via
nvidia-smi. The run-time version of NVML ships with the NVIDIA display driver,
and the SDK provides the appropriate header, stub libraries and sample
applications. Each new version of NVML is backwards compatible and is intended
to be a platform for building 3rd party applications.

%package devel
Summary:        Development files for %{name}
Conflicts:      xorg-x11-drv-nvidia-devel
Conflicts:      xorg-x11-drv-nvidia-devel-173xx
Conflicts:      xorg-x11-drv-nvidia-devel-304xx
Conflicts:      xorg-x11-drv-nvidia-devel-340xx
Requires:       %{name}-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       %{name}-NVML%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       %{name}-NvFBCOpenGL%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}


%description devel
This package provides the development files of the %{name} package,
such as OpenGL headers.
 
%prep
%ifarch %{ix86}
%setup -q -n %{name}-%{version}-i386
%endif

%ifarch x86_64
%setup -q -T -b 1 -n %{name}-%{version}-x86_64
%endif

# Print and remove execstack from binaries
execstack -q nvidia-cuda-mps-control nvidia-cuda-mps-server lib*.so.*
execstack -c nvidia-cuda-mps-control nvidia-cuda-mps-server lib*.so.*

# Create symlinks for shared objects
ldconfig -vn .

# Required for building gstreamer 1.0 NVENC plugins
ln -sf libnvidia-encode.so.%{version} libnvidia-encode.so
# Required for building ffmpeg 3.1 Nvidia CUVID
ln -sf libnvcuvid.so.%{version} libnvcuvid.so
# Required for building against CUDA
ln -sf libcuda.so.%{version} libcuda.so

%build

%install
# Create empty tree
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/nvidia/
mkdir -p %{buildroot}%{_includedir}/nvidia/GL/
mkdir -p %{buildroot}%{_libdir}/nvidia/xorg/
mkdir -p %{buildroot}%{_libdir}/vdpau/
mkdir -p %{buildroot}%{_libdir}/xorg/modules/drivers/
mkdir -p %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/
mkdir -p %{buildroot}%{_sysconfdir}/nvidia/
mkdir -p %{buildroot}%{_udevrulesdir}
mkdir -p %{buildroot}%{_modprobe_d}/
mkdir -p %{buildroot}%{_dracut_conf_d}/
mkdir -p %{buildroot}%{_sysconfdir}/OpenCL/vendors/

%if 0%{?rhel}
mkdir -p %{buildroot}%{_datadir}/X11/xorg.conf.d/
%endif

%if 0%{?fedora}
mkdir -p %{buildroot}%{_datadir}/appdata/
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_presetdir}
%endif

# Headers
install -p -m 0644 *.h %{buildroot}%{_includedir}/nvidia/GL/

# OpenCL config
install -p -m 0755 nvidia.icd %{buildroot}%{_sysconfdir}/OpenCL/vendors/

# Library search path
echo "%{_libdir}/nvidia" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf

# Blacklist nouveau
install -p -m 0644 %{SOURCE20} %{buildroot}%{_modprobe_d}/

# Autoload nvidia-uvm module after nvidia module
install -p -m 0644 %{SOURCE23} %{buildroot}%{_modprobe_d}/

# Binaries
install -p -m 0755 nvidia-{debugdump,smi,cuda-mps-control,cuda-mps-server,bug-report.sh} %{buildroot}%{_bindir}

# Man pages
install -p -m 0644 nvidia-{smi,cuda-mps-control}*.gz %{buildroot}%{_mandir}/man1/

%if 0%{?fedora}
# install AppData and add modalias provides
install -p -m 0644 %{SOURCE40} %{buildroot}%{_datadir}/appdata/
fn=%{buildroot}%{_datadir}/appdata/com.nvidia.driver.metainfo.xml
%{SOURCE41} README.txt "NVIDIA GEFORCE GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE41} README.txt "NVIDIA QUADRO GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE41} README.txt "NVIDIA NVS GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE41} README.txt "NVIDIA TESLA GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE41} README.txt "NVIDIA GRID GPUS" | xargs appstream-util add-provide ${fn} modalias
# install auto-fallback to nouveau service
install -p -m 0644 %{SOURCE50} %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE51} %{buildroot}%{_presetdir}
%endif

%if 0%{?rhel}
install -p -m 0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia-modules.conf
sed -i -e 's|@LIBDIR@|%{_libdir}|g' %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia-modules.conf
install -p -m 0644 %{SOURCE11} %{buildroot}%{_datadir}/X11/xorg.conf.d/10-nvidia-driver.conf
%endif

%if 0%{?fedora} >= 25
install -p -m 0644 %{SOURCE13} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
sed -i -e 's|@LIBDIR@|%{_libdir}|g' %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
%endif

%if 0%{?fedora} >= 26
install -p -m 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia-ignoreabi.conf
%endif

# X stuff
install -p -m 0755 nvidia_drv.so %{buildroot}%{_libdir}/xorg/modules/drivers/
install -p -m 0755 libglx.so.%{version} %{buildroot}%{_libdir}/nvidia/xorg/libglx.so

# NVIDIA specific configuration files
install -p -m 0644 nvidia-application-profiles-%{version}-key-documentation \
    %{buildroot}%{_datadir}/nvidia/
install -p -m 0644 nvidia-application-profiles-%{version}-rc \
    %{buildroot}%{_datadir}/nvidia/

# UDev rules:
# https://github.com/NVIDIA/nvidia-modprobe/blob/master/modprobe-utils/nvidia-modprobe-utils.h#L33-L46
# https://github.com/negativo17/nvidia-driver/issues/27
install -p -m 644 %{SOURCE21} %{SOURCE22} %{buildroot}%{_udevrulesdir}

# Install system conflicting libraries
cp -a \
    libGL.so* \
    libGLESv1_CM.so* \
    libGLESv2.so* \
    libEGL.so* \
    %{buildroot}%{_libdir}/nvidia/

%if 0%{?rhel} == 6
cp -a libOpenCL.so* %{buildroot}%{_libdir}
%endif

# Install unique libraries
cp -a libcuda.so* libnv*.so* \
    %{buildroot}%{_libdir}/
ln -sf libcuda.so.%{version} %{buildroot}%{_libdir}/libcuda.so

# VDPAU libraries
cp -a libvdpau_nvidia.so* %{buildroot}%{_libdir}/vdpau/

# Apply the systemd preset for nvidia-fallback.service when upgrading from
# a version without nvidia-fallback.service, as %%systemd_post only does this
# on fresh installs
%if 0%{?fedora} >= 25
%triggerun -- %{name} < 2:340.104-1
systemctl --no-reload preset nvidia-fallback.service >/dev/null 2>&1 || :
%endif

%post
if [ "$1" -eq "1" ]; then
  %{_grubby} --args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  sed -i -e 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="%{_dracutopts} /g' /etc/default/grub
%endif
fi || :
if [ "$1" -eq "2" ]; then
  # Remove no longer needed options
  %{_grubby} --remove-args='%{_dracutopts_rm}' &>/dev/null
  for param in %{_dracutopts_rm}; do sed -i -e "s/$param //g" /etc/default/grub; done
fi || :
%if 0%{?fedora} >= 25
%systemd_post nvidia-fallback.service
%endif

%post libs -p /sbin/ldconfig

%post cuda-libs -p /sbin/ldconfig

%post NvFBCOpenGL -p /sbin/ldconfig

%post NVML -p /sbin/ldconfig

%preun
if [ "$1" -eq "0" ]; then
  %{_grubby} --remove-args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  sed -i -e 's/%{_dracutopts} //g' /etc/default/grub
%endif
fi ||:
%if 0%{?fedora} >= 25
%systemd_preun nvidia-fallback.service
%endif

%if 0%{?fedora} >= 25
%postun
%systemd_postun nvidia-fallback.service
%endif

%postun libs -p /sbin/ldconfig

%postun cuda-libs -p /sbin/ldconfig

%postun NvFBCOpenGL -p /sbin/ldconfig

%postun NVML -p /sbin/ldconfig

%files
%license LICENSE
%doc NVIDIA_Changelog README.txt html
%dir %{_sysconfdir}/nvidia
%{_bindir}/nvidia-bug-report.sh
%if 0%{?fedora}
%{_datadir}/appdata/com.nvidia.driver.metainfo.xml
%{_unitdir}/nvidia-fallback.service
%{_presetdir}/95-nvidia-fallback.preset
%endif
%{_datadir}/nvidia
%{_libdir}/nvidia
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
%{_modprobe_d}/nvidia.conf
%{_udevrulesdir}/60-nvidia.rules

# X.org configuration files
%if 0%{?rhel}
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/99-nvidia-modules.conf
%config(noreplace) %{_datadir}/X11/xorg.conf.d/10-nvidia-driver.conf
%endif

%if 0%{?fedora} >= 25
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
%endif

%if 0%{?fedora} >= 26 || 0%{?rhel} >= 8
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/99-nvidia-ignoreabi.conf
%endif

%files cuda
%{_sysconfdir}/OpenCL/vendors/*
%{_bindir}/nvidia-cuda-mps-control
%{_bindir}/nvidia-cuda-mps-server
%{_bindir}/nvidia-debugdump
%{_bindir}/nvidia-smi
%{_mandir}/man1/nvidia-cuda-mps-control.1.*
%{_mandir}/man1/nvidia-smi.*
%{_modprobe_d}/nvidia-uvm.conf
%{_udevrulesdir}/60-nvidia-uvm.rules

%files libs
%dir %{_libdir}/nvidia
%{_libdir}/nvidia/libEGL.so.1
%{_libdir}/nvidia/libEGL.so.%{version}
%{_libdir}/nvidia/libGL.so.1
%{_libdir}/nvidia/libGL.so.%{version}
%{_libdir}/nvidia/libGLESv1_CM.so.1
%{_libdir}/nvidia/libGLESv1_CM.so.%{version}
%{_libdir}/nvidia/libGLESv2.so.2
%{_libdir}/nvidia/libGLESv2.so.%{version}
%{_libdir}/libnvidia-cfg.so.1
%{_libdir}/libnvidia-cfg.so.%{version}
%{_libdir}/libnvidia-eglcore.so.%{version}
%{_libdir}/libnvidia-glcore.so.%{version}
%{_libdir}/libnvidia-glsi.so.%{version}
%{_libdir}/libnvidia-tls.so.%{version}
%{_libdir}/vdpau/libvdpau_nvidia.so.1
%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}
%{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf

%files cuda-libs
%{_libdir}/libcuda.so
%{_libdir}/libcuda.so.1
%{_libdir}/libcuda.so.%{version}
%{_libdir}/libnvcuvid.so.1
%{_libdir}/libnvcuvid.so.%{version}
%{_libdir}/libnvidia-compiler.so.%{version}
%{_libdir}/libnvidia-encode.so.1
%{_libdir}/libnvidia-encode.so.%{version}
%{_libdir}/libnvidia-opencl.so.1
%{_libdir}/libnvidia-opencl.so.%{version}
%if 0%{?rhel} == 6
%{_libdir}/libOpenCL.so.1
%{_libdir}/libOpenCL.so.1.0.0
%endif

%files NvFBCOpenGL
%{_libdir}/libnvidia-fbc.so.1
%{_libdir}/libnvidia-fbc.so.%{version}
%{_libdir}/libnvidia-ifr.so.1
%{_libdir}/libnvidia-ifr.so.%{version}

%files NVML
%{_libdir}/libnvidia-ml.so.1
%{_libdir}/libnvidia-ml.so.%{version}

%files devel
%{_includedir}/nvidia/
%{_libdir}/libnvcuvid.so
%{_libdir}/libnvidia-encode.so

%changelog
* Sun Aug 12 2018 Jemma Denson <jdenson@gmail.com> - 2:340.104-1
- Update to 340.107

* Sat Dec 23 2017 Jemma Denson <jdenson@gmail.com> - 2:340.104-2
- Merge in negativo17 changes from latest:
- Make the major number of Nvidia devices dynamic again:
  https://github.com/negativo17/nvidia-driver/issues/29
- Add udev rules to always create device nodes:
  https://github.com/negativo17/nvidia-driver/issues/27
- Use _target_cpu in place of _lib where appropriate.
- Do not obsolete/provide packages from other repositories, instead conflict
  with them.
- Add dracut.conf.d/99-nvidia.conf file enforcing that the nvidia modules never
  get added to the initramfs (doing so would break things on a driver update)
- Make the fallback service check for the module status instead of the device,
  which appears only after starting X.
- Add nvidia-fallback.service which automatically fallsback to nouveau if the
  nvidia driver fails to load for some reason (F25+ only)
- Thanks to Hans de Goede <jwrdegoede@fedoraproject.org> for patches.
- Update RHEL/CentOS 6 packages to use OutputClass as in RHEL/CentOS 7 (since
  RHEL 6.8 it's using X.org server 1.17+).
- Add nvidia-uvm-tools device creation to CUDA subpackage.
- Enable SLI and BaseMosaic (SLI multimonitor) by default.
- Adjust removal of obsolete kernel command line options for RHEL 6.
- Update OutputClass configuration for Intel/Optimus systems.
- Add configuration options for new OutputClass Device integration on Fedora 25
  with X server 1.19.0-3 (new 10-nvidia.conf configuration file).

* Fri Dec 22 2017 Jemma Denson <jdenson@gmail.com> - 2:340.104-1
- Update to 340.104.

* Thu Feb 23 2017 Simone Caronni <negativo17@gmail.com> - 2:340.102-1
- Udpate to 340.102.
- Install the OpenCL loader only on RHEL < 7 and in the system path.

* Thu Dec 15 2016 Simone Caronni <negativo17@gmail.com> - 2:340.101-1
- Update to 340.101.

* Sun Oct 02 2016 Simone Caronni <negativo17@gmail.com> - 2:340.98-1
- Update to 340.98.
- Remove ARM support also from tarball generation script.

* Fri Jun 24 2016 Simone Caronni <negativo17@gmail.com> - 2:340.96-3
- Ignore X.org ABI from Fedora 25+.

* Thu Jun 23 2016 Simone Caronni <negativo17@gmail.com> - 2:340.96-2
- Load nvidia-uvm.ko through a soft dependency on nvidia.ko. This avoids
  inserting the nvidia-uvm configuration file in the initrd. Since the module is
  not (and should not be) in the initrd, this prevents the (harmless) module
  loading error in Plymouth.
- Remove ARM (Carma, Kayla) support.
- Use new X.org OutputClass loader for RHEL 7 (X.org 1.16+, RHEL 7.2+).
- Rename blacklist-nouveau.conf to nvidia.conf.

* Tue Nov 17 2015 Simone Caronni <negativo17@gmail.com> - 2:340.96-1
- Update to 340.96.
- Add kernel command line also to Grub default files for grub2-mkconfig
  consumption.
- Create new macro for grubby command in post.
- Remove support for Grub 0.97 in Fedora or CentOS/RHEL 7.
- Update modprobe configuration file position in CentOS/RHEL 6.
- Ignore ABI configuration file moved to Fedora 24+.
- Move all libraries that do not replace system libraries in the default
  directories. There is no reason to keep them separate and this helps for
  building programs that link to these libraries (like nvidia-settings on NVML)
  and for writing out filters in the SPEC file.
- Rework completely symlink creation using ldconfig, remove useless symlink and
  trim devel subpackage.

* Tue Sep 08 2015 Simone Caronni <negativo17@gmail.com> - 2:340.93-1
- Update to 340.93.
- Build requires execstack in place of prelink on Fedora 23+.

* Thu May 28 2015 Simone Caronni <negativo17@gmail.com> - 2:340.76-2
- Ignore ABI configuration file moved to Fedora 23+.

* Wed Jan 28 2015 Simone Caronni <negativo17@gmail.com> - 2:340.76-1
- Update to 340.76.
- Update kernel parameters on all installed kernels, not just current. This
  solves issues when updating kernel, not rebooting, and installing the driver
  afterwards.

* Mon Jan 12 2015 Simone Caronni <negativo17@gmail.com> - 2:340.65-2
- RHEL/CentOS 7 does not have OpenCL packages (thanks stj).

* Mon Dec 08 2014 Simone Caronni <negativo17@gmail.com> - 2:340.65-1
- Update to 340.65.

* Wed Nov 05 2014 Simone Caronni <negativo17@gmail.com> - 2:340.58-1
- Update to 340.58.

* Wed Oct 01 2014 Simone Caronni <negativo17@gmail.com> - 2:340.46-1
- Update to 340.46.

* Sun Aug 17 2014 Simone Caronni <negativo17@gmail.com> - 2:340.32-1
- Update to 340.32.

* Tue Aug 05 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-5
- Split xorg.conf.d configuration in multiple files.

* Mon Jul 14 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-4
- Split out NVML library.

* Mon Jul 14 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-3
- Rely on built in generator for some requirements.
- Rpmlint fixes.
- Provides nvidia-driver-NVML for GPU Deployment kit.

* Fri Jul 11 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-2
- Move nvidia-ml/nvidia-debugdump to cuda packages.
- Use new OutputClass to load the driver on X.org server 1.16 (Fedora 21):
  https://plus.google.com/118125769023950376556/posts/YqyEgcpZmJU
- Add udev rule in nvidia-driver-cuda for nvidia-uvm module (Jan P. Springer).
- Move X.org NVIDIA Files section to be loaded latest (overwrite all Files
  section - Jan P. Springer).
- Remove nvidia-modprobe requirement.

* Tue Jul 08 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-1
- Update to 340.24.

* Fri Jun 13 2014 Simone Caronni <negativo17@gmail.com> - 2:340.17-3
- Add IgnoreABI server flag for Fedora 21.

* Wed Jun 11 2014 Simone Caronni <negativo17@gmail.com> - 2:340.17-2
- Move application profiles configuration in proper place where the driver
  expects defaults.

* Mon Jun 09 2014 Simone Caronni <negativo17@gmail.com> - 2:340.17-1
- Update to 340.17.

* Mon Jun 02 2014 Simone Caronni <negativo17@gmail.com> - 2:337.25-1
- Update to 337.25.

* Thu May 15 2014 Simone Caronni <negativo17@gmail.com> - 2:337.19-2
- Update RPM filters for autogenerated Provides/Requires.

* Tue May 06 2014 Simone Caronni <negativo17@gmail.com> - 2:337.19-1
- Update to 337.19.

* Tue Apr 08 2014 Simone Caronni <negativo17@gmail.com> - 2:337.12-1
- Update to 337.12.

* Tue Mar 04 2014 Simone Caronni <negativo17@gmail.com> - 2:334.21-1
- Update to 334.21.
- Added application profiles to the main package.

* Sat Feb 08 2014 Simone Caronni <negativo17@gmail.com> - 2:334.16-1
- Update to 334.16.
- Add EGL/GLES libraries to x86_64 package.
- Add NvFBCOpenGL libraries to armv7hl.
- Added new nvidia-modprobe dependency.

* Tue Jan 14 2014 Simone Caronni <negativo17@gmail.com> - 2:331.38-1
- Update to 331.38.

* Wed Jan 08 2014 Simone Caronni <negativo17@gmail.com> - 2:331.20-4
- CUDA subpackage requires opencl-filesystem on Fedora & RHEL 7.
- Update filters on libraries so all libGL, libEGL and libGLES libraries are
  excluded.

* Tue Dec 17 2013 Simone Caronni <negativo17@gmail.com> - 2:331.20-3
- Update libGL filters with recent packaging guidelines for Fedora and RHEL 7.

* Wed Nov 13 2013 Simone Caronni <negativo17@gmail.com> - 2:331.20-2
- Disable glamoregl X.org module.

* Thu Nov 07 2013 Simone Caronni <negativo17@gmail.com> - 2:331.20-1
- Update to 331.20.
- Create NvFBCOpenGL subpackage.

* Mon Nov 04 2013 Simone Caronni <negativo17@gmail.com> - 2:331.17-1
- Update to 331.17.
- Added new libraries:
    libnvidia-fbc (i686, armv7hl, x86_64)
    libvdpau_nvidia, libEGL (armv7hl)
    libGLESv* libraries (i686, armv7hl)
- Removed libraries (they will probably be re-added):
    libnvidia-vgxcfg libraries (i686, x86_64)

* Fri Oct 04 2013 Simone Caronni <negativo17@gmail.com> - 2:331.13-1
- Update to 331.13.
- Add new libEGL library to i686.

* Mon Sep 09 2013 Simone Caronni <negativo17@gmail.com> - 2:325.15-1
- Update to 325.15.
- Add new libnvidia-vgxcfg (i686, x86_64).

* Thu Aug 22 2013 Simone Caronni <negativo17@gmail.com> - 2:319.49-2
- Move nvidia-debugdump in main package.
- Remove libvdpau from driver tarball.

* Wed Aug 21 2013 Simone Caronni <negativo17@gmail.com> - 2:319.49-1
- Updated to 319.49.
- Add new libnvidia-ifr where appropriate.

* Tue Aug 06 2013 Simone Caronni <negativo17@gmail.com> - 2:319.32-6
- Fix duplicated binaries in non CUDA packages.
- Removed libnvidia-wfb.
- Deleted unused libnvidia-tls libraries.

* Mon Aug 05 2013 Simone Caronni <negativo17@gmail.com> - 2:319.32-5
- Fedora 17 has gone EOL.

* Thu Jul 25 2013 Simone Caronni <negativo17@gmail.com> - 2:319.32-4
- Remove dependency on nvidia-xconfig.

* Tue Jul 02 2013 Simone Caronni <negativo17@gmail.com> - 2:319.32-2
- Add armv7hl support.

* Fri Jun 28 2013 Simone Caronni <negativo17@gmail.com> - 1:319.32-1
- Update to 319.32.
- Bump Epoch.

* Fri May 24 2013 Simone Caronni <negativo17@gmail.com> - 1:319.23-1
- Update to 319.23.

* Wed May 22 2013 Simone Caronni <negativo17@gmail.com> - 1:319.17-5
- Obsolete also xorg-x11-drv-nvidia-libs.
- Add dracut options depending on distribution.
- Add grubby to requirements.

* Tue May 21 2013 Simone Caronni <negativo17@gmail.com> - 1:319.17-3
- Split CUDA into subpackages.

* Thu May 02 2013 Simone Caronni <negativo17@gmail.com> - 1:319.17-2
- Update to 319.17.
- Switch nvidia-cuda-proxy* to nvidia-cuda-mps*.
- Add dependency on nvidia-persistenced and versioned nvidia tools.

* Tue Apr 30 2013 Simone Caronni <negativo17@gmail.com> - 1:319.12-3
- Remove all filters except libGL.so*.

* Mon Apr 22 2013 Simone Caronni <negativo17@gmail.com> - 1:319.12-2
- Started off from rpmfusion-nonfree packages.
- Updated to 319.12.
- Simplify packaging.
- Add conflict to drivers 304xx.
- Add dependency on libva-vdpau-driver.
- Obsoletes xorg-x11-drv-nvidia.
- Switched to no-compat32 x86_64 archive.
- Switch to generated sources.
