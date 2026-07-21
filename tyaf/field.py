import io

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    NameObject,
    BooleanObject,
    DictionaryObject,
    ArrayObject,
    TextStringObject,
    FloatObject,
    NumberObject,
    DecodedStreamObject
)

from .util import pt_to_float

def add_field_to_acroform(writer: PdfWriter, field_ref) -> None:
    root = writer._root_object
    if NameObject("/AcroForm") not in root:
        root[NameObject("/AcroForm")] = DictionaryObject({
            # (Optional) A flag specifying whether to construct appearance streams
            # and appearance dictionaries for all widget annotations in the docu-
            # ment (see “Variable Text” on page 677). Default value: false.
            NameObject("/NeedAppearances"): BooleanObject(True)
        })
    acroform = root[NameObject("/AcroForm")]

    if NameObject("/Fields") not in acroform:
        acroform[NameObject("/Fields")] = ArrayObject()

    acroform[NameObject("/Fields")].append(field_ref)


def add_field_to_annots(writer: PdfWriter, page_index, field_ref) -> None:
    # Is this error ok?
    # writer.add_annotation(page_number=page_index, annotation=new_field_ref)

    page_dict = writer.pages[page_index]

    if NameObject("/Annots") not in page_dict:
        page_dict.update({
            NameObject("/Annots"): ArrayObject()
        })

    page_dict["/Annots"].append(field_ref)




def add_field_to_page(writer: PdfWriter, page_index: int, field) -> None:
    field_ref = writer._add_object(field)
    add_field_to_annots(writer, page_index, field_ref)
    add_field_to_acroform(writer, field_ref)


