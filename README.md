# carrot-market-intelligence

# Market Analysis Engine

A Flask-based web application that performs comprehensive market analysis for real estate investors. The application combines demographic data, search rankings, and SEO metrics to provide insights into different markets.

## Features

- **Market Comparison**: Analyzes and compares similar markets based on demographic data
- **Search Rankings**: Tracks search engine rankings for key real estate investment terms
- **SEO Analysis**: Provides detailed SEO metrics including domain authority and backlink data
- **iBuyer Detection**: Identifies and tracks iBuyer presence in markets
- **Interactive Visualizations**: Includes maps and charts for data visualization

## Technologies

- Python 3.11
- Flask (Async)
- Hypercorn
- Pandas
- Scikit-learn
- SEMrush API
- Serper.dev API
- Folium (for mapping)

## Prerequisites

Before you begin, ensure you have:
- Python 3.11 or higher installed
- A SEMrush API key
- A Serper.dev API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/market-analysis-engine.git
cd market-analysis-engine
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
FLASK_APP=app.py
FLASK_ENV=development
SERPER_API_KEY=your_serper_key
SEMRUSH_API_KEY=your_semrush_key
```

## Configuration

The application uses several configuration files:
- `config/settings.py` - Application settings
- `config/constants.py` - Constant values like iBuyer lists
- `hypercorn.conf.py` - Server configuration

## Running Locally

1. Make sure your environment variables are set
2. Run the application:
```bash
hypercorn app:app --config hypercorn.conf.py
```

The application will be available at `http://localhost:8000`

## Deployment to Heroku

1. Install the Heroku CLI
2. Login to Heroku:
```bash
heroku login
```

3. Create a new Heroku app:
```bash
heroku create your-app-name
```

4. Set environment variables:
```bash
heroku config:set SERPER_API_KEY=your_serper_key
heroku config:set SEMRUSH_API_KEY=your_semrush_key
heroku config:set FLASK_APP=app.py
heroku config:set FLASK_ENV=production
```

5. Deploy:
```bash
git push heroku main
```

## Project Structure
```
market-analysis-engine/
├── app.py              # Main application file
├── config/            
│   ├── __init__.py
│   ├── settings.py     # Configuration settings
│   └── constants.py    # Constants and iBuyer lists
├── services/
│   ├── __init__.py
│   ├── search_service.py
│   └── seo_service.py
├── models/
│   └── __init__.py
├── utils/
│   └── domain_utils.py
├── templates/
│   ├── index.html
│   └── results.html
├── requirements.txt
├── Procfile
├── runtime.txt
└── README.md
```

## API Dependencies

### SEMrush API
- Used for domain authority and backlink analysis
- Required fields: ascore, total, domains_num

### Serper.dev API
- Used for search rankings analysis
- Returns organic search results

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| SERPER_API_KEY | API key for Serper.dev | Yes |
| SEMRUSH_API_KEY | API key for SEMrush | Yes |
| FLASK_APP | Flask application entry point | Yes |
| FLASK_ENV | Application environment | Yes |

