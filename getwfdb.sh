#!/bin/sh

# rsync the randopony production database from Webfaction
rsync -hvz webfaction:webapps/randopony/randopony/randopony-production.db ./