#!/bin/sh -x
set -e

VERSION=340.98
#DL_SITE=ftp://download.nvidia.com/XFree86
DL_SITE=http://us.download.nvidia.com/XFree86

create_tarball() {
    KMOD=nvidia-kmod-${VERSION}-${ARCH}
    DRIVER=nvidia-driver-${VERSION}-${ARCH}

    sh nvidia-${VERSION}-${ARCH}.run --extract-only --target temp
    mkdir ${KMOD} ${KMOD_MULTI} ${DRIVER}

    cd temp

    # Compiled from source
    rm -f nvidia-settings* nvidia-xconfig* nvidia-persistenced* \
            nvidia-modprobe* libvdpau.so* libvdpau_trace.so*

    # Useless with packages
    rm -f nvidia-installer* .manifest make* mk* tls_test*

    # useless on modern distributions
    rm -f libnvidia-wfb*

    # Use correct tls implementation
    mv -f tls/libnvidia-tls.so* .
    rm -fr tls

    mv kernel ../${KMOD}/
    mv * ../${DRIVER}/

    cd ..
    rm -fr temp

    tar --remove-files -cJf ${KMOD}.tar.xz ${KMOD}
    tar --remove-files -cJf ${DRIVER}.tar.xz ${DRIVER}

    rm -f nvidia-${VERSION}-${ARCH}.run
}

ARCH=i386
wget -c ${DL_SITE}/Linux-x86/${VERSION}/NVIDIA-Linux-x86-${VERSION}.run
mv NVIDIA-Linux-x86-${VERSION}.run nvidia-${VERSION}-${ARCH}.run
create_tarball

ARCH=x86_64
wget -c ${DL_SITE}/Linux-${ARCH}/${VERSION}/NVIDIA-Linux-${ARCH}-${VERSION}-no-compat32.run
mv NVIDIA-Linux-${ARCH}-${VERSION}-no-compat32.run nvidia-${VERSION}-${ARCH}.run
create_tarball
