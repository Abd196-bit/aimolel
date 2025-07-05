# DieAI Knowledge Library

A comprehensive Python library for mathematics and science knowledge processing, providing tools for solving mathematical problems, accessing scientific facts, and performing unit conversions.

## Features

- **Mathematical Problem Solving**: Solve equations, calculate geometry, statistics, and more
- **Scientific Knowledge Base**: Access facts, formulas, and constants across multiple disciplines
- **Unit Conversion**: Convert between various units of measurement
- **Comprehensive Data**: Built-in knowledge base covering mathematics, physics, chemistry, and biology

## Installation

```bash
pip install dieai-knowledge
```

## Quick Start

```python
from dieai_knowledge import KnowledgeBase, MathSolver, ScienceFacts, UnitConverter

# Initialize components
kb = KnowledgeBase()
math_solver = MathSolver()
science = ScienceFacts()
converter = UnitConverter()

# Search the knowledge base
results = kb.search("pythagorean theorem")
print(results)

# Solve mathematical problems
result = math_solver.solve_equation("2x + 5 = 15")
print(f"Solution: {result}")

# Calculate physics problems
energy = science.calculate_physics("kinetic_energy", mass=10, velocity=20)
print(f"Kinetic Energy: {energy}")

# Convert units
conversion = converter.convert(100, "meters", "feet")
print(f"100 meters = {conversion['converted_value']:.2f} feet")
```

## Components

### KnowledgeBase

The knowledge base provides access to comprehensive mathematical and scientific information:

```python
from dieai_knowledge import KnowledgeBase

kb = KnowledgeBase()

# Search for information
results = kb.search("newton's laws")

# Get specific sections
physics = kb.get_section("PHYSICS")

# Find formulas
formulas = kb.find_formulas("physics")

# Explain concepts
explanation = kb.explain_concept("photosynthesis")
```

### MathSolver

Solve various types of mathematical problems:

```python
from dieai_knowledge import MathSolver

solver = MathSolver()

# Solve equations
linear = solver.solve_equation("3x - 7 = 14")
quadratic = solver.solve_quadratic(1, -5, 6)

# Calculate geometry
circle = solver.geometry_calculator("circle", radius=5)
rectangle = solver.geometry_calculator("rectangle", length=10, width=6)

# Statistics
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
stats = solver.statistics(data)

# Mathematical functions
fibonacci = solver.fibonacci(10)
factors = solver.prime_factors(60)
```

### ScienceFacts

Access scientific knowledge and perform calculations:

```python
from dieai_knowledge import ScienceFacts

science = ScienceFacts()

# Get scientific constants
speed_of_light = science.get_constant("c", "physics")
avogadro = science.get_constant("N_A", "chemistry")

# Calculate physics problems
force = science.calculate_physics("force", mass=10, acceleration=9.8)
kinetic_energy = science.calculate_physics("kinetic_energy", mass=5, velocity=20)

# Calculate chemistry problems
molarity = science.calculate_chemistry("molarity", moles=2, volume=1)
ph = science.calculate_chemistry("ph", h_concentration=1e-7)

# Get periodic table information
carbon = science.get_periodic_element("C")
hydrogen = science.get_periodic_element("Hydrogen")

# Get formulas
wave_formulas = science.search_formulas("wave")
```

### UnitConverter

Convert between various units of measurement:

```python
from dieai_knowledge import UnitConverter

converter = UnitConverter()

# Basic conversions
length = converter.convert(100, "meters", "feet")
mass = converter.convert(10, "kilograms", "pounds")
temperature = converter.convert(25, "celsius", "fahrenheit")

# Multiple conversions
multiple = converter.convert_multiple(100, "meters", ["feet", "inches", "yards"])

# Conversion chains
chain = converter.conversion_chain(1, ["meters", "centimeters", "millimeters"])

# Get supported units
units = converter.get_supported_units("length")
```

## Knowledge Base Content

The library includes comprehensive knowledge in:

### Mathematics
- Arithmetic and number theory
- Algebra and equation solving
- Geometry and trigonometry
- Calculus and derivatives
- Statistics and probability

### Physics
- Classical mechanics
- Thermodynamics
- Electromagnetism
- Wave physics
- Modern physics concepts

### Chemistry
- Atomic structure
- Chemical bonding
- Reaction kinetics
- Gas laws
- Solution chemistry

### Biology
- Cell biology
- Genetics
- Evolution
- Ecology
- Molecular biology

## Unit Conversion Support

The library supports conversion between units in:

- **Length**: meters, feet, inches, kilometers, miles, etc.
- **Mass**: kilograms, pounds, grams, ounces, etc.
- **Volume**: liters, gallons, cubic meters, etc.
- **Temperature**: Celsius, Fahrenheit, Kelvin, Rankine
- **Energy**: joules, calories, BTU, kWh, etc.
- **Power**: watts, horsepower, etc.
- **Pressure**: pascals, atmospheres, PSI, etc.
- **Time**: seconds, minutes, hours, days, etc.
- **Area**: square meters, acres, hectares, etc.

## API Reference

### KnowledgeBase Methods

- `search(query)`: Search for information
- `get_section(section_name)`: Get specific section content
- `find_formulas(subject)`: Extract formulas
- `explain_concept(concept)`: Get concept explanations

### MathSolver Methods

- `solve_equation(equation)`: Solve mathematical equations
- `solve_quadratic(a, b, c)`: Solve quadratic equations
- `geometry_calculator(shape, **kwargs)`: Calculate geometric properties
- `statistics(data)`: Calculate statistical measures
- `evaluate(expression)`: Evaluate mathematical expressions

### ScienceFacts Methods

- `get_constant(name, field)`: Get scientific constants
- `calculate_physics(formula_type, **kwargs)`: Physics calculations
- `calculate_chemistry(calculation_type, **kwargs)`: Chemistry calculations
- `get_periodic_element(identifier)`: Periodic table lookup

### UnitConverter Methods

- `convert(value, from_unit, to_unit)`: Basic unit conversion
- `convert_multiple(value, from_unit, target_units)`: Multiple conversions
- `get_supported_units(unit_type)`: List supported units

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please visit the [GitHub repository](https://github.com/dieai/dieai-knowledge).