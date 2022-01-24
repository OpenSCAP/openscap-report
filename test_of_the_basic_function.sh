#!/usr/bin/env bash
# Test of the basic function

set -e -o pipefail

# Generate report
oscap-report < ./tests/test_data/arf-report.xml > report.html

# Search for some rule ID in the report
grep -q "xccdf_org\.ssgproject\.content_rule_enable_fips_mode" report.html

echo "Report generation success"
