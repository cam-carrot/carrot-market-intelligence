from flask import Flask, render_template, request, flash, jsonify
import folium
import logging
import asyncio
from logging.config import dictConfig
import os
import sys

from config.settings import LOGGING
from config.constants import MARKET_TAGS
from engine.market_engine import MarketAnalysisEngine
from engine.search_engine import SearchEngine
from services.seo_service import SEOService

# Initialize logging
dictConfig(LOGGING)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key_here'  # Move to settings in production
app.config['DEBUG'] = True

engine = MarketAnalysisEngine()
search_engine = SearchEngine()

# Increase recursion limit for Heroku
if 'DYNO' in os.environ:
    sys.setrecursionlimit(3000)

# Custom filter for number formatting
@app.template_filter('format_number')
def format_number(value):
    return "{:,}".format(int(value))

def create_map(similar_cities, target_city, target_state):
    target_city_state = f"{target_city}, {target_state}".lower().strip()
    
    target_lat, target_lon = similar_cities.loc[target_city_state, ['lat', 'lng']]
    m = folium.Map(location=[target_lat, target_lon], zoom_start=8)

    for idx, row in similar_cities.iterrows():
        color = 'red' if idx == target_city_state else \
                'green' if row['opportunity_category'] == 'High' else \
                'orange' if row['opportunity_category'] == 'Average' else 'blue'
        
        folium.Marker(
            [row['lat'], row['lng']],
            popup=f"{idx}<br>Opportunity: {row['opportunity_category']}",
            tooltip=idx,
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)

    return m._repr_html_()

@app.route('/')
def index():
    logger.info("Index route accessed")
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
async def analyze():
    try:
        target_city = request.form['city']
        target_state = request.form['state']
        radius = int(request.form['radius'])  # Get the radius from the form
        
        app.logger.info(f"Analyzing market for {target_city}, {target_state} with radius {radius} miles")
        
        similar_cities = engine.find_similar_cities(target_city, target_state, radius_miles=radius)
        app.logger.info(f"Found {len(similar_cities)} similar cities")
        
        # Convert DataFrame to list of dictionaries
        similar_cities_list = similar_cities.to_dict('records')
        app.logger.debug(f"Similar cities data: {similar_cities_list}")
        
        target_data = similar_cities.loc[f"{target_city}, {target_state}".lower()].to_dict()
        app.logger.debug(f"Target data: {target_data}")
        
        map_html = create_map(similar_cities, target_city, target_state)

        market_analysis = await search_engine.analyze_market(target_city, target_state)
        
        # Add some debug logging
        app.logger.debug(f"Similar cities list: {similar_cities_list}")
        
        # Extract websites and filter out None/empty values
        competitor_domains = [
            city.get('website') 
            for city in similar_cities_list 
            if city.get('website')
        ]
        
        app.logger.debug(f"Competitor domains to analyze: {competitor_domains}")
        
        seo_metrics = {}
        if competitor_domains:  # Only proceed if we have domains to analyze
            try:
                seo_service = SEOService()
                seo_metrics = await seo_service.get_bulk_metrics(set(competitor_domains))  # Use bulk_metrics instead
                app.logger.debug(f"SEO Metrics retrieved: {seo_metrics}")
            except Exception as e:
                app.logger.error(f"Error fetching SEO metrics: {str(e)}")
                seo_metrics = {}
        
        return render_template('results.html',
                           target_city=target_city,
                           target_state=target_state,
                           target_data=target_data,
                           similar_cities=similar_cities_list,
                           map_html=map_html,
                           market_tags=MARKET_TAGS,
                           market_analysis=market_analysis,
                           seo_metrics=seo_metrics)  # Verify this is being passed
    except Exception as e:
        app.logger.error(f"Error in analyze route: {str(e)}")
        return render_template('404.html', error=str(e))

@app.route('/results', methods=['GET'])
async def results():
    try:
        target_city = request.args.get('city')
        target_state = request.args.get('state')
        radius = int(request.args.get('radius'))
        
        app.logger.info(f"Analyzing market for {target_city}, {target_state} with radius {radius} miles")
        
        similar_cities = engine.find_similar_cities(target_city, target_state, radius_miles=radius)
        app.logger.info(f"Found {len(similar_cities)} similar cities")
        
        # Convert DataFrame to list of dictionaries
        similar_cities_list = similar_cities.to_dict('records')
        app.logger.debug(f"Similar cities data: {similar_cities_list}")
        
        target_data = similar_cities.loc[f"{target_city}, {target_state}".lower()].to_dict()
        app.logger.debug(f"Target data: {target_data}")
        
        map_html = create_map(similar_cities, target_city, target_state)

        market_analysis = await search_engine.analyze_market(target_city, target_state)
        
        # Get SEO metrics for competitor domains
        seo_metrics = {}
        competitor_domains = [city.website for city in similar_cities if hasattr(city, 'website') and city.website]
        
        try:
            seo_service = SEOService()
            seo_metrics = await seo_service.get_metrics_for_domains(competitor_domains)
        except Exception as e:
            app.logger.error(f"Error fetching SEO metrics: {e}")
            seo_metrics = {}  # Fallback to empty dict if there's an error

        return render_template(
            'results.html',
            target_city=target_city,
            target_state=target_state,
            target_data=target_data,
            similar_cities=similar_cities,
            map_html=map_html,
            market_tags=MARKET_TAGS,
            seo_metrics=seo_metrics
        )
    except ValueError as e:
        if "not found in the dataset" in str(e):
            app.logger.warning(f"City not found: {target_city}, {target_state}")
            return render_template('cityerror.html', city=target_city, state=target_state)
        else:
            app.logger.error(f"Error in analyze route: {str(e)}", exc_info=True)
            return render_template('cityerror.html', error_message=str(e))
    except Exception as e:
        app.logger.error(f"Error in analyze route: {str(e)}", exc_info=True)
        return render_template('cityerror.html', error_message=str(e))

@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"404 error: {request.url}")
    return render_template('404.html'), 404

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)