def add_fields(input_file: str, output_file: str, fields: list[dict]) -> None:
    reader = PdfReader(input_file)
    writer = PdfWriter()
    writer.append(reader)

    radio_groups: dict = {}

    font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/ZapfDingbats"),
        NameObject("/Encoding"): NameObject("/WinAnsiEncoding"),
    })
    font_ref = writer._add_object(font)

    checked = DecodedStreamObject()
    checked.update({
        NameObject("/Type"): NameObject("/XObject"),
        NameObject("/Subtype"): NameObject("/Form"),
        NameObject("/BBox"): ArrayObject([
                    FloatObject(0),
                    FloatObject(0),
                    FloatObject(40),
                    FloatObject(40)
                    ]),
        NameObject("/Resources"): DictionaryObject({
            NameObject("/Font"): DictionaryObject({
                NameObject("/ZD"): font_ref
            })
        }),
    })
    checked.set_data(b'BT /ZD 26 Tf 9 11 Td (\064) Tj ET')
    # checked.set_data(b'BT /F1 12 Tf 2 2 Td (X) Tj ET') # python interprets hex values in <>
    # checked.set_data(b'BT /F1 12 Tf 0 0 Td <FEFF2713> Tj ET') # python interprets hex values in <>
    # checked.set_data(b'BT /F1 12 Tf 0 0 Td <FEFF2714> Tj ET') # python interprets hex values in <>
    # U+2713 CHECK MARK, UTF‑16BE literal
    # BT /F1 12 Tf 0 0 Td <FEFF2713> Tj ET
    # checked_ref = writer._add_object(checked)


    radio_selected = DecodedStreamObject()
    radio_selected.update({
        NameObject("/Type"): NameObject("/XObject"),
        NameObject("/Subtype"): NameObject("/Form"),
        NameObject("/BBox"): ArrayObject([
                    FloatObject(0),
                    FloatObject(0),
                    FloatObject(36),
                    FloatObject(36)
                    ]),
        NameObject("/Resources"): DictionaryObject({
            NameObject("/Font"): DictionaryObject({
                NameObject("/ZD"): font_ref
            })
        }),
    })
    radio_selected.set_data(b'BT /ZD 18 Tf 11 12 Td (\154) Tj ET')

    # unchecked = DecodedStreamObject()
    # unchecked.update({
        # NameObject("/Type"): NameObject("/XObject"),
        # NameObject("/Subtype"): NameObject("/Form"),
        # NameObject("/BBox"): ArrayObject([
                    # FloatObject(0),
                    # FloatObject(0),
                    # FloatObject(12),
                    # FloatObject(12)
                    # ]),
        # NameObject("/Resources"): DictionaryObject({
            # NameObject("/Font"): DictionaryObject({
                # NameObject("/F1"): font_ref
            # })
        # }),
    # })
    # unchecked.set_data(b'BT /F1 12 Tf 0 0 Td ( ) Tj ET')
    # unchecked.set_data(b'BT /F1 12 Tf 0 0 Td <FEFF25CB> Tj ET') # ○ - White Circle
    # U+25CB WHITE CIRCLE, UTF‑16BE literal
    # unchecked_ref = writer._add_object(unchecked)

    blank = DecodedStreamObject()
    blank.update({
        NameObject("/Type"): NameObject("/XObject"),
        NameObject("/Subtype"): NameObject("/Form"),
        NameObject("/BBox"): ArrayObject([
                    FloatObject(0),
                    FloatObject(0),
                    FloatObject(12),
                    FloatObject(12)
                    ]),
        NameObject("/Resources"): DictionaryObject({
            NameObject("/Font"): DictionaryObject({
                NameObject("/F1"): font_ref
            })
        }),
    })
    blank.set_data(b'BT /F1 12 Tf 0 0 Td ( ) Tj ET')

    for value in fields:
        name = value["fieldName"]
        field_type = value["fieldType"]
        page_index = int(value["pos"]["page"]) - 1
        x = pt_to_float(value["pos"]["x"])
        # Convert top‑left Y to bottom‑left PDF coordinate
        typst_y = pt_to_float(value["pos"]["y"])
        page_info = value.get("page", {})
        page_height = pt_to_float(page_info.get("height", "0pt"))
        height = pt_to_float(value["dimensions"]["height"])
        y = page_height - typst_y - height  # flipped Y coordinate
        width = pt_to_float(value["dimensions"]["width"])
        box = (x, y, x + width, y + height)

        new_field = None

        print(name+" is a "+field_type)

        if field_type == "text":
            print("Adding "+name+" as "+field_type)

            new_field = DictionaryObject({
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Widget"),
                NameObject("/FT"): NameObject("/Tx"),     # Field Type: Text
                NameObject("/T"): TextStringObject(name), # Field Name (key in get_fields)
                NameObject("/V"): TextStringObject(""), # Default Value
                # /Rect [llx lly urx ury]
                NameObject("/Rect"): ArrayObject([
                    FloatObject(x),
                    FloatObject(y),
                    FloatObject(x+width),
                    FloatObject(y+height)]),
                NameObject("/F"): NumberObject(4), # Print flag (ensures it shows when printed)
            })

            add_field_to_page(writer, page_index, new_field)

        if field_type == "textarea":
            print("Adding "+name+" as "+field_type)

            new_field = DictionaryObject({
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Widget"),
                NameObject("/FT"): NameObject("/Tx"),     # Field Type: Text
                NameObject("/T"): TextStringObject(name), # Field Name (key in get_fields)
                NameObject("/V"): TextStringObject(""), # Default Value
                NameObject("/DA"): TextStringObject("/Helv 8 Tf 0 g"),
                # /Rect [llx lly urx ury]
                NameObject("/Rect"): ArrayObject([
                    FloatObject(x),
                    FloatObject(y),
                    FloatObject(x+width),
                    FloatObject(y+height)]),
                NameObject("/F"): NumberObject(4), # Print flag (ensures it shows when printed)
                NameObject("/Ff"): NumberObject(4096) # Field Flag (4096 = Multiline)
            })

            add_field_to_page(writer, page_index, new_field)

        if field_type == "checkbox":
            print("Adding "+name+" as "+field_type)

            # NOTE: MUST be /Yes and /Off
            new_field = DictionaryObject({
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Widget"),
                NameObject("/FT"): NameObject("/Btn"),     # Field Type: Text
                NameObject("/T"): TextStringObject(name), # Field Name (key in get_fields)
                NameObject("/V"):  NameObject("/Off"),      # Current Value (/Yes /No)
                NameObject("/AS"): NameObject("/Off"),      # Appearance State (/Yes /No)
                NameObject("/AP"): DictionaryObject({
                    NameObject("/N"): DictionaryObject({
                        NameObject("/Off"): writer._add_object(blank),
                        NameObject("/Yes"): writer._add_object(checked),
                    }),
                    NameObject("/D"): DictionaryObject({
                        NameObject("/Off"): writer._add_object(blank),
                        NameObject("/Yes"): writer._add_object(checked),
                    }),
                }),
                # /Rect [llx lly urx ury]
                NameObject("/Rect"): ArrayObject([
                    FloatObject(x),
                    FloatObject(y),
                    FloatObject(x+width),
                    FloatObject(y+height)]),
                NameObject("/F"): NumberObject(4), # Print flag (ensures it shows when printed)
            })

            add_field_to_page(writer, page_index, new_field)

        if field_type == "radio":
            # Here we need to create and add a radio group button to the AcroForm and the children to the Annots for the page

            group_name = value["groupName"]
            print("Adding "+name+" as "+field_type+" in "+group_name)

            if group_name not in radio_groups:

                radio_group = DictionaryObject()
                radio_group.update({
                    NameObject("/T"): TextStringObject(group_name),   # Group name
                    NameObject("/FT"): NameObject("/Btn"),            # Field Type: Button
                    NameObject("/Ff"): NumberObject(32768),           # 32768 = Radio flag
                    NameObject("/V"): NameObject("/Off")              # The currently selected value
                })

                # Register parent to get an IndirectObject reference pointer
                group_ref = writer._add_object(radio_group)

                add_field_to_acroform(writer, group_ref)

                radio_groups[group_name] = (radio_group, group_ref, [])

            (radio_group, group_ref, radio_buttons) = radio_groups[group_name]

            on = DictionaryObject({
                NameObject("/"+name): NameObject("/Annot"),
            })

            new_field = DictionaryObject({
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Widget"),
                NameObject("/Parent"): group_ref,
                NameObject("/AS"): NameObject("/Off"),      # Appearance State (/Yes /No)
                NameObject("/AP"): DictionaryObject({
                    NameObject("/N"): DictionaryObject({
                        NameObject("/"+name): writer._add_object(radio_selected),
                        NameObject("/Off"): writer._add_object(blank),
                    }),
                }),
                # /Rect [llx lly urx ury]
                NameObject("/Rect"): ArrayObject([
                    FloatObject(x),
                    FloatObject(y),
                    FloatObject(x+width),
                    FloatObject(y+height)]),
                NameObject("/F"): NumberObject(4), # Print flag (ensures it shows when printed)
                NameObject("/Ff"): NumberObject(32768), # 32768 = Radio flag

                # 25 0 obj
                # << /Female 26 0 R /Off 28 0 R >>
                # endobj

                # 18 0 obj
                # <<
                # /Border [ 0 0 1 ]
                # /Rect [ 87.6719 709.794 105.672 727.794 ]
                # /F 4
                # /BS 34 0 R
                # /Subtype /Widget /DA (/Helvetica 12 Tf 0 g) /MK 35 0 R /AP 36 0 R /H /P /Parent
                # 17 0 R /AS /Off /Type /Annot /Ff 49152 >>
                # endobj

                # 19 0 obj
                # <<
                # /Border [ 0 0 1 ] # h-radius v-radius width
                # /Rect [ 87.2463 682.216 105.246 700.216 ]
                # /F 4                            # Print Flag
                # /BS 21 0 R # Border Style?
                # /BS << /W 2 /S /D /D [3 2] >>  % 2‑pt dashed line, dash‑space pattern 3‑2 pt

                # 21 0 obj
                # << /S /I >> # Solid Inset
                # endobj

                ## Annotation Flags (TABLE 8.16)
                # Invisible = 0x1
                # Hidden = 0x2
                # Print = 0x4
                # NoZoom = 0x8
                # NoRotate = 0x10
                # NoView = 0x20
                # ReadOnly = 0x40
                # Locked = 0x80
                # ToggleNoView = 0x100
                # LockedContents = 0x200

                ## Button Field Flags (TABLE 8.75)
                # NoToggleToOff=0x4000
                # Radio=0x8000
                # PushButton=0x10000
                # RadiosInUnison=0x20000

                # /Subtype
                # /Widget
                # /DA (/ZapfDingbatsITC 12 Tf 0 g)
                # /MK 22 0 R
                # /AP 23 0 R
                # /H
                # /P
                # /Parent 17 0 R
                # /AS /Female
                # /Type /Annot
                # /Ff 49152 >>
                # endobj


            })

            # FIXME: For now have nothing selected
            # if value["selected"]:
                # new_field.update({
                    # NameObject("/AS"): NameObject("/"+name)
                # })

            new_field_ref = writer._add_object(new_field)

            add_field_to_annots(writer, page_index, new_field_ref)

            # Update Kids
            if NameObject("/Kids") not in radio_group:
                radio_group.update({
                    NameObject("/Kids"): ArrayObject([new_field_ref])
                })
            else:
                radio_group[NameObject("/Kids")].append(new_field_ref)

            # Update Opt
            if NameObject("/Opt") not in radio_group:
                radio_group.update({
                    NameObject("/Opt"): ArrayObject([TextStringObject(name)])
                })
            else:
                radio_group[NameObject("/Opt")].append(TextStringObject(name))



    # Write the modified structure back out
    with open(output_file, "wb") as f:
        writer.write(f)

    # print("Wrote to "+output_file)
