#!/usr/bin/env python3
"""
Demo script for the DieAI Knowledge Library
Shows how to use all the main components
"""

try:
    from dieai_knowledge import KnowledgeBase, MathSolver, ScienceFacts, UnitConverter
except ImportError:
    print("DieAI Knowledge Library not installed. Install with: pip install dieai-knowledge")
    print("For local development, run from the project directory:")
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dieai_knowledge import KnowledgeBase, MathSolver, ScienceFacts, UnitConverter

def demo_knowledge_base():
    """Demonstrate KnowledgeBase functionality"""
    print("=== KNOWLEDGE BASE DEMO ===")
    
    kb = KnowledgeBase()
    
    # Search for information
    print("\n1. Searching for 'pythagorean theorem':")
    results = kb.search("pythagorean theorem")
    for result in results[:2]:  # Show first 2 results
        print(f"Section: {result['section']}")
        for content in result['content'][:1]:  # Show first content line
            print(f"  - {content}")
    
    # Get available sections
    print("\n2. Available knowledge sections:")
    sections = kb.get_all_sections()
    for section in sections:
        print(f"  - {section}")
    
    # Get constants
    print("\n3. Mathematical constants:")
    constants = kb.get_constants()
    for name, value in list(constants.items())[:3]:  # Show first 3
        print(f"  {name}: {value}")

def demo_math_solver():
    """Demonstrate MathSolver functionality"""
    print("\n=== MATH SOLVER DEMO ===")
    
    solver = MathSolver()
    
    # Solve simple equations
    print("\n1. Solving equations:")
    equation = "15 + 25"
    result = solver.evaluate(equation)
    print(f"  {equation} = {result}")
    
    # Geometry calculations
    print("\n2. Geometry calculations:")
    circle = solver.geometry_calculator("circle", radius=5)
    if 'area' in circle:
        print(f"  Circle (r=5): Area = {circle['area']:.2f}, Circumference = {circle['circumference']:.2f}")
    
    # Statistics
    print("\n3. Statistics:")
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    stats = solver.statistics(data)
    if 'mean' in stats:
        print(f"  Data {data}")
        print(f"  Mean: {stats['mean']:.2f}, Median: {stats['median']}, Std Dev: {stats['standard_deviation']:.2f}")
    
    # Quadratic equation
    print("\n4. Quadratic equation (x² - 5x + 6 = 0):")
    quad = solver.solve_quadratic(1, -5, 6)
    if 'solutions' in quad:
        print(f"  Solutions: {quad['solutions']}")

def demo_science_facts():
    """Demonstrate ScienceFacts functionality"""
    print("\n=== SCIENCE FACTS DEMO ===")
    
    science = ScienceFacts()
    
    # Get constants
    print("\n1. Scientific constants:")
    speed_of_light = science.get_constant("c", "physics")
    if speed_of_light:
        print(f"  Speed of light: {speed_of_light['value']} {speed_of_light['unit']}")
    
    avogadro = science.get_constant("N_A", "chemistry")
    if avogadro:
        print(f"  Avogadro's number: {avogadro['value']:.2e} {avogadro['unit']}")
    
    # Physics calculations
    print("\n2. Physics calculations:")
    force = science.calculate_physics("force", mass=10, acceleration=9.8)
    if 'force' in force:
        print(f"  Force (F=ma): {force['force']} N (mass=10kg, acceleration=9.8m/s²)")
    
    kinetic_energy = science.calculate_physics("kinetic_energy", mass=5, velocity=20)
    if 'kinetic_energy' in kinetic_energy:
        print(f"  Kinetic Energy: {kinetic_energy['kinetic_energy']} J (mass=5kg, velocity=20m/s)")
    
    # Chemistry calculations
    print("\n3. Chemistry calculations:")
    molarity = science.calculate_chemistry("molarity", moles=2, volume=1)
    if 'molarity' in molarity:
        print(f"  Molarity: {molarity['molarity']} M (2 moles in 1 L)")
    
    # Periodic table
    print("\n4. Periodic table:")
    carbon = science.get_periodic_element("C")
    if carbon:
        print(f"  Carbon: Atomic number {carbon['atomic_number']}, mass {carbon['atomic_mass']}")

def demo_unit_converter():
    """Demonstrate UnitConverter functionality"""
    print("\n=== UNIT CONVERTER DEMO ===")
    
    converter = UnitConverter()
    
    # Length conversions
    print("\n1. Length conversions:")
    length = converter.convert(100, "meters", "feet")
    if 'converted_value' in length:
        print(f"  100 meters = {length['converted_value']:.2f} feet")
    
    # Mass conversions
    print("\n2. Mass conversions:")
    mass = converter.convert(10, "kilograms", "pounds")
    if 'converted_value' in mass:
        print(f"  10 kg = {mass['converted_value']:.2f} pounds")
    
    # Temperature conversions
    print("\n3. Temperature conversions:")
    temp = converter.convert(25, "celsius", "fahrenheit")
    if 'converted_value' in temp:
        print(f"  25°C = {temp['converted_value']:.1f}°F")
    
    # Multiple conversions
    print("\n4. Multiple conversions (1 meter to various units):")
    multiple = converter.convert_multiple(1, "meters", ["feet", "inches", "centimeters"])
    if 'conversions' in multiple:
        for unit, value in multiple['conversions'].items():
            if isinstance(value, (int, float)):
                print(f"  1 meter = {value:.2f} {unit}")

def main():
    """Run all demos"""
    print("DieAI Knowledge Library Demo")
    print("=" * 40)
    
    try:
        demo_knowledge_base()
        demo_math_solver()
        demo_science_facts()
        demo_unit_converter()
        
        print("\n" + "=" * 40)
        print("Demo completed successfully!")
        print("\nTo use this library in your projects:")
        print("1. Install: pip install dieai-knowledge")
        print("2. Import: from dieai_knowledge import KnowledgeBase, MathSolver, ScienceFacts, UnitConverter")
        print("3. Check the README.md for detailed examples and API documentation")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        print("Make sure the dieai_knowledge package is properly installed.")

if __name__ == "__main__":
    main()