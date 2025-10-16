.PHONY: installdeps srpm git_config_pre

installdeps:
	dnf -y install git autoconf automake make python3-devel

git_config_pre:
	# From git 2.35.2 we need to mark temporary directory, where the project is cloned to, as safe, otherwise
	# git commands won't work
	$(eval REPO_DIR=$(shell pwd))
	git config --global --add safe.directory ${REPO_DIR}

srpm: installdeps git_config_pre
	$(eval SUFFIX=$(shell sh -c " echo '.$$(date -u +%Y%m%d%H%M%S).git$$(git rev-parse --short HEAD)'"))
	mkdir -p tmp.repos
	./autogen.sh
	sed "s:%{?release_suffix}:${SUFFIX}:" -i engine-db-query.spec
	make dist
	rpmbuild \
		-D "_topdir tmp.repos" \
		-ts ./*.tar.gz
	cp tmp.repos/SRPMS/*.src.rpm $(outdir)
