from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import datetime
import json, time, os, re
import pandas as pd
import csv

def scrape():
	user = 'attndotcom'
	browser = webdriver.Chrome() #opens chrome browser

	# Load JSON
	with open('InstAnalytics.json') as iaFile:
	    iaDictionary = json.load(iaFile)

	with open('InstAnalytics_backup.json', 'w') as iaFile:
	    json.dump(iaDictionary, iaFile, indent=4)

	 browser.get('https://instagram.com/' + str(user)) #opens the webpage on chrome

	 soup = BeautifulSoup(browser.page_source, 'html.parser')

	 #Gets the metrics from the header of Posts, Followers, and Following
	postsT = soup.html.body.span.section.main.article.header.findAll('div', recursive=False)[1].ul.findAll('li', recursive=False)[0].span.findAll('span', recursive=False)[0].getText()
	followersT = soup.html.body.span.section.main.article.header.findAll('div', recursive=False)[1].ul.findAll('li', recursive=False)[1].span.findAll('span', recursive=False)[0].getText()
	followingT = soup.html.body.span.section.main.article.header.findAll('div', recursive=False)[1].ul.findAll('li', recursive=False)[2].span.findAll('span', recursive=False)[0].getText()

	posts     = int(re.sub('[^0-9]', '', postsT))
	followers = int(re.sub('[^0-9]', '', followersT))
	following = int(re.sub('[^0-9]', '', followingT))
	# Convert k to thousands and m to millions
	if 'k' in postsT: 	  posts     = posts     * 1000
	if 'k' in followersT: followers = followers * 1000
	if 'k' in followingT: following = following * 1000
	if 'm' in postsT: 	  posts     = posts     * 1000000
	if 'm' in followersT: followers = followers * 1000000
	if 'm' in followingT: following = following * 1000000

	if posts > 12:
	# Click the 'Load more' button
		browser.find_element_by_xpath('/html/body/span/section/main/article/div/div[3]/a').click()

	if posts > 24:
	# Load more by scrolling to the bottom of the page
		for i in range (0, (posts-24)//12):
			browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
			time.sleep(0.1)
			browser.execute_script('window.scrollTo(0, 0)')
			time.sleep(0.5)
	browser.execute_script('window.scrollTo(0, 0)')

	soup = BeautifulSoup(browser.page_source, 'html.parser')

	links = []
	for link in soup.html.body.span.section.main.article.findAll('a'):
		if link.get('href')[:3] == '/p/': links.append(link.get('href'))

	photosDic = []
	pLikesT = 1
	pCounter = 1


	photosDic = []
	pLikesT = 0
	pCounter = 0
	for link in links:
	# Photo Id
		pId = link.split("/")[2]
		# Hover over a photo reveals Likes & Comments
		time.sleep(0.08)
		photo = browser.find_element_by_xpath('//a[contains(@href, "' + pId + '")]')
		time.sleep(0.08)
		ActionChains(browser).move_to_element(photo).perform()
		# Soup
		soup = BeautifulSoup(browser.page_source, 'html.parser')
		# Likes
		pLikes    = int(re.sub('[^0-9]', '', soup.html.body.span.section.main.article.findAll('div', recursive=False)[0].findAll('div', recursive=False)[0].findAll('a')[pCounter].find('ul').findAll('li', recursive=False)[0].findAll('span', recursive=False)[0].getText()))

		# Comments
		pComments = int(re.sub('[^0-9]', '', soup.html.body.span.section.main.article.findAll('div', recursive=False)[0].findAll('div', recursive=False)[0].findAll('a')[pCounter].find('ul').findAll('li', recursive=False)[1].findAll('span', recursive=False)[0].getText()))
		# Photo dictionary
		photoDic = {
			'pId': pId,
			'pLikes': pLikes,
			'pComments': pComments
		}
		photosDic.append(photoDic)
		# Total likes
		pLikesT += pLikes
		# Simple counter
		pCounter += 1

	iaDictionary.append(userDic)
	with open('InstAnalytics.json', 'w') as iaFile:
		json.dump(iaDictionary, iaFile, indent=4)
	pId = link.split("/")[2]

	pandas = pd.DataFrame(photosDic)
	pandapanda = []
	pandapandapandapanda = []
	for i in range(0, len(pandas)):
	    pandapanda = 'https://www.instagram.com/p/' + str(pandas['pId'][i]) + '/'
	    pandapandapandapanda.append(pandapanda)

	yes = pd.DataFrame(pandapandapandapanda)
	yes1 = pd.concat([pandas, yes], axis=1)
	yes1.to_csv("scraped.csv")
