import pytest

from oscap_report.scap_results_parser.scap_results_parser import \
    SCAPResultsParser

from ..constants import PATH_TO_ARF, PATH_TO_EMPTY_XML_FILE, PATH_TO_XCCDF


@pytest.mark.parametrize("file_path, result", [
    (PATH_TO_ARF, True),
    (PATH_TO_XCCDF, False),
    (PATH_TO_EMPTY_XML_FILE, False),
])
def test_validation(file_path, result):
    xml_data = None
    with open(file_path, "r", encoding="utf-8") as xml_report:
        xml_data = xml_report.read().encode()
    parser = SCAPResultsParser(xml_data)
    assert parser.validate(parser.arf_schemas_path) == result
