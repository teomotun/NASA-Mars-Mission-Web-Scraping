import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import tweepy

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=True)

def scrape_info():
    browser = init_browser()
    # NASA Mars News url
    news_url = "https://mars.nasa.gov/news/"
    try:
        browser.visit(news_url)
        html = browser.html
        soup = bs(html, "html.parser")
        article = soup.find("div", class_='list_text')
        news_title = article.find("div", class_="content_title").text
        news_p = article.find("div", class_ ="article_teaser_body").text
    except:
        pass
    
    # JPL Mars Space Images url
    jps_mars_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    try:
        browser.visit(jps_mars_url)
        html = browser.html
        soup = bs(html, "html.parser")
        featured_image_url = 'https://www.jpl.nasa.gov'+soup.find("a", class_='button fancybox')['data-fancybox-href']
    except:
        pass
    
    # Mars Weather FROM TWITTER
        # Twitter API Keys
    def get_file_contents(filename):
        try:
            with open(filename, 'r') as f:
                return f.read().strip()
        except:
            pass

    consumer_key = get_file_contents('consumer_key.py')
    consumer_secret = get_file_contents('consumer_secret.py')
    access_token = get_file_contents('access_token.py')
    access_token_secret = get_file_contents('access_token_secret.py')

    # Setup Tweepy API Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    target_user = "MarsWxReport"
    tweet = api.user_timeline(target_user, count=1)
    mars_weather = (tweet)[0]["text"].replace('\n', ' ').split("…")[0]

    # Mars Facts
    facts_url = "https://space-facts.com/mars/"
    facts_table = pd.read_html(facts_url)[0]
    facts_table.columns = ["Description", "Value"]
    facts_table.set_index("Description", inplace=True)
    facts_table.to_csv("Output/mars_facts_table")
    facts_html = facts_table.to_html().replace('\n', '')
    
    # Mars Hemispheres
    hemisphere_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemisphere_url)
    hemisphere_image_urls = []
    try:
        html = browser.html
        soup = bs(html, "html.parser")
        for i in soup.find_all("div", class_='description'):
            browser.click_link_by_partial_text(f'{i.h3.text}')
            browser.click_link_by_id('wide-image-toggle')
            result = browser.find_by_xpath('//*[@id="wide-image"]/img')['src']
            hemisphere_image_urls.append({"title": i.h3.text, "img_url": result})
            browser.visit(hemisphere_url)
    except:
        pass
    browser.quit()
     
    nasa_data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image_url": featured_image_url,
        "mars_weather": mars_weather,
        "facts_html": facts_html,
        "hemisphere_image_urls": hemisphere_image_urls
    } 

    # Return results
    return nasa_data