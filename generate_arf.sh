#!/usr/bin/env bash
# This script generate ARF results.
# Requirements:
#  - cmake
#  - make
#  - openscap-utils
#  - openscap-scanner
#  - python3-pyyaml
#  - python3-jinja2
#  - python3-setuptools
#  - git
#  - scap-security-guide
# Usage: ./generate_arf MODE FETCH PRODUCT ARF_FILE SKIP_BUILD
#   MODE        [latest, ssg] use scap-security-guide or latest content from github
#   FETCH       [yes, no] scanner fetch remote resources 
#   PRODUCT     build or use security content for one specific product
#   ARF_FILE    Writes results to a given ARF_FILE.
#   SKIP_BUILD  [yes] Skip build of latest content(Have affect with mode latest).


set -e -o pipefail


build_content() {
    product=$1

    echo "Build - Start"
    
    git clone https://github.com/ComplianceAsCode/content.git
    cd content/
    git checkout master
    
    ./build_product "${product}"
    cd ..
    echo "Build - Done"
}

run_oscap_scan() {
    ds=$1
    fetch=$2
    file=$3
    echo "Scans - Start"
    oscap xccdf eval ${fetch} --profile "(all)" --results-arf ${file} ${ds} || EXIT_CODE=$?
    echo $EXIT_CODE
    if [ ! -f "$file" ]; then
        echo "$file does not exist."
        exit 2
    fi
}


if [ "$1" = "" ]; then
    echo "ERROR: Missing MODE parameter!"
    exit 1
fi


if [ "$2" = "" ]; then
    echo "ERROR: Missing FETCH parameter!"
    exit 1
fi


if [ "$3" = "" ]; then
    echo "ERROR: Missing PRODUCT parameter!"
    exit 1
fi

if [ "$4" = "" ]; then
    echo "ERROR: Missing PRODUCT parameter!"
    exit 1
fi

file=$4
product=$3

fetch="--fetch-remote-resources"
if [ "$2" = "no" ]; then
    fetch=""
fi


if [ "$1" = "latest" ]; then
    if [ "$5" != "yes" ]; then
        build_content "${product}"
    fi
    run_oscap_scan "./content/build/ssg-${product}-ds.xml" "${fetch}" "${file}"
fi

if [ "$1" = "ssg" ]; then
    run_oscap_scan "/usr/share/xml/scap/ssg/content/ssg-${product}-ds.xml" "${fetch}" "${file}"
fi
