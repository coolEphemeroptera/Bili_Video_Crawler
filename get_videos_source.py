from playwright.sync_api import sync_playwright
import re


class BLVideoSearch:
    def __init__(self, playwright: sync_playwright, headless=True) -> None:
        self.browser = playwright.chromium.launch(headless=headless)

    def log(self, message):
        print(f"[{self.__class__.__name__}]: {message}")

    def make_url(self, keyword=["机器学习"]):
        keyword = "+".join(keyword)
        return f"https://search.bilibili.com/video?keyword={keyword}"

    def get_pages(self, page):
        path = '//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div/div'
        element = page.query_selector(f'xpath={path}')
        pages = 0
        if element:
            text = element.text_content()
            pages = int(text.split('...')[1].replace("下一页", ""))
        return pages

    def get_video_href(self, page, match_str='//www.bilibili.com/video'):
        page.wait_for_selector('a[data-mod="search-card"]', state="attached", timeout=10000)
        links = page.query_selector_all('a[data-mod="search-card"]')
        hrefs = set()
        for link in links:
            href = link.get_attribute('href')
            if href and re.match(match_str, href):
                href = "https:" + href
                hrefs.add(href)
        return hrefs

    def run(self, base_url, outfile):
        context = self.browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.goto(base_url)
        self.log(f"Opened URL: {base_url}")

        pages = self.get_pages(page)
        self.log(f"Total pages detected: {pages}")

        results = set()
        for i in range(pages):
            url = f"{base_url}&page={i + 1}"
            page.goto(url)
            self.log(f"Accessing page {i + 1}/{pages}: {url}")

            try:
                hrefs = self.get_video_href(page)
                results.update(hrefs)
                self.log(f"Collected {len(results)} videos so far.")
            except Exception as e:
                self.log(f"Error occurred, skipping... Reason: {str(e)}")

        with open(outfile, 'w+', encoding='utf-8') as f:
            for item in results:
                print(item, file=f)


if __name__ == "__main__":
    
    with sync_playwright() as playwright:
        searcher = BLVideoSearch(playwright, headless=True)
        url = searcher.make_url(keyword=["小学公开课"])
        searcher.run(url, outfile="videos_url.txt")
