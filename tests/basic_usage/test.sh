#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
. /usr/share/beakerlib/beakerlib.sh || exit 1


rlJournalStart
    rlPhaseStartSetup
        rlRun "tmp=\$(mktemp -d)" 0 "Creating tmp directory"            
        rlRun "pushd $tmp"
        rlRun "set -o pipefail"              
        rlRun "oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_ospp --results-arf arf.xml /usr/share/xml/scap/ssg/content/ssg-fedora-ds.xml" 2
    rlPhaseEnd
    
    rlPhaseStartTest
        rlRun "oscap-report < arf.xml | tee output" 0 "Check basic generation of report"
        rlAssertGrep "xccdf_org\.ssgproject\.content_rule_enable_fips_mode" "output"
    rlPhaseEnd

    rlPhaseStartCleanup
        rlRun "popd"
        rlRun "rm -r $tmp" 0 "Remove tmp directory"
    rlPhaseEnd
rlJournalEnd
