# pyhanko sign addfields --field 1/7.2,82.22,208.8,154.22/PM_SIG sig.pdf out.pdf

from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields
# from pyhanko.sign import signers
from pyhanko.sign.fields import SigFieldSpec

from .util import pt_to_float

def add_signatures(input_file: str, output_file: str, signatures: list[dict]) -> None:
    with open(input_file, "rb") as input_file_handle:
        iwriter = IncrementalPdfFileWriter(input_file_handle)

        # Dynamically add signature fields based on metadata
        for value in signatures:
            name = value["fieldName"]
            print("Adding signature field for "+name)
            page_idx = int(value["pos"]["page"]) - 1  # zero‑based index for pyhanko
            x = pt_to_float(value["pos"]["x"])
            # Convert top‑left Y to bottom‑left PDF coordinate
            typst_y = pt_to_float(value["pos"]["y"])
            page_info = value.get("page", {})
            page_height = pt_to_float(page_info.get("height", "0pt"))
            height = pt_to_float(value["dimensions"]["height"])
            y = page_height - typst_y - height  # flipped Y coordinate
            width = pt_to_float(value["dimensions"]["width"])
            box = (x, y, x + width, y + height)

            fields.append_signature_field(
                iwriter,
                sig_field_spec=SigFieldSpec(
                    sig_field_name=name,
                    on_page=page_idx,
                    # error about floats in tuple(int) intentional
                    box=box,
                ),
            )

        with open(output_file, "wb") as outf:
            iwriter.write(outf)
        print("Wrote to "+output_file)

    # print(f"Successfully signed '{input_file}' and saved to '{output_file}'.")
