#!/usr/bin/python3

from selenium import webdriver

from time import sleep
from retrying import retry

d = webdriver.Firefox()
url = "https://www.muckrock.com/accounts/login/?next=/"
d.get(url)

password_fh = open('/home/matt/.muckrock_password')
password = password_fh.readline().strip()

e = d.find_element_by_id("id_username")
e.send_keys("ChapFOIA")
e = d.find_element_by_id("id_password")
e.send_keys(password)

e = d.find_element_by_name("submit")
e.click()

d.get("https://www.muckrock.com/foi/list/?page=1&per_page=100")

ret = {}

def get_raw_emails():
    @retry(stop_max_attempt_number=7, wait_exponential_multiplier=5000, wait_exponential_max=10000)
    def get_raw_email_text(raw_url):
        d.get(raw_url)
        text = d.find_element_by_css_selector("html body pre").text

        return text

    while True:
        lists_url = d.current_url
        list_top = d.find_element_by_css_selector("html body.touch div.container div.content div.list.grid__row div.grid__column.three-quarters table.sortable.cardtable.stacktable.large-only tbody")
        link_elements = list_top.find_elements_by_class_name("bold") #request links
        request_urls = [link.get_attribute("href") for link in link_elements]

        for url in request_urls:
            d.get(url)
            request_no = int(url.split('-')[-1][:-1])

            response_list_elem = d.find_element_by_class_name("communications-list")

            responses = response_list_elem.find_elements_by_css_selector('[class=" collapsable communication textbox  "')
            raw_responses = [ r.find_elements_by_partial_link_text("Raw") for r in responses if r.find_elements_by_partial_link_text("Raw") ]

            raw_page_urls = [ e[0].get_attribute("href") for e in raw_responses ]

            for raw_url in raw_page_urls:
                raw_email_no = int(raw_url.split('/')[-2])
                text = get_raw_email_text(raw_url)
                yield request_no, raw_email_no, text

        d.get(lists_url)
        next_page = d.find_element_by_link_text("Next Page")
        next_page.click()

emails = []

for request_no, email_no, text in get_raw_emails():
    emails.append((request_no, email_no, text))
