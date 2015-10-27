#!/bin/bash

# going to git root
cd `git rev-parse --show-toplevel`

# updating changelog
$(which git-dch || echo gbp dch) --debian-tag='%(version)s' --debian-branch=${1:-master}
dch -e

# commiting
git add -p
debcommit -r

# going back
cd -
