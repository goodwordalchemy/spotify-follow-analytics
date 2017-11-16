from selenium import webdriver
from selenium.webdriver import ActionChains                                                                                                                                          
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def login(url):
	config = {}
	config['facebook_email'] = ...
	config['facebook_password'] = ...

	options = webdriver.ChromeOptions()                                                                                                                                          
	# options.add_experimental_option(
	#   "excludeSwitches", 
	#   ["ignore-certificate-errors"]
	# ) # Suppress a command-line flag
	# driver = webdriver.Chrome(chrome_options=options, 
	#   service_args=["--verbose", "--log-path=webdriver.log"])
	service_args = ["--ignore-ssl-errors=true", "--ssl-protocol=any"]
	driver = webdriver.Chrome('/usr/local/bin/chromedriver')
	driver.set_window_size(1024,768)
	driver.implicitly_wait(2)

	print 'Navigating to Spotify ...'
	driver.get(url)
	# Click the "Already have an account" link
	action_chains = ActionChains(driver)
	login = WebDriverWait(driver, 60).until(
		EC.element_to_be_clickable((By.ID, 'has-account')))
	action_chains.double_click(login).perform()

	# Type in credentials at the command line to log in Spotiy with Facebook
	fb_login = WebDriverWait(driver, 10).until(
		EC.element_to_be_clickable((By.ID, 'fb-login-btn')))
	fb_login.click()
	driver.switch_to_window(driver.window_handles[1])
	print 'Logging in via Facebook ...'
	email_blank = driver.find_element_by_id('email')
	pass_blank  = driver.find_element_by_id('pass')

	input_email = config["facebook_email"]
	input_pass = config["facebook_password"]
	email_blank.send_keys(input_email)
	pass_blank.send_keys(input_pass)
	email_blank.submit()
	import ipdb
	ipdb.set_trace()

if __name__ == '__main__':
	url = raw_input('theurl')
	login(url)
