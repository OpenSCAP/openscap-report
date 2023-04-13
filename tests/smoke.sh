#!/usr/bin/env bash
# Test of the basic function
# Usage: ./smoke.sh path_to_arf
#   path_to_arf     (Default: ./test_data/arf-report.xml) Path where is tested ARF file

set -e -o pipefail

path_to_arf=$1
if [ "$path_to_arf" = "" ]; then
    path_to_arf="./test_data/arf-report.xml"
fi

# Generate report
oscap-report < "${path_to_arf}" > report.html

# Search for some rule ID in the report
grep -q "xccdf_org\.ssgproject\.content_rule_enable_fips_mode" report.html

rm report.html

echo "Report generation success"
