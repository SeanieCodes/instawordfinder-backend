import os
import sys

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper.instagram_scraper import InstagramScraper

def test_scraper():
    scraper = InstagramScraper()
    profile_name = "owls_of_.minerva"  # You can change this to any public Instagram profile
    keywords = ["told"]  # You can change these keywords
    
    print(f"Searching @{profile_name} for posts containing: {keywords}")
    results = scraper.get_profile_posts(profile_name, keywords)
    
    if not results:
        print("No posts found matching your criteria")
        return
    
    print(f"Found {len(results)} matching posts")
    
    # Display all results
    for i, post in enumerate(results, 1):
        print(f"\nPost {i}:")
        print(f"Date: {post['postDate']}")
        print(f"Link: {post['postLink']}")
        print(f"Matched keywords: {post.get('matchedKeywords', [])}")
        print(f"Caption: {post['caption']}")

if __name__ == "__main__":
    test_scraper()