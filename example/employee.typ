#import "@local/typst-fillable:1.0.0": *

#set page(paper: "us-letter", margin: .5in)

First: #text_field("first", width: 150pt, height: 1em)

Last: #text_field("last", width: 150pt, height: 1em)

U.S Citizen: #checkbox_field("citizen")

Employment Type:
#radio_field("contractor", "employment_type", selected: false) Contractor
#radio_field("full-time", "employment_type", selected: false) Full-Time
#radio_field("part-time", "employment_type", selected: false) Part-Time

Hobbies:
#textarea_field("hobbies",  height: 1.5in)

#v(2em)

#grid(
  columns: (1fr, 1fr),

  //gutter: 5pt,
  row-gutter: 5pt,
  column-gutter: 5pt,

  [],
  {
    signature_field("employee_signature")
    {
      set block(above: 3pt, below: 3pt)
      line(stroke: 1pt, length: 100%)
    }
    [Employee Signature]
  }
)
