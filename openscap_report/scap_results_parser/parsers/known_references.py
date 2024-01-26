import logging

from ..namespaces import NAMESPACES

# pylint: disable=line-too-long
KNOWN_REFERENCES = {
    "http://www.ssi.gouv.fr/administration/bonnes-pratiques/": "ANSSI",
    "https://public.cyber.mil/stigs/cci/": "CCI",
    "https://www.ccn-cert.cni.es/pdf/guias/series-ccn-stic/guias-de-acceso-publico-ccn-stic/6768-ccn-stic-610a22-perfilado-de-seguridad-red-hat-enterprise-linux-9-0/file.html": "CCN for RHEL 9",  # noqa: E501
    "https://www.cisecurity.org/controls/": "CIS",
    "https://www.cisecurity.org/benchmark/red_hat_linux/": "CIS for RHEL",
    "https://www.fbi.gov/file-repository/cjis-security-policy-v5_5_20160601-2-1.pdf": "CJIS",  # noqa: E501
    "http://www.cnss.gov/Assets/pdf/CNSSI-1253.pdf": "CNSS",
    "https://www.isaca.org/resources/cobit": "COBIT",
    "http://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-171.pdf": "CUI",  # noqa: E501
    "https://www.gpo.gov/fdsys/pkg/CFR-2007-title45-vol1/pdf/CFR-2007-title45-vol1-chapA-subchapC.pdf": "HIPAA",  # noqa: E501
    "https://www.isa.org/products/ansi-isa-62443-3-3-99-03-03-2013-security-for-indu": "ISA-62443-2013",  # noqa: E501
    "https://www.isa.org/products/isa-62443-2-1-2009-security-for-industrial-automat": "ISA-62443-2009",  # noqa: E501
    "https://www.cyber.gov.au/acsc/view-all-content/ism": "ISM",
    "https://www.iso.org/standard/54534.html": "ISO 27001-2013",
    "https://www.nerc.com/pa/Stand/Standard%20Purpose%20Statement%20DL/US_Standard_One-Stop-Shop.xlsx": "NERC-CIP",  # noqa: E501
    "http://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r4.pdf": "NIST 800-53",  # noqa: E501
    "https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.04162018.pdf": "NIST CSF",  # noqa: E501
    "https://www.niap-ccevs.org/Profile/PP.cfm": "OSPP",
    "https://www.pcisecuritystandards.org/documents/PCI_DSS_v3-2-1.pdf": "PCI-DSS v3",  # noqa: E501
    "https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0.pdf": "PCI-DSS v4",  # noqa: E501
    "https://public.cyber.mil/stigs/downloads/?_dl_facet_stigs=application-servers": "SRG-APP",  # noqa: E501
    "https://public.cyber.mil/stigs/downloads/?_dl_facet_stigs=operating-systems%2Cgeneral-purpose-os": "SRG-OS",  # noqa: E501
    "https://public.cyber.mil/stigs/downloads/?_dl_facet_stigs=operating-systems%2Cunix-linux": "STIG ID",  # noqa: E501
    "https://public.cyber.mil/stigs/srg-stig-tools/": "STIG ref",
}
# pylint: enable=line-too-long


def update_references(root):
    references_elements = root.findall(".//xccdf:Benchmark/xccdf:reference", NAMESPACES)
    if len(references_elements) == 0:
        logging.warning(
            "Mapping of references was not found. So search by references is disabled."
        )
    for ref_el in references_elements:
        href = ref_el.get("href")
        if href is not None:
            KNOWN_REFERENCES[href] = ref_el.text
