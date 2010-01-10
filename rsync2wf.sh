#!/bin/sh

# rsync the randopony Django app to WebFaction
rsync -avz \
    --exclude=.hg* --exclude=*.pyc --exclude=*.db --exclude=rsync2wf.sh \
    --exclude=settings.py --exclude=.secret_key --exclude=.DS_Store \
    $PWD webfaction:webapps/randopony/
