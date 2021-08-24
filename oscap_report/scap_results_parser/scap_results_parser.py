import logging
from pathlib import Path

from lxml import etree

SCHEMAS_DIR = Path(__file__).parent / "schemas"


class SCAPResultsParser():
    def __init__(self, data):
        self.root = etree.XML(data)
        self.arf_schemas_path = 'arf/1.1/asset-reporting-format_1.1.0.xsd'
        if not self.validate(self.arf_schemas_path):
            logging.warning("This file is not valid ARF report!")
        else:
            logging.info("The file is valid ARF report")

    def validate(self, xsd_path):
        xsd_path = str(SCHEMAS_DIR / xsd_path)
        xmlschema_doc = etree.parse(xsd_path)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        return xmlschema.validate(self.root)
