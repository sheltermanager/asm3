#!/bin/bash
# Removes all git tags and re-adds them with the dates of the commits they are tagging
# This is used primarily to retrospectively mark github releases
git tag -l | while read -r tag ; do COMMIT_HASH=$(git rev-list -1 $tag) && GIT_COMMITTER_DATE="$(git show $COMMIT_HASH --format=%aD | head -1)" git tag -a -f $tag -m"$tag" $COMMIT_HASH ; done && git push --tags --force
