import io

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject
from reportlab.pdfgen import canvas
from reportlab.lib.colors import transparent, black, white

from .util import pt_to_float

def add_fields(input_file: str, output_file: str, fields: list[dict]) -> None:
    reader = PdfReader(input_file)
    writer = PdfWriter()

    for value in fields:
        name = value["fieldName"]
        print("Adding "+name+" as "+value["fieldType"])
        page_num = int(value["pos"]["page"]) - 1
        x = pt_to_float(value["pos"]["x"])
        # Convert top‑left Y to bottom‑left PDF coordinate
        typst_y = pt_to_float(value["pos"]["y"])
        page_info = value.get("page", {})
        page_height = pt_to_float(page_info.get("height", "0pt"))
        height = pt_to_float(value["dimensions"]["height"])
        y = page_height - typst_y - height  # flipped Y coordinate
        width = pt_to_float(value["dimensions"]["width"])
        box = (x, y, x + width, y + height)

        # Get the target page to look up its structural height
        # page = writer.pages[page_num]
        # page_height = float(page.mediabox.height)

        target_page = reader.pages[page_num]
        page_width = float(target_page.mediabox.width)
        page_height = float(target_page.mediabox.height)

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))

        # Access the form property directly
        form = can.acroForm #

        form.textfield(
            name=name,
            # tooltip="Enter text here",
            x=x,
            y=y,
            width=width,
            height=height,
            fontSize=11,
            borderWidth=1,
            borderColor=black,
            fillColor=white
        )


        can.showPage()
        can.save()
        packet.seek(0)

        overlay_reader = PdfReader(packet)
        overlay_page = overlay_reader.pages[0]

        target_page.merge_page(overlay_page)

    # The PdfWriter will preserve any AcroForm fields added via ReportLab.
    # No explicit NeedAppearances handling is necessary for basic visibility.

    writer.append(reader)
    # Write the modified structure back out
    with open(output_file, "wb") as f:
        writer.write(f)

    # print("Wrote to "+output_file)
