# from annotationlib import type_repr
import sys
import os
import json
import tempfile
import shutil
from . import signature
from . import field

import typst
from pathlib import Path

def usage() -> None:
    print("Usage:", sys.argv[0], " <in.typ>")


def split_fields_signatures(metadata_json) -> tuple[list[dict], list[dict]]:

    fields: list = []
    signatures: list = []

    for entry in metadata_json:
        value = entry.get("value", {})
        if value.get("fieldType") == "text":
            fields.append(value)
        elif value.get("fieldType") == "textarea":
            fields.append(value)
        elif value.get("fieldType") == "checkbox":
            fields.append(value)
        elif value.get("fieldType") == "radio":
            fields.append(value)
        elif value.get("fieldType") == "signature":
            signatures.append(value)

    return fields, signatures



def main() -> None:
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    input_typ = sys.argv[1]
    typ_path = Path(input_typ)

    metadata_json = json.loads(typst.eval(input_typ, "query(metadata)"))

    # Extract just the name without the extension
    output_pdf = typ_path.stem+".pdf"

    with tempfile.NamedTemporaryFile(delete=True) as pdf1:
        with tempfile.NamedTemporaryFile(delete=True) as pdf2:

            dir = os.path.dirname(input_typ)
            if dir != "":
                os.chdir(dir)

            print("Compiling, writing to "+pdf1.name)
            typst.compile(input=os.path.basename(input_typ), output=pdf1.name)
            shutil.copy(pdf1.name, output_pdf)


            print("Adding Signatures, writing to "+pdf2.name)
            fields, signatures = split_fields_signatures(metadata_json)
            signature.add_signatures(pdf1.name, pdf2.name, signatures)
            shutil.copy(pdf2.name, output_pdf)
            field.add_fields(pdf2.name, pdf1.name, fields)
            shutil.copy(pdf1.name, output_pdf)

