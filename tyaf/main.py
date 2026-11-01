# from annotationlib import type_repr
import argparse
import sys
import os
import json
import tempfile
import shutil
from . import signature
from . import field

import typst
from pathlib import Path


def parse_key_value(s: str) -> tuple[str, str]:
    if "=" not in s:
        raise argparse.ArgumentTypeError(f"expected 'key=value', got '{s}'")
    key, value = s.split("=", 1)
    return key, value


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
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description="Compile a typst document into a fillable/signable PDF.",
    )
    parser.add_argument("input_typ", help="path to the .typ input file")
    parser.add_argument(
        "output_pdf",
        nargs="?",
        help="full path to the output PDF file; if omitted, it is "
        "derived from the input filename",
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="sys_inputs",
        action="append",
        type=parse_key_value,
        default=[],
        metavar="KEY=VALUE",
        help="system input for typst, e.g. --input 'key=value' (repeatable)",
    )
    # Intermixed parsing so positionals and flags can appear in any order.
    args = parser.parse_intermixed_args()

    input_typ = args.input_typ
    sys_inputs: dict[str, str] = dict(args.sys_inputs)
    typ_path = Path(input_typ)

    metadata_json = json.loads(typst.eval(input_typ, "query(metadata)"))

    if args.output_pdf is not None:
        # Resolve to an absolute path so it survives the os.chdir below.
        output_pdf = str(Path(args.output_pdf).resolve())
        Path(output_pdf).parent.mkdir(parents=True, exist_ok=True)
    else:
        # Extract just the name without the extension
        output_pdf = typ_path.stem+".pdf"

    with tempfile.NamedTemporaryFile(delete=True) as pdf1:
        with tempfile.NamedTemporaryFile(delete=True) as pdf2:

            dir = os.path.dirname(input_typ)
            if dir != "":
                os.chdir(dir)

            pdf_out = pdf1
            pdf_in = pdf2

            # print("Compiling, writing to "+pdf1.name)
            typst.compile(
                input=os.path.basename(input_typ),
                output=pdf_out.name,
                sys_inputs=sys_inputs,
            )
            shutil.copy(pdf_out.name, output_pdf)

            # print("Adding Signatures, writing to "+pdf2.name)
            fields, signatures = split_fields_signatures(metadata_json)


            if len(signatures) > 0:
                pdf_in, pdf_out = pdf_out, pdf_in
                signature.add_signatures(pdf_in.name, pdf_out.name, signatures)

                # copy to output_pdf just in case the next step fails
                shutil.copy(pdf_out.name, output_pdf)


            if len(fields) > 0:
                pdf_in, pdf_out = pdf_out, pdf_in
                field.add_fields(pdf_in.name, pdf_out.name, fields)

                # copy to output_pdf just in case the next step fails
                shutil.copy(pdf_out.name, output_pdf)
