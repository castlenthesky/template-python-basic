# Getting Started

Welcome to the project documentation! This guide will help you get up and running quickly.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd template-python-basic
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```

## Quick Start

Run the application:

```bash
uvicorn src.api.server:app --reload
```

The API will be available at `http://localhost:8000`

## Next Steps

- Check out the [API Guide](api-guide) for detailed endpoint documentation
- Review the [Configuration](configuration) for environment setup
- See [Examples](examples) for common use cases