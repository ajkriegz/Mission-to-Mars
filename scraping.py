# Import Splinter and BeautifulSoup
from xml.dom.minidom import Attr
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
# Import pandas to use .read_html() function
import pandas as pd
import datetime as dt


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True) # When we were testing our code in Jupyter, headless was set as False so we could see the scraping in action.
    
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemi_scrape(browser)
    }

    # Stop webdriver and return data   # Stop draining computer resources
    browser.quit()
    return data

def mars_news(browser):
    # ### NASA news site
    # Visit the mars nasa news site
    #url = 'https://redplanetscience.com'
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    # assigned parent element, slide_elem, as the variable to look for the <div /> tag and its descendent (the other tags within the <div /> element)
    html = browser.html
    news_soup = soup(html, 'html.parser')
    slide_elem = news_soup.select_one('div.list_text')

    # Add try/except for error handling
    try:

        # The data we're looking for is the content title, which we've specified by saying, "The specific data is in a <div /> with a class of 'content_title'."
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Alternatively
        # news_title = slide_elem.find('div', class_='content_title').text
        # news_title

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # ### Featured Images
    # Visit URL
    #url = 'https://spaceimages-mars.com'
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None 

    # Use the base URL to create an absolute URL # f-strings are evaluated at run-time
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url


def mars_facts():
    # ### Mars facts
    # import pandas inside dependencies to use .read_html() function
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        #df = pd.read_html('https://galaxyfacts-mars.com')[0]
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None
    
    # Assign columns and set index for df    
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert data back to html, add bootstrap
    return df.to_html()


def hemi_scrape(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    for x in range(4):
        hemispheres = {}
        browser.find_by_css('a.itemLink img')[x].click()
        page_html = browser.find_by_text('Sample')
        img_url = page_html['href']
        title = browser.find_by_css('h2.title').text
        hemispheres['img_url'] = img_url
        hemispheres['title'] = title
        hemisphere_image_urls.append(hemispheres)
        browser.back()

    # Return the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())