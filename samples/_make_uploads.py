from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent

rows = [
    {"Job": "Auntie florist website", "You said": 12, "It took": 19, "Paid": 24000},
    {"Job": "Neighbour spice shop", "You said": 30, "It took": 34, "Paid": 60000},
    {"Job": "Tuition fees sheet", "You said": 28, "It took": 41, "Paid": 56000},
    {"Job": "Cafe logo", "You said": 12, "It took": 18, "Paid": 24000},
]

pd.DataFrame(rows).to_excel(HERE / "upload-test.xlsx", index=False)

(HERE / "upload-test.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")

(HERE / "upload-test.tsv").write_text(
    "Job\tYou said\tIt took\tPaid\n"
    "Cafe logo\t12\t18\t24000\n"
    "Plumber page\t8\t11\t16000\n"
    "Wedding invite\t5\t8\t10000\n",
    encoding="utf-8",
)

docx_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
<w:p><w:r><w:t>Finished jobs</w:t></w:r></w:p>
<w:p><w:r><w:t>Auntie florist website. I said 12 hours, it took 19. They paid 24000.</w:t></w:r></w:p>
<w:p><w:r><w:t>Neighbour spice shop. I said 30 hours, it took 34. They paid 60000.</w:t></w:r></w:p>
<w:p><w:r><w:t>Tuition fees sheet. I said 28 hours, it took 41. They paid 56000.</w:t></w:r></w:p>
</w:body>
</w:document>
"""
content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""
rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""
with zipfile.ZipFile(HERE / "upload-test.docx", "w") as z:
    z.writestr("[Content_Types].xml", content_types)
    z.writestr("_rels/.rels", rels)
    z.writestr("word/document.xml", docx_xml)

print("wrote xlsx json tsv docx")
