.PHONY: installdeps srpm

installdeps:
	dnf -y install git autoconf automake make python3-devel

srpm: installdeps
	$(eval SUFFIX=$(shell sh -c " echo '.$$(date -u +%Y%m%d%H%M%S).git$$(git rev-parse --short HEAD)'"))
	mkdir -p tmp.repos
	./autogen.sh
	sed "s:%{?release_suffix}:${SUFFIX}:" -i engine-db-query.spec
	make dist
	rpmbuild \
		-D "_topdir tmp.repos" \
		-ts ./*.tar.gz
	cp tmp.repos/SRPMS/*.src.rpm $(outdir)
