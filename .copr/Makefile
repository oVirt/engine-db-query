.PHONY: installdeps srpm

installdeps:
	dnf -y install git autoconf automake make python3-devel

srpm: installdeps
	mkdir -p tmp.repos
	./autogen.sh
	make dist
	rpmbuild \
		-D "_topdir tmp.repos" \
		-ts ./*.tar.gz
	cp tmp.repos/SRPMS/*.src.rpm $(outdir)
