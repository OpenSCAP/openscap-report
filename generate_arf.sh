#!/usr/bin/env bash
# This script generates ARF results.
# Supported OS:
#  - Fedora
#  - RHEL8/9
#  - Centos8/9
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
#   ARF_FILE    Writes results to a given ARF_FILE.
#   SKIP_BUILD  [yes] Skip build of latest content(Have affect with mode latest).


set -e -o pipefail


build_content() {
    product=$1

    echo "Build - Start"

    git clone https://github.com/ComplianceAsCode/content.git
    cd content/
    git checkout master

    cd build/
    cmake ../
    make -j4 "${product}"

    cd ../../
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

get_product() {
    cpe_name=$(grep "CPE_NAME=" < /etc/os-release | sed 's/CPE_NAME=//g' | sed 's/["]//g')
    if [[ "${cpe_name}" =~ fedora ]]; then
        echo "fedora"
    elif [[ "${cpe_name}" =~ redhat.*8 ]]; then
        echo "rhel8"
    elif [[ "${cpe_name}" =~ redhat.*9 ]]; then
        echo "rhel9"
    elif [[ "${cpe_name}" =~ centos.*8 ]]; then
        echo "centos8"
    elif [[ "${cpe_name}" =~ centos.*9 ]]; then
        echo "cs9"
    else
        echo $cpe_name
        echo "ERROR: Not supported OS!"
        exit 1
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
    echo "ERROR: Missing ARF_FILE parameter!"
    exit 1
fi
file=$3

product=$(get_product)

fetch="--fetch-remote-resources"
if [ "$2" = "no" ]; then
    fetch=""
fi


if [ "$1" = "latest" ]; then
    if [ "$4" != "yes" ]; then
        build_content "${product}"
    fi
    run_oscap_scan "./content/build/ssg-${product}-ds.xml" "${fetch}" "${file}"
fi

if [ "$1" = "ssg" ]; then
    run_oscap_scan "/usr/share/xml/scap/ssg/content/ssg-${product}-ds.xml" "${fetch}" "${file}"
fi
