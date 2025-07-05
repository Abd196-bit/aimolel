# Publishing DieAI Knowledge Library to PyPI

This guide shows you how to publish the `dieai-knowledge` library to PyPI.

## Prerequisites

1. **Create PyPI account**: Register at https://pypi.org/account/register/
2. **Install build tools**:
   ```bash
   pip install build twine
   ```

## Publishing Steps

### 1. Build the package

```bash
# From the project root directory
python -m build
```

This creates distribution files in the `dist/` directory:
- `dieai-knowledge-1.0.0.tar.gz` (source distribution)
- `dieai_knowledge-1.0.0-py3-none-any.whl` (wheel distribution)

### 2. Check the package

```bash
# Verify the package is correctly formatted
twine check dist/*
```

### 3. Test upload (optional but recommended)

Upload to TestPyPI first to verify everything works:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

You'll need to enter your TestPyPI credentials.

Test the installation:
```bash
pip install --index-url https://test.pypi.org/simple/ dieai-knowledge
```

### 4. Upload to PyPI

```bash
# Upload to the real PyPI
twine upload dist/*
```

Enter your PyPI credentials when prompted.

### 5. Verify installation

```bash
pip install dieai-knowledge
python -c "from dieai_knowledge import KnowledgeBase; print('Success!')"
```

## Package Structure

```
dieai-knowledge/
├── dieai_knowledge/           # Main package
│   ├── __init__.py           # Package initialization
│   ├── knowledge_base.py     # Knowledge base module
│   ├── math_solver.py        # Math solving module
│   ├── science_facts.py      # Science facts module
│   └── unit_converter.py     # Unit conversion module
├── data.txt                  # Training data file
├── demo_library.py           # Demo script
├── setup.py                  # Setup script (legacy)
├── pyproject.toml           # Modern build configuration
├── README.md                # Package documentation
├── LICENSE                  # MIT license
├── MANIFEST.in              # Include/exclude files
└── PYPI_PUBLISHING_GUIDE.md # This guide
```

## Key Features

The published library includes:

1. **KnowledgeBase**: Comprehensive math and science knowledge
2. **MathSolver**: Equation solving, geometry, statistics
3. **ScienceFacts**: Scientific constants, formulas, calculations
4. **UnitConverter**: Universal unit conversion system

## Version Management

To update the package:

1. Update version in `dieai_knowledge/__init__.py`
2. Update version in `pyproject.toml`
3. Rebuild and republish:
   ```bash
   python -m build
   twine upload dist/*
   ```

## Usage Example

After installation via `pip install dieai-knowledge`:

```python
from dieai_knowledge import KnowledgeBase, MathSolver, ScienceFacts, UnitConverter

# Initialize components
kb = KnowledgeBase()
solver = MathSolver()
science = ScienceFacts()
converter = UnitConverter()

# Use the library
results = kb.search("pythagorean theorem")
calculation = solver.solve_equation("2x + 5 = 15")
force = science.calculate_physics("force", mass=10, acceleration=9.8)
length = converter.convert(100, "meters", "feet")
```

## Troubleshooting

### Common Issues

1. **Build fails**: Ensure all dependencies are installed
2. **Upload rejected**: Check if version already exists on PyPI
3. **Import errors**: Verify package structure and __init__.py

### Testing Locally

Run the demo script to test functionality:
```bash
python demo_library.py
```

## Security Notes

- Never commit API keys or credentials
- Use API tokens for automated publishing
- Keep your PyPI account secure with 2FA

## License

This package is released under the MIT License. See LICENSE file for details.

## Support

For issues or questions:
- GitHub: https://github.com/dieai/dieai-knowledge
- Email: info@dieai.com