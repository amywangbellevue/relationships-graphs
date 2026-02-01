# People Relationship Graph

A Python tool for modeling and visualizing directional, multi-type relationships
between people.

## Features
- visual spring-loaded graph displaying relationships as edges and people as nodes
- three types of relationships: positive (denoted + in the table), negative (denoted -), and working (denoted ~ and for relationships that are neutral and/or workplace in nature)
- multi-select for simultaneous multiple kinds of relationships between two people
- curved graph lines for one-directional relationships and straight graph lines for reciprocal relationship
- .csv file importing for relationships between people
- table view for quicker editing of relationships between existing people (people with no relationships are removed)

## Example
```bash
python people_graph.py
```
(This is a placeholder lol)

## TODO
- ~~DONE: visual interface with a table where you can check cells off to indicate presence of a relationship (or uncheck to indicate lack of)~~
- ~~DONE: live graph updates~~
- TODO: different tracks for different kinds of relationships for visibility
- TODO: make the UI less laggy?
  - possible fix: calculate/render after user finishes resizing window, not during/calculate in the background while the resizing/scrolling is happening/navigation with arrow keys so we render one new row/col at a time?
- TODO: make the UI more visually appealing and possibly less visually confusing...
- TODO: make nodes dragable
- TODO: allow reopening of table editing view after closing table and opening graph
- TODO: editing from graph view?
- TODO: allow people with no relationships to persist
  - possible fix: allow self-relationships, probably in a separate CSV that gets loaded in alongside the main relationships CSV. Self-relationships should not display or be editable. (Then to delete a person, we would delete the self-relationship)
- TODO: rewrite this in Rust... (I have to actually learn Rust first T-T)
- TODO: negative relationship line as bomb emojis for the funny as an easter egg?
