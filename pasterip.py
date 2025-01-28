import re, os, sys, time, requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

pages = [] # all page/s forking from main page
links = [] # all individual pastes

page_user = None

# setup colors
r = '\033[1m\033[31m' #red
w = '\033[1m\033[37m' #white
g = '\033[1m\033[32m' #green

def download(paste, path):
    # get paste content
    response = requests.get(paste)
    
    if not response.status_code == 200:
        print(f'{r}----> Error! Unable to download {paste}')
    else:
        print(f'{g}----> File downloaded: {paste}')
    
    # format file
    parsed_url = urlparse(paste)
    
    filename = os.path.basename(parsed_url.path) + '.txt'
    
    # setup download path
    file_path = os.path.join(path, filename)
    
    # write to disk
    try:
        with open(file_path, "w") as file:
            file.write(response.text)
            file.close()
    except:
        print(f'{w}----> Error! Could not write to disk! {paste}')

def scrape(page):
    global links
    
    # get html for each page
    response = requests.get(page)
    
    if response.status_code != 200:
        # if request wasnt successful...
        return []
        
    # parse page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # dind all div elements that have "data-key" attribute
    divs = soup.find_all('div', attrs={'data-key': True})
    
    # Extract links under the div elements
    for div in divs:
        # Look for the <a> tag under this div
        a_tag = div.find_next('a', href=True)
        if a_tag:
            # format extracted hyperlink
            paste = 'https://pastebin.com/raw' + a_tag['href']
        
            # add to list
            links.append(paste)
    
def find_pages(page):
    # get html on main page
    response = requests.get(page)
    
    # if request wasnt successful...
    if response.status_code != 200:
        sys.exit(f'\r\n{r}Error! Unable to reach page!{w}\r\n')

    # parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # find pastebin "pagination" html div
    pagination_div = soup.find('div', class_='pagination')

    if pagination_div:
        # find <a> tags w/in the pagination div
        page_links = pagination_div.find_all('a')

        # extract href links for each page (excluding the "oldest" link)
        found_pages = [link.get('href') for link in page_links if link.get('href') and page_user in link.get('href')]

        if found_pages:
            for new_page in found_pages:
                # add to pages list
                pages.append(new_page)
        else:
            # no forked pages found. scrape only main page
            pages.append(page + '/1')
    else:
        # html anomaly. add only main page
        pages.append(page + '/1')
    
def format(page):
    # extract user from url

    global page_user

    match = re.search(r"pastebin\.com/u/([a-zA-Z0-9_-]+)", page)
    
    if match:
        user = match.group(1)
        
        page_user = '/u/' + user
        
        return user
    else:
        sys.exit(f'\r\n{r}Error! User not found/bad page...{w}\r\n')
    
def main():
    global pages, links

    # display banner
    print('\r\n' * 20)
    print(f'''
{w}  ______                        {r} ______  _                         
{w} (_____ \             _         {r}(_____ \(_)                        
{w}  _____) )____  ___ _| |_ _____ {r} _____) )_ ____  ____  _____  ____ 
{w} |  ____(____ |/___|_   _) ___ |{r}|  __  /| |  _ \|  _ \| ___ |/ ___)
{w} | |    / ___ |___ | | |_| ____|{r}| |  \ \| | |_| | |_| | ____| |    
{w} |_|    \_____(___/   \__)_____){r}|_|   |_|_|  __/|  __/|_____)_|    
{w}                                {r}          |_|   |_|                    
''')

    # capture user-input
    try:
        page = input(f'{w}Pastebin page:{r} ')
        
        # ensure correct formatting
        user = format(page)
        page = 'https://pastebin.com/u/' + user
        
        path = input(f'{w}Rip to folder (ex- /tmp/Files/):{r} ')
        
        # confirm folder exists
        if not os.path.exists(path):
            sys.exit(f'\r\n{w}Error! Invalid path...{r}\r\n')
        
        wait = float(input(f'{w}Sleep in M/s (default 100|0=none):{r} '))
        
        input(f'\r\n{w}Ready? Strike ENTER to begin scraping...\r\n')
    except KeyboardInterrupt:
        pass
    except Exception as e:
        pass

    # calculate cummulative pages
    print(f'{w}[{g}~{w}] Gathering hyperlinks from all page/s! Stand-by...')
    find_pages(page)

    for new_page in pages:
        scrape(new_page)
    
    # download all pastes
    print(f'\r\n{w}[{r}!{w}] Ripping all pastes!\r\n')
    try:
        for paste in links:
            download(paste, path)
            
            if wait != 0:
                time.sleep(wait / 1000)
    except KeyboardInterrupt:
        sys.exit(f'\r\n{w}Aborted!\r\n')

    sys.exit(f'\r\n{w}Rip complete! More free junk @ Github.com/Waived\r\n')
    
if __name__ == '__main__':
    main()
