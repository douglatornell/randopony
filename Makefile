# Makefile to automate deployment update & development tasks for RandoPony

.PHONY:	help docs clean-docs rsync-all rsync-proj rsync-docs getwfdb \
	    coverage-report

WF_PONY = webfaction:webapps/randopony

help:
	@echo "Use \`make <target>' where <target> is one of"
	@echo "  docs             to make docs as standalone HTML files"
	@echo "  clean-docs       to delete docs HTML files"
	@echo "  rsync-docs       to make docs HTML files & rsync them to webfaction"
	@echo "  rsync-proj       to rsync the RandoPony project to webfaction"
	@echo "  rsync-all        to rsync the RandoPony project & docs to webfaction"
	@echo "  getwfdb          to rsync the RandoPony database FROM webfaction"
	@echo "  coverage-report  to rsync the RandoPony database FROM webfaction"

docs:
	(cd docs; make html; cd ..)

clean-docs:
	rm -rf docs/_build

rsync-docs: docs
	rsync -ahvz --dry-run docs/_build/html $(WF_PONY)/randopony/docs/_build/

rsync-proj:
	rsync -ahvz --dry-run \
    --exclude=.hg* --exclude=*.pyc --exclude=*.db --exclude=.DS_Store \
    --exclude=settings.py --exclude=.secret_key --exclude=docs \
    --exclude=*.aside --exclude=*.backup \
    ../randopony $(WF_PONY)/

rsync-all: rsync-docs rsync-proj

getwfdb:
	rsync -hvz $(WF_PONY)/randopony/randopony-production.db ./

coverage-report:
	coverage run --source . manage.py test 
	coverage html
