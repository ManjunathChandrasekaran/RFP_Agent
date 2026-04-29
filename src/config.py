import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
USE_AI_ENHANCEMENT = os.getenv('USE_AI_ENHANCEMENT', 'false').lower() == 'true'

# Default Pricing Configuration
DEFAULT_PRICING = {
    'junior': 50,
    'mid': 100,
    'senior': 150,
    'architect': 200,
}

# Markup and minimums
MARKUP_PERCENTAGE = 30
MINIMUM_PROJECT_COST = 5000

# Output formats
SUPPORTED_FORMATS = ['json', 'md', 'xlsx', 'html', 'csv']

# Requirement categories
REQUIREMENT_CATEGORIES = [
    'functional',
    'non_functional',
    'performance',
    'security',
    'compliance',
    'infrastructure',
    'integration',
    'support',
    'training',
]

# Effort estimation defaults (in hours)
DEFAULT_EFFORTS = {
    'simple_feature': 16,
    'moderate_feature': 40,
    'complex_feature': 80,
    'integration': 24,
    'api_endpoint': 12,
    'database_design': 20,
    'testing': 30,
    'documentation': 15,
    'deployment': 10,
    'training': 20,
}

# Risk factors (multiplier to effort)
RISK_FACTORS = {
    'low': 1.0,
    'medium': 1.25,
    'high': 1.5,
    'critical': 2.0,
}

# PDF Processing Configuration
PDF_CONFIG = {
    'max_file_size_mb': 50,
    'supported_formats': ['.pdf'],
    'extraction_method': 'pdfplumber',  # or 'PyPDF2'
}

# Output directory configuration
OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')
CONFIG_DIR = os.getenv('CONFIG_DIR', './config')
TEMPLATES_DIR = os.getenv('TEMPLATES_DIR', './templates')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', './rfp_agent.log')
