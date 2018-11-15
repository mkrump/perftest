import logging

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from timeit import default_timer as timer
import pandas as pd

base_urls = {
    'ec2': 'http://myohdsiapplication.us-east-1.elasticbeanstalk.com',
    'demo': 'http://www.ohdsi.org/web/atlas/'
}

test_terms = [
    'tetracycline',
    'minocycline',
    'acne',
    'malaria',
    'tretinoin',
    'isotretinoin'
]
modal_timeout = 5
load_timeout = 120


def accept_terms(driver, query):
    driver.get(query)
    accept_terms_button_xpath = "//button[@class='terms-and-conditions__btn btn btn-success']"
    wait = WebDriverWait(driver, modal_timeout)
    accept_terms_button_present = EC.element_to_be_clickable((By.XPATH, accept_terms_button_xpath))
    button = wait.until(accept_terms_button_present)
    return button.click()


def wait_for_results(driver, query):
    start = timer()
    driver.get(query)
    paginate_buttion_xpath = "//a[@class='paginate_button current']"
    paginate_button_present = EC.presence_of_element_located((By.XPATH, paginate_buttion_xpath))
    wait = WebDriverWait(driver, load_timeout)
    wait.until(paginate_button_present)
    end = timer()
    return start, end


def generate_query(base_url, term):
    return "{}/#/search/{}".format(base_url, term)


def main():
    driver = webdriver.Chrome()
    for name, base_url in base_urls.items():
        with open(name + '.csv', 'w') as f:
            f.write("source,total_load_time\n")
            query = generate_query(base_url, 'fake-search')
            try:
                accept_terms(driver, query)
            except TimeoutException:
                logging.info("modal not found")
            for term in test_terms:
                start, end = 0, 9999
                query = generate_query(base_url, term)
                try:
                    start, end = wait_for_results(driver, query)
                except TimeoutException:
                    logging.info("page load exceeds timeout")
                f.write("{},{}\n".format(query, end - start))
    driver.quit()


if __name__ == '__main__':
    main()
    for perf in base_urls.keys():
        df = pd.read_csv(perf + '.csv')
        print('-------- {} --------'.format(perf))
        print(df.describe())
        print('\n')
