#!/bin/sh

# rsync the randopony Django app to WebFaction
rsync -ahvz \
    --exclude=.hg* --exclude=*.pyc --exclude=*.db --exclude=rsync2wf.sh \
    --exclude=settings.py --exclude=.secret_key --exclude=.DS_Store \
    --exclude=*.aside --exclude=*.backup --exclude=getwfdb.sh \
    $PWD webfaction:webapps/randopony/
