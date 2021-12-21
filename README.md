# pybabyplus

Converts the Baby+ app's (https://philips-digital.com/baby-new/; v2.9.3) data export (``babyplus_data_export.json``) using Python Pandas
into a multi-sheet Excel file with various pivot tables, visualizations, etc.


# TODO

- map Ontology and the tag parser to Kõnele rewrite rules
- integrate reference charts (growth, Beba Pre food intake, etc.)
- color table cells based on Ontology
- group time into 24 buckets
- DONE: dont plot "All" on the same figure as individual samples

## Plots

- daily food intake
- duration between shits
- event stream of cumulative food intake, that is zerod by the eventual shit
  (color-coded by the color of shit)
