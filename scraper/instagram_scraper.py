import requests
import time
import random
import re
import json
from bs4 import BeautifulSoup
import config

class InstagramScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def delay_between_requests(self):
        """Introduce a random delay between requests to mimic human behavior."""
        delay = random.uniform(config.SCRAPER_DELAY_MIN, config.SCRAPER_DELAY_MAX)
        time.sleep(delay)
    
    def get_profile_posts(self, profile_name, keywords=None):
        """Scrape posts from a public Instagram profile."""
        if keywords and not isinstance(keywords, list):
            keywords = [keywords]
        
        url = f"https://www.instagram.com/{profile_name}/"
        
        matching_posts = []
        
        try:
            # Get the profile page
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {"error": f"Failed to access profile: {response.status_code}"}
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the shared data JSON
            script_pattern = re.compile(r'window\._sharedData = (.+?);</script>')
            script_matches = script_pattern.search(response.text)
            
            if not script_matches:
                return {"error": "Could not extract profile data"}
            
            shared_data = json.loads(script_matches.group(1))
            
            # Extract posts data
            try:
                user_data = shared_data['entry_data']['ProfilePage'][0]['graphql']['user']
                posts = user_data['edge_owner_to_timeline_media']['edges']
                
                # Process each post
                for post in posts:
                    node = post['node']
                    
                    # Extract caption if available
                    caption = ""
                    if node.get('edge_media_to_caption') and node['edge_media_to_caption']['edges']:
                        caption = node['edge_media_to_caption']['edges'][0]['node']['text']
                    
                    # Filter by keywords if provided
                    if keywords:
                        caption_lower = caption.lower()
                        matched_keywords = []
                        
                        for keyword in keywords:
                            if keyword.lower() in caption_lower:
                                matched_keywords.append(keyword)
                        
                        if not matched_keywords:
                            continue
                    else:
                        matched_keywords = []
                    
                    # Create post object
                    post_data = {
                        'id': node['id'],
                        'caption': caption,
                        'postDate': node['taken_at_timestamp'],
                        'postLink': f"https://www.instagram.com/p/{node['shortcode']}/",
                        'profileName': profile_name,
                        'matchedKeywords': matched_keywords
                    }
                    
                    matching_posts.append(post_data)
                    
                    # Simulate human-like behavior
                    self.delay_between_requests()
                
                return matching_posts
                
            except KeyError as e:
                return {"error": f"Failed to extract posts: {str(e)}"}
                
        except Exception as e:
            return {"error": f"Scraping error: {str(e)}"}