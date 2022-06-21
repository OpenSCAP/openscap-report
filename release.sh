#!/usr/bin/env bash
# This script perform first steps of release.
# Update version of package, create tag and push it to upstream.
# Usage: ./release.sh [new_version]

set -e

check_version_format(){
    echo "INFO: Check the format of the version."
    if ! echo "$1" | grep -q -E '^[0-9]{1,}.[0-9]{1,}.[0-9]{1,}$'; then
        echo "ERROR: Bad version format!"
        exit 1
    fi
}

check_uncommitted_changes(){
    echo "INFO: Check uncommitted changes."
    if git status --porcelain=v1 | grep -q '^\(.M\|M.\)'; then
        echo "ERROR: Not commited changes!"
        exit 1
    fi
}

update_version(){
    echo "INFO: Update version."
    new_version=$1
    old_version=$(python3 setup.py --version)
    sed -i "s/$old_version/$new_version/g" "setup.py"
}

commit_new_version(){
    echo "INFO: Commit new version."
    version=$1
    git add setup.py
    git commit -m "${version}"
}

create_tag(){
    echo "INFO: Create tag."
    version=$1
    git tag "v${version}" HEAD
}

push_changes(){
    echo "INFO: Push changes."
    git push upstream master
    git push --tags
}


if [ "$1" = "" ]; then
    echo "ERROR: Missing version parameter!"
    exit 1
fi
    
new_version=$1

check_version_format "$new_version"
check_uncommitted_changes
update_version "$new_version"
commit_new_version "$new_version"
create_tag "$new_version"
push_changes
echo "INFO: Done"
exit 0
