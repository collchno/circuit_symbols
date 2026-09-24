# circuit_symbols
A repo for inkscape/svg circuit and related symbols

# Usage Instructions

## Installation
- Clone the repo to wherever you clone your repos, e.g.:
`/.../repos/circuit_symbols`
- Go to your inkscape symbols dir, and link the svg file. On linux, this should be:
`ln -s .../circuit_symbols/circuit_symbols.svg ~/.config/inkscape/symbols/circuit_symbols.svg`
- Restart inkscape, and the symbols panel should now be available in the Symbold panel (CNTL+SHIFT+Y)

## Add a symbol to the library
- Open `circuit_symbols.svg` in inkscape.
- Create your drawing
- Group all the content (lines etc) in your drawing by selecting everything and hitting CNTL+G
- Go to the object properties and name your symbol in the `ID` field. Hit the `Set` button
- Go to the `Symbols` panel, set the drop down to Current document, select your new group, and hit the `+` symbol.
- Your new group should now appear in the symbols panel. Save the document and exit.
 
