# pybabyplus

Converts the Baby+ app's (https://philips-digital.com/baby-new/) data export (``babyplus_data_export.json``) using Python Pandas
into a multi-sheet Excel file with various pivot tables, visualizations (TODO), etc.


# TODO

- map Ontology and the tag parser to Kõnele rewrite rules
- integrate reference charts (growth, Beba Pre food intake, etc.)
- color table cells based on Ontology

## Plots

- daily food intake
- duration between shits
- event stream of cumulative food intake, that is zerod by the eventual shit
  (color-coded by the color of shit)
