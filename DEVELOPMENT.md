# Development Guide

## Setting Up Development Environment

### Prerequisites

- Python 3.8+
- pip or conda
- Git

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/ManjunathChandrasekaran/RFP_Agent.git
cd RFP_Agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Run tests
pytest tests/
```

## Project Structure

```
RFP_Agent/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration
│   ├── pdf_parser.py             # PDF extraction
│   ├── requirement_analyzer.py   # Requirement analysis
│   ├── compliance_matcher.py     # Capability matching
│   ├── cost_estimator.py         # Cost estimation
│   ├── timeline_generator.py     # Timeline generation
│   ├── response_generator.py     # Response generation
│   └── main.py                   # Orchestrator
├── tests/
│   ├── test_pdf_parser.py
│   ├── test_requirement_analyzer.py
│   ├── test_compliance_matcher.py
│   ├── test_cost_estimator.py
│   ├── test_timeline_generator.py
│   └── test_response_generator.py
├── samples/
│   ├── sample_rfp_1.pdf
│   ├── sample_rfp_2.pdf
│   └── sample_requirements.txt
├── output/                       # Generated outputs
├── requirements.txt
├── README.md
├── DEVELOPMENT.md
└── .gitignore
```

## Module Development Guide

### Adding a New Analysis Module

1. **Create new file**: `src/new_analyzer.py`

2. **Follow the pattern**:

```python
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class NewAnalyzer:
    """Description of what this analyzer does"""
    
    def __init__(self):
        """Initialize the analyzer"""
        pass
    
    def analyze(self, data: Dict) -> Dict:
        """
        Main analysis method
        
        Args:
            data: Input data
            
        Returns:
            Analysis results
        """
        try:
            # Implementation
            logger.info("Analysis complete")
            return results
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise
```

3. **Integrate into main.py**:

```python
from new_analyzer import NewAnalyzer

# In RFPAgent.__init__:
self.new_analyzer = NewAnalyzer()

# In process_rfp():
results = self.new_analyzer.analyze(data)
```

### Extending Requirement Types

1. Edit `requirement_analyzer.py`:

```python
class RequirementType(Enum):
    # Add new type:
    MY_TYPE = "my_type"
```

2. Add keywords for detection:

```python
KEYWORDS = {
    RequirementType.MY_TYPE: [
        'keyword1', 'keyword2', 'keyword3'
    ],
}
```

3. Add default effort estimate:

```python
DEFAULT_EFFORTS = {
    'my_type': 24,  # hours
}
```

### Customizing Pricing Models

Edit `cost_estimator.py`:

```python
class CostEstimator:
    DEFAULT_RATES = {
        'my_level': 200,  # $/hour
    }
    
    PRIORITY_MULTIPLIERS = {
        'critical': 1.5,
        # Add more levels
    }
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_pdf_parser.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v tests/
```

### Writing Tests

```python
import pytest
from src.pdf_parser import PDFParser

class TestPDFParser:
    
    def setup_method(self):
        """Setup before each test"""
        self.parser = PDFParser()
    
    def test_validate_pdf_valid(self):
        """Test PDF validation with valid file"""
        is_valid, msg = self.parser.validate_pdf("tests/samples/valid.pdf")
        assert is_valid is True
    
    def test_validate_pdf_invalid(self):
        """Test PDF validation with invalid file"""
        is_valid, msg = self.parser.validate_pdf("nonexistent.pdf")
        assert is_valid is False
    
    def test_extract_text(self):
        """Test text extraction"""
        text = self.parser.extract_text("tests/samples/sample.pdf")
        assert len(text) > 0
        assert isinstance(text, str)
```

## Code Style

### Formatting

Use Black for code formatting:

```bash
# Format all files
black src/

# Format specific file
black src/pdf_parser.py
```

### Linting

Use Flake8 for style checking:

```bash
# Check all files
flake8 src/

# With configuration
flake8 src/ --max-line-length=100
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `PDFParser`)
- **Functions/Methods**: snake_case (e.g., `extract_text`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_RATES`)
- **Private**: Leading underscore (e.g., `_internal_method`)

## Adding Sample RFPs

1. Place PDF files in `samples/` directory:
   ```bash
   samples/
   ├── sample_rfp_1.pdf
   ├── sample_rfp_2.pdf
   └── sample_rfp_complex.pdf
   ```

2. Test with:
   ```bash
   python src/main.py --rfp-file samples/sample_rfp_1.pdf --verbose
   ```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile main processing
cProfile.run('agent.process_rfp(pdf_file)', 'output.prof')

# Analyze
stats = pstats.Stats('output.prof')
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Optimization Tips

1. **Caching**: Cache parsed requirements
2. **Lazy Loading**: Load modules only when needed
3. **Parallel Processing**: Use multiprocessing for large PDFs
4. **Database**: Consider SQLite for caching

## Debugging

### Enable Debug Logging

```bash
python src/main.py --rfp-file test.pdf --verbose
```

### Debug with Python

```python
import pdb

# Set breakpoint
pdb.set_trace()

# Useful commands:
# n - next line
# s - step into
# c - continue
# p variable - print variable
# l - list code
```

### Logging Best Practices

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed info for diagnostics")
logger.info("General informational message")
logger.warning("Warning about something")
logger.error("Error occurred")
logger.critical("Critical issue")
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements.txt
      - run: pytest tests/
      - run: flake8 src/
```

## Building for Distribution

### Creating Package

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Upload to PyPI
twine upload dist/*
```

## Documentation

### Docstring Format

Follow Google-style docstrings:

```python
def process_requirement(requirement: Dict) -> Dict:
    """
    Process a single requirement.
    
    This function analyzes the requirement and categorizes it
    based on type and priority keywords.
    
    Args:
        requirement: Dictionary containing requirement data with keys:
            - 'id': Unique identifier
            - 'text': Requirement text
            - 'priority': Priority level
    
    Returns:
        Dictionary with processed requirement containing:
            - 'id': Requirement ID
            - 'type': Categorized type
            - 'priority': Priority level
            - 'effort': Estimated effort in hours
    
    Raises:
        ValueError: If requirement text is empty
        KeyError: If required keys missing from input
    
    Example:
        >>> req = {'id': 1, 'text': 'Build API', 'priority': 'high'}
        >>> result = process_requirement(req)
        >>> print(result['type'])
        'functional'
    """
    pass
```

## Release Process

1. **Update version** in relevant files
2. **Update CHANGELOG**
3. **Run full test suite**
4. **Create git tag**: `git tag v1.0.0`
5. **Push changes**: `git push origin main --tags`
6. **Build and distribute**

## Common Issues

### Issue: Import errors

```bash
# Ensure working directory is project root
cd /path/to/RFP_Agent

# Verify PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Test import
python -c "from src.pdf_parser import PDFParser"
```

### Issue: Dependency conflicts

```bash
# Clear and reinstall
pip install --upgrade --force-reinstall -r requirements.txt
```

### Issue: PDF parsing fails

- Ensure PDF is text-based (not scanned image)
- Try with different PDF files
- Check pdfplumber version: `pip list | grep pdfplumber`

## Getting Help

- Check logs: `cat rfp_agent.log`
- Enable verbose mode: `--verbose`
- Review generated JSON outputs
- Check GitHub issues: [Issues Page](https://github.com/ManjunathChandrasekaran/RFP_Agent/issues)

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and commit: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Create Pull Request

## Resources

- [Python Official Docs](https://docs.python.org/3/)
- [PyPDF2 Documentation](https://github.com/py-pdf/PyPDF2)
- [PDFPlumber Documentation](https://pdfplumber.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)

---

Happy coding! 🚀
