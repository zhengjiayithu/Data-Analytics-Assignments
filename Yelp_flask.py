from flask import Flask, session, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from datetime import date
import gmplot
from wtforms import SelectField, Form, StringField, validators, RadioField
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from bokeh.charts import BoxPlot, Bar, output_file, show, output_notebook
from pandas.tools.plotting import table
from wordcloud import WordCloud, STOPWORDS
import nltk
import numpy as np
import requests
from sklearn.cluster import KMeans
from sklearn import preprocessing
from sklearn.neighbors import NearestNeighbors
from nltk.corpus import wordnet as wn
from collections import Counter
from wtforms import BooleanField
from flask_wtf import Form
from math import sqrt
from scipy.misc import imread
global text
global label_food
from bokeh.embed import autoload_server
from bokeh.client import push_session, pull_session
from bokeh.resources import Resources
import subprocess
import atexit
import platform
import time



app = Flask(__name__)

app.secret_key = 'Yelp'

business = pd.read_csv("Montreal.csv",encoding = "latin1")
user = pd.read_csv("user.csv")
review = pd.read_csv("review.csv")

user["yelping_since"]=pd.to_datetime(user["yelping_since"])
review["review_len"] = [len(t) for t in review["text"]]
food = wn.synset('food.n.02')
foodlist=list(set([w for s in food.closure(lambda s:s.hyponyms()) for w in s.lemma_names()]))

class queryForm(FlaskForm):
	price = SelectField('Price', choices=[('<10', '<10'), ('10~30', '10~30'), ('30~60', '30~60'),('>60','>60')])
	parking = SelectField('Parking', choices=[('Not Necessary', 'Not Necessary'), ('Yes', 'Yes')])
	category = StringField('Categories', [validators.Length(min=1, max=40)])
	access = SelectField('Access', choices=[('Not Necessary', 'Not Necessary'), ('Yes', 'Yes')])
	deliver = SelectField('Deliver', choices=[('Not Necessary', 'Not Necessary'), ('Yes', 'Yes')])
	rsvp = SelectField('RSVP', choices=[('Not Necessary', 'Not Necessary'), ('Yes', 'Yes')])
	morning = SelectField('Morning', choices=[('Not Necessary', 'Not Necessary'), ('Yes', 'Yes')])
	noon = SelectField('Noon', choices=[('Not Necessary', 'Not Necessary'), ('Yes', 'Yes')])
	evening = SelectField('Evening', choices=[('Not Necessary', 'Not Necessary'), ('Yes', 'Yes')])
	night = SelectField('Night', choices=[('Not Necessary', 'Not Necessary'), ('Yes', 'Yes')])
	group = SelectField('Group', choices=[('Not Necessary', 'Not Necessary'), ('Yes', 'Yes')])

class recommendForm1(FlaskForm):
	funny = RadioField('Funny', choices=[('f1', 'Strongly disagree'), ('f2', 'Disagree'), ('f3', 'Neither agree nor disagree'), ('f4', 'Agree'), ('f5', 'Strongly agree')])
	cool = RadioField('Cool', choices=[('c1', 'Strongly disagree'), ('c2', 'Disagree'), ('c3', 'Neither agree nor disagree'), ('c4', 'Agree'), ('c5', 'Strongly agree')])
class recommendForm2(FlaskForm):
	category = StringField('Category', [validators.Length(min=1, max=40)])
	time = SelectField('Time', choices=[('t1', 'morning'), ('t2', 'noon'), ('t3', 'evening'), ('t4', 'late night'), ('t5', 'not sure')])
	purpose = SelectField('Purpose', choices=[('p1', 'dating'), ('p2', 'business'), ('p3', 'friends'), ('p4', 'families'), ('p5', 'single'), ('p6', 'tourist')])

class recommendForm3(FlaskForm):
	pic_choice = RadioField('Pic_choice', choices=[('p1', 'This is my favorite'), ('p2', 'This is my favorite'), ('p3', 'This is my favorite'), ('p4', 'This is my favorite'), ('p5', 'This is my favorite'), ('p6', 'This is my favorite'), ('p7', 'This is my favorite'), ('p8', 'This is my favorite')])

class recommendForm4(FlaskForm):
	reviewOrstar = SelectField('ReviewOrstar', choices=[('r1', 'star'), ('r2', 'review')])

class reviewForm(FlaskForm):
	keyword = StringField('Keyword', [validators.Length(min=1, max=40)])

class featureForm(Form):
	box1=BooleanField('check1')
	box2=BooleanField('check2')
	box3=BooleanField('check3')
	box4=BooleanField('check4')
	box5=BooleanField('check5')
	box6=BooleanField('check6')
	box7=BooleanField('check7')
	box8=BooleanField('check8')
	box9=BooleanField('check1')
	box10=BooleanField('check2')
	box11=BooleanField('check3')
	box12=BooleanField('check4')
	box13=BooleanField('check5')
	box14=BooleanField('check6')
	box15=BooleanField('check7')
	box16=BooleanField('check8')
	box17=BooleanField('check1')
	box18=BooleanField('check2')
	box19=BooleanField('check3')
	box20=BooleanField('check4')
	box_all=BooleanField('all')

def get_homepage_links():
	return [ {"href1": url_for('visualize'), "label1":"A Glance at Data"},
				{"href2": url_for('query'), "label2":"Find Your Restaurants"},
				{"href3": url_for('reviewpage'), "label3":"Taste Food"},
				{"href4": url_for('recommend0'), "label4":"Recommendation"},
				]

def get_links():
	return [{"href": url_for('business1'), "label":"Restaurants Heatmap"},
				{"href": url_for('business2'), "label":"Restaurants by Neighborhoods"},
				{"href": url_for('business3'), "label":"Restaurants by Stars"},
				{"href": url_for('business4'), "label":"Restaurants' Number of Reviews"},
				{"href": url_for('user1'), "label":"New Users Every Month"},
				{"href": url_for('user2'), "label":"Users' Average Stars"},
				{"href": url_for('user3'), "label":"Users' Number of Reviews"},
				{"href": url_for('reviews1'), "label":"Reviews Count Across Years"},
				{"href": url_for('reviews2'), "label":"Distribution of Stars"},
				{"href": url_for('reviews3'), "label":"Length of Review Texts"},
				{"href": url_for('join1'), "label":"Review Length and Review Count"},
				{"href": url_for('join2'), "label":"Review Length (Grouped by Stars of Businesses)"},
				{"href": url_for('overview'), "label":"Overview"}
				]

def get_review_links(keyword):
	return  {"href": url_for('review_feature'), "label":"   Taste your favorate food at '%s'    " % keyword}

def get_recommend1_links():
	return {"href": url_for('recommend1'), "label":"Let's GO!"}

@app.route("/")
def home():
	session["data_loaded"] = True
	return render_template('home.html', links=get_homepage_links())

@app.route("/visualize/", methods=['GET','POST'])
def visualize():
	return render_template('visualization.html', links=get_links())

@app.route("/visualize/overview/", methods=['GET','POST'])
def overview():
	connected = False
	while not connected:
		try:
			port = 5000+np.random.randint(0,100)
			subprocess.Popen(['bokeh', 'serve', '--show', 'visualize.py', '--port',str(port)]) 
			connected = True
		except:
			pass
	return redirect(url_for('visualize'))

@app.route("/visualize/business1/", methods=['GET','POST'])
def business1():
	latitudes = business["latitude"]
	longitudes = business["longitude"]
	gmap = gmplot.GoogleMapPlotter.from_geocode("Montreal",8)
	gmap.heatmap(latitudes, longitudes)
	gmap.draw('templates/Montreal.html')
	return render_template('businessoutput1.html', mapfile = 'Montreal.html')
	
@app.route("/visualize/business2/", methods=['GET','POST'])
def business2():
	plt.clf()
	neighbordata = business[["business_id","neighborhoods"]]
	neighbordata["neighborhoods"] = [i.strip('[]').strip("''") for i in neighbordata["neighborhoods"]]
	neighbordata["neighborhoods"] = [i.replace('\\xe9', str("\xe9")) for i in neighbordata["neighborhoods"]]
	neighbordata["neighborhoods"] = [i.replace("u'", "") for i in neighbordata["neighborhoods"]]
	neighbordata["neighborhoods"] = [i.replace("\\xe8", str("\xe8")) for i in neighbordata["neighborhoods"]]
	neighbordata["neighborhoods"] = [i.replace("\\xf4", str("\xf4")) for i in neighbordata["neighborhoods"]]
	neighbordata["neighborhoods"] = [i.replace("\\xe2", str("\xe2")) for i in neighbordata["neighborhoods"]]
	neighbordata["neighborhoods"] = [i.replace("\\u", "") for i in neighbordata["neighborhoods"]]
	plt.figure(figsize=(15,5))
	ax = sns.countplot(x="neighborhoods", data=neighbordata, palette="GnBu_d")
	rects = ax.patches
	labels = [l.get_text() for l in ax.xaxis.get_ticklabels()]
	for rect, label in zip(rects, labels):
	    height = rect.get_height()
	    ax.text(rect.get_x() + rect.get_width()/2, height+20, label, ha='center', va='bottom',rotation=90, fontsize=9)
	ax.xaxis.set_ticklabels([])
	fig = ax.get_figure()
	fig.savefig('static/business2.png')
	return render_template('businessoutput2.html')
	
@app.route("/visualize/business3/", methods=['GET','POST'])
def business3():
	plt.clf()
	ax = sns.countplot(x="stars", data=business, palette="Blues")
	fig = ax.get_figure()
	fig.savefig('static/business3.png')
	return render_template('businessoutput3.html')

@app.route("/visualize/business4/", methods=['GET','POST'])
def business4():
	plt.clf()
	plt.figure(figsize=(15,5))
	sns.plt.title("Restaurants' Number of Reviews",fontsize=20)
	ax1 = sns.distplot(business["review_count"])
	fig1 = ax1.get_figure()
	fig1.savefig('static/business4_1.png')

	plt.clf()
	plt.figure(figsize=(15,5))
	sns.plt.title("Restaurants' Number of Reviews (Grouped by Stars)",fontsize=20)
	ax2 = sns.stripplot(x="stars", y="review_count", data=business)
	fig2 = ax2.get_figure()
	fig2.savefig('static/business4_2.png')	
	return render_template('businessoutput4.html')

@app.route("/visualize/user1/", methods=['GET','POST'])
def user1():
	plt.clf()
	plt.figure(figsize=(15,5))
	plt.xlabel('Months')
	plt.ylabel('# of New Users')
	plt.xticks(rotation=45)
	ax = sns.countplot(x="yelping_since", data=user,palette="GnBu_d")
	ticks = ax.xaxis.get_ticklocs()
	xtl = [item.get_text()[:7] for item in ax.xaxis.get_ticklabels()]
	ax.xaxis.set_ticks(ticks[::5])
	ax.xaxis.set_ticklabels(xtl[::5])
	fig = ax.get_figure()
	fig.savefig('static/user1_1.png')

	plt.clf()
	plt.figure(figsize=(15,5))
	newuser = user.groupby('yelping_since')
	matplotlib.style.use('ggplot')
	plt.xlabel('Months')
	plt.ylabel('# of New Users')
	plt.xticks(rotation=45)
	ax2 = newuser.size().plot()
	fig2 = ax2.get_figure()
	fig2.savefig('static/user1_2.png')	

	return render_template('useroutput1.html')

@app.route("/visualize/user2/", methods=['GET','POST'])
def user2():
	plt.clf()
	plt.xlim(xmin=0)
	plt.xlim(xmax=5)
	ax = sns.distplot(user["average_stars"])
	fig = ax.get_figure()
	fig.savefig('static/user2.png')	
	return render_template('useroutput2.html')

@app.route("/visualize/user3/", methods=['GET','POST'])
def user3():
	plt.clf()
	ax = sns.distplot(user["review_count"])
	fig = ax.get_figure()
	fig.savefig('static/user3.png')	
	return render_template('useroutput3.html')

@app.route("/visualize/reviews1/", methods=['GET','POST'])
def reviews1():
	plt.clf()
	newreview = review[["business_id", "date"]]
	newreview["date"]=pd.to_datetime(newreview["date"])
	newreview["newdate"] = 100*newreview["date"].dt.year + newreview["date"].dt.month
	plt.figure(figsize=(15,5))
	ax = sns.countplot(x="newdate", data=newreview, palette="GnBu_d")
	ticks = ax.xaxis.get_ticklocs()
	xtl = [item.get_text()[:7] for item in ax.xaxis.get_ticklabels()]
	ax.xaxis.set_ticks(ticks[::5])
	ax.xaxis.set_ticklabels(xtl[::5])
	plt.xlabel('Date')
	plt.ylabel('# of Reviews')
	plt.xticks(rotation=45)
	fig = ax.get_figure()
	fig.savefig('static/reviews1.png')
	return render_template('reviewsoutput1.html')

@app.route("/visualize/reviews2/", methods=['GET','POST'])
def reviews2():
	plt.clf()
	ax = sns.countplot(x="stars", data=review, palette=sns.cubehelix_palette(5))
	fig = ax.get_figure()
	fig.savefig('static/reviews2.png')	
	return render_template('reviewsoutput2.html')

@app.route("/visualize/reviews3/", methods=['GET','POST'])
def reviews3():
	plt.clf()
	plt.figure(figsize=(15,5))
	plt.xlim(xmin=0)
	plt.xlim(xmax=5000)
	sns.plt.title("Length of Review Texts (Histogram)",fontsize=20)
	ax1 = sns.distplot(review["review_len"])
	fig1 = ax1.get_figure()
	fig1.savefig('static/reviews3_1.png')
	
	plt.clf()
	plt.figure(figsize=(15,5))
	matplotlib.style.use('seaborn-pastel')
	sns.plt.title("Length of Review Texts (Boxplot)",fontsize=20)
	ax2 = sns.boxplot(review['review_len'])
	fig2 = ax2.get_figure()
	fig2.savefig('static/reviews3_2.png')

	plt.clf()
	plt.figure(figsize=(15,5))
	plt.xticks(rotation=90)
	sns.plt.title("Length of Reviews v. Votes Useful",fontsize=20)
	ax3 = sns.stripplot(y="votes.useful", x="review_len", data=review, jitter=True)
	ticks = ax3.xaxis.get_ticklocs()
	xtl = [item.get_text() for item in ax3.xaxis.get_ticklabels()]
	ax3.xaxis.set_ticks(ticks[::50])
	ax3.xaxis.set_ticklabels(xtl[::50])
	fig3 = ax3.get_figure()
	fig3.savefig('static/reviews3_3.png')

	return render_template('reviewsoutput3.html')

@app.route("/visualize/join1/", methods=['GET','POST'])
def join1():
	plt.clf()
	businessreview = pd.merge(business,review, on="business_id", how="inner")
	sub = businessreview[["business_id","review_len"]]
	avg = sub.groupby('business_id').mean()
	avg = avg.reset_index()
	m = pd.merge(business, avg, on="business_id", how="inner")
	g = sns.jointplot(x="review_count", y="review_len", data=m)
	g.savefig('static/join1.png')	
	return render_template('joinoutput1.html')	

@app.route("/visualize/join2/", methods=['GET','POST'])
def join2():
	plt.clf()
	businessreview = pd.merge(business,review, on="business_id", how="inner")
	sub = businessreview[["business_id","review_len"]]
	avg = sub.groupby('business_id').mean()
	avg = avg.reset_index()
	m = pd.merge(business, avg, on="business_id", how="inner")
	plt.figure(figsize=(15,5))	
	ax = sns.boxplot(m['stars'],m['review_len'])
	fig = ax.get_figure()
	fig.savefig('static/join2.png')	
	return render_template('joinoutput2.html')	

@app.route('/query/',methods=['GET','POST'])
def query():
	form = queryForm()
	if form.validate_on_submit():
		category = request.form.get('category')
		price = request.form.get('price')
		parking = request.form.get('parking')
		access = request.form.get('access')
		deliver = request.form.get('deliver')
		rsvp = request.form.get('rsvp')
		morning = request.form.get('morning')
		noon = request.form.get('noon')
		evening = request.form.get('evening')
		night = request.form.get('night')
		group = request.form.get('group')

		x1 = business[business['categories'].str.contains(category, case = False)]
	
		if price == "<10":
			code = 1
		if price == "10~30":
			code = 2
		if price == "30~60":
			code = 3
		if price == ">60":
			code = 4
		x21 = x1[x1['attributes.Price Range'] == code]
		x22 = x1[x1['attributes.Price Range'].isnull()]
		x2 = pd.concat([x21, x22])
	
		if parking == "Yes":
			x3 = x2[x2['attributes.Parking.street'] == True]
		if parking == "Not Necessary":
			x3 = x2

		if access == "Yes":
			x4 = x3[x3['attributes.Wheelchair Accessible'] == True]
		if access == "Not Necessary":
			x4 = x3

		if deliver == "Yes":
			x5 = x4[x4['attributes.Delivery'] == True]
		if deliver == "Not Necessary":
			x5 = x4

		if rsvp == "Yes":
			x6 = x5[x5['attributes.Takes Reservations'] == True]
		if rsvp == "Not Necessary":
			x6 = x5

		if morning == "Yes":
			x7 = x6[x6['attributes.Good For.breakfast'] == True]
		if morning == "Not Necessary":
			x7 = x6

		if noon == "Yes":
			x8 = x7[x7['attributes.Good For.lunch'] == True]
		if noon == "Not Necessary":
			x8 = x7

		if evening == "Yes":
			x9 = x8[x8['attributes.Good For.dinner'] == True]
		if evening == "Not Necessary":
			x9 = x8

		if night == "Yes":
			x10 = x9[x9['attributes.Good For.latenight'] == True]
		if night == "Not Necessary":
			x10 = x9

		if group == "Yes":
			x11 = x10[x10['attributes.Good For Groups'] == True]
		if group == "Not Necessary":
			x11 = x10
		
		restaurant = x11.sort_values('stars', ascending = False)

		result = restaurant[['name', 'full_address',  'stars','review_count']].reset_index().drop('index', 1)

		result["name"] = [i.replace('?', '') for i in result["name"]]

		result.to_csv("query.csv")

		lat = list(restaurant["latitude"])
		lnt = list(restaurant["longitude"])
		gmap = gmplot.GoogleMapPlotter(np.mean(lat),np.mean(lnt),12)
		#gmap.scatter(lat, lnt, 'k', marker=True)
		gmap.scatter(lat, lnt, '#3B0B39', size=200, marker=False)
		gmap.draw("templates/searchmap.html")

		connected = False
		#port = 5000+np.random.randint(0,100)

		while not connected:
			try:
				port = 5000+np.random.randint(0,100)
				# if 'window' in platform.system().lower():
				# 	bokeh_process = subprocess.Popen(
				# 		'bokeh serve --show q.py --port %d'%(port), shell=False, stdout=subprocess.PIPE)
				# 	connected = True
				# else:
				subprocess.Popen(['bokeh', 'serve', '--show', 'q.py', '--port',str(port)]) 
				connected = True
			except:
				pass

		time.sleep(6)	

		return render_template('queryoutput.html', mapfile='searchmap.html')
		#return render_template('queryoutput.html', )
		
	return render_template('queryparams.html', form=form)


@app.route('/review/',methods=['GET','POST'])
def reviewpage():
	
	# review-block-1: search_restaurant_function
	def search_restaurant(keyword):
		N=len(business)
		search_result_name=list()
		for i in range(0,N):
			if keyword.lower() in business.loc[i]['name'].lower():
				search_result_name.append(business.loc[i]['name']) 
		return business[business['name'].isin(list(search_result_name))]

	# review-block-2: get_review_fuction 
	def get_review(keyword):
		result_frame=search_restaurant(keyword)
		text=str()
		for i in range(len(result_frame)):
			myid=result_frame.iloc[i,16]
			text=text+str(list(review[review['business_id']==result_frame.iloc[i,16]]['text']))
		return text

	# review-block-3: get_cloud_fuction 
	def get_cloud(text,name):
		if len(text)<20:
			return None
		delete_words=[name.lower(),'food','restaurant',' one ','place',' really ',\
		' go ',' year ',' come ',' the ',' a ','\n',' is ',' are ',' of ',' le ',' de ',' la ',' place '\
		' et ','side','plate','cut','green','heart','tongue']
		newlist=list()
		for word in delete_words:
			text=text.replace(word,' ')
		for word in text.split():
			if word in foodlist:
				newlist.append(word)
		newtext=' '.join(newlist)
		wordcloud = WordCloud(stopwords=STOPWORDS,background_color='white',mask=imread('static/mask2.jpeg'),width=1200,height=1000).generate(newtext)
		wordcloud.to_file("static/review_cloud_1.png")
		return newlist

	# review-block-4: main 
	form = reviewForm()
	if form.validate_on_submit():
		keyword = request.form.get('keyword')
		myres=search_restaurant(keyword) #McDonald's, Marven's Restaurant
		if len(myres)>0:
			myres=myres.sort_values(by=['stars','name'],ascending=False)
			plt.clf()
			ax = sns.countplot(x="stars", data=myres, palette="GnBu_d")
			fig=ax.get_figure()
			sns.set(font_scale=1.5)
			ave_star=round(np.mean(list(myres['stars'])),2)
			std_star=round(np.std(list(myres['stars'])),2)
			result=myres.loc[:,['name','full_address','stars']].head(45)

			lat = list(myres["latitude"])
			lnt = list(myres["longitude"])
			gmap = gmplot.GoogleMapPlotter(np.mean(lat),np.mean(lnt),12)
			gmap.scatter(lat, lnt, '#3B0B39', size=200, marker=False)
			gmap.draw("templates/reviewmap.html")
			global text
			text=get_review(keyword).lower()
			newlist=get_cloud(text,keyword)


			cnt = Counter()
			plt.figure(figsize=(15,5))
			for word in newlist:
				cnt[word]+=1
			frequency_list=pd.DataFrame(list(cnt.items())).sort_values(1,ascending=False)
			menu=list(pd.DataFrame(list(cnt.items()))[0].unique())
			col=5
			row=len(menu)//col
			menu=np.array(menu[0:col*row])
			menu_list=pd.DataFrame(menu.reshape(row,col))
			if len(frequency_list)>20:
				frequency_list=frequency_list[0:20]
			global label_food
			num_food=list(frequency_list[1])
			label_food=list(frequency_list[0])
			fig=plt.bar(range(len(num_food)),num_food)
			plt.xticks(range(len(num_food)), label_food)
			plt.xticks(rotation=30,fontsize=10)
			plt.savefig('static/review_distribution.png')



			return render_template('reviewoutput.html', data=menu_list.to_html(),keyword=keyword,ave_rate=ave_star,std_rate=std_star,
				link=get_review_links(keyword), mapfile = 'reviewmap.html')

		else:
			return 'We cannot find restaurant:%s' %keyword

	return render_template('reviewparams.html', form=form)



@app.route("/review/feature/", methods=['GET','POST'])
def review_feature():

	# feature-block-1 concordance_function
	def concordance(text,word,width):
		locs = [loc for loc, x in enumerate(text) if x.lower() == word.lower()]
		fragments = list()
		for loc in locs:
			start = max(0,loc-width)
			end = min(len(text),loc+width)
			fragments.append(' '.join(text[start:end]))
		return fragments

	# feature-block-2 get_concordance_sentiment_function
	def get_concordance_sentiment(text,word,width):
		if len(str(nearby_content))<20:
			return 0
		sentences = concordance(text,word,width)
		pos=0
		neg=0
		for sent in sentences:
			for word in sent.split():
				if word in positive_words:
					pos+=1
				if word in negative_words:
					neg+=1
		if not pos and not neg:
			return 1
		if pos and not neg:
			return 10
		else:
			return pos/neg


	# review-block-3: get_words_function
	def get_words(url):
		words = requests.get(url).content.decode('latin-1')
		word_list = words.split('\n')
		index = 0
		while index < len(word_list):
			word = word_list[index]
			if ';' in word or not word:
				word_list.pop(index)
			else:
				index+=1
		return word_list
	p_url = 'http://ptrckprry.com/course/ssd/data/positive-words.txt'
	n_url = 'http://ptrckprry.com/course/ssd/data/negative-words.txt'
	positive_words = get_words(p_url)
	negative_words = get_words(n_url)

	# feature-block-4: main
	global text
	global label_food
	form = featureForm()

	if form.validate_on_submit():

		value1=form.box1.data
		value2=form.box2.data
		value3=form.box3.data
		value4=form.box4.data
		value5=form.box5.data
		value6=form.box6.data
		value7=form.box7.data
		value8=form.box8.data
		value9=form.box9.data
		value10=form.box10.data
		value11=form.box11.data
		value12=form.box12.data
		value13=form.box13.data
		value14=form.box14.data
		value15=form.box15.data
		value16=form.box16.data
		value17=form.box17.data
		value18=form.box18.data
		value19=form.box19.data
		value20=form.box20.data
		value_all=form.box_all.data
		logic_array=[value1,value2,value3,value4,value5,value6,value7,value8,\
		value9,value10,value11,value12,value13,value14,value15,value16,\
		value17,value18,value19,value20]
		if value_all==True:
			logic_array=[True for _ in range(0,20)]
		mylabel=pd.DataFrame(label_food)
		feature_list=list(mylabel[logic_array][0])


		global rates
		global rates_name_str
		global nearby
		rates=list()
		rates_name_str='['
		text_content=nltk.Text(text.split())
		matplotlib.style.use('seaborn-colorblind')

		if len(feature_list)<4:
			COL_NUM=len(feature_list)
			ROW_NUM=1
		else:
			COL_NUM=4
			if len(feature_list)%COL_NUM!=0:
				ROW_NUM=len(feature_list)//COL_NUM+1
			else:
				ROW_NUM=len(feature_list)//COL_NUM

		fig, axes = plt.subplots(ROW_NUM, COL_NUM, figsize=(12,12))

		for i in range(0,COL_NUM*ROW_NUM):
			if i < len(feature_list):
				exec('global feature'+str(i+1)+'\n'+'feature'+str(i+1)+'=feature_list['+str(i)+']')
				exec('global nearby\nnearby=str(concordance(text_content,feature'+str(i+1)+',10))')
				exec('global nearby_content\nnearby_content=nltk.Text(nearby.split())')
				exec('global rates\nrates.append(get_concordance_sentiment(nearby_content,feature'+str(i+1)+',10))')
				rates_name_str+='feature'+str(i+1)+','

			if len(feature_list)>1:
				if len(feature_list)>4:
					ax = axes[i//COL_NUM, i%COL_NUM]
				else:
					ax = axes[i%COL_NUM]
				if i<len(feature_list):
					ax.set_title(eval('feature'+str(i+1)))
					delete_words=[eval('feature'+str(i+1)+'.lower()'),'food','restaurant',' one ','place',' really ',\
					' go ',' year ',' come ',' the ',' a ','\n',' is ',' are ',' of ',' le ',' de ',' la ',' place '\
					' et ','side','plate','cut']
					for word in delete_words:
						nearby=nearby.replace(word,' ')
					wordcloud = WordCloud(stopwords=STOPWORDS,background_color='white',mask=imread('static/mask6.png'),width=1200,height=1000,max_words=20,scale=0.5).generate(nearby)
					ax.imshow(wordcloud)
					ax.axis('off')
				else:
					ax.axis('off')
			else:
				delete_words=[eval('feature'+str(i+1)+'.lower()'),'food','restaurant',' one ','place',' really ',\
				' go ',' year ',' come ',' the ',' a ','\n',' is ',' are ',' of ',' le ',' de ',' la ',' place '\
				' et ','side','plate','cut']
				wordcloud = WordCloud(stopwords=STOPWORDS,background_color='white',mask=imread('static/mask6.png'),width=1200,height=1000,max_words=10,scale=0.5).generate(nearby)
				wordcloud.to_file('static/many_wordcloud.png')
		if len(feature_list)>1:
			fig.savefig('static/many_wordcloud.png')
		rates_name_str+=']'


		ax=pd.DataFrame({'rating':rates}).plot(kind='bar',fontsize=15,figsize=(15,5))
		ax.set_xticklabels(eval(rates_name_str),fontsize=11,rotation=20)
		fig=ax.get_figure()
		fig.suptitle('Scores of Selected Food', fontsize=35)
		fig.savefig('static/feature_rating.png')

		return render_template('featureoutput.html')
	return render_template('featureparams.html', form=form, label_food=label_food)



@app.route("/recommend0/", methods=['GET','POST'])
def recommend0():
	return render_template('recommend0.html', link=get_recommend1_links())

@app.route('/recommend0/recommend1/',methods=['GET','POST'])
def recommend1():
	form = recommendForm1()

	user["yelping_since"]=pd.to_datetime(user["yelping_since"])
	review["review_len"] = [len(t) for t in review["text"]]

	b_r=pd.merge(business, review, on='business_id',how='inner')
	b_r_u=pd.merge(b_r, user, on='user_id',how='inner')
	b_r_u1 = b_r_u[b_r_u['review_count_x'] >= 10]
	user0 = b_r_u1[['user_id', 'business_id', 'name_x', 'stars_x', 'review_count_x', 'attributes.Ambience.touristy', 'attributes.Ambience.intimate', \
                'attributes.Ambience.casual', 'attributes.Ambience.romantic', 'attributes.Ambience.upscale', 'categories', \
                'attributes.Good For.breakfast', 'attributes.Good For.lunch', 'attributes.Good For.dinner', 'attributes.Good For.latenight', \
                'attributes.Attire', 'attributes.Price Range', 'stars_y', 'latitude', 'longitude', 'votes.cool_y', 'votes.funny_y', 'votes.useful_y']]
	user1 = user0[user0['stars_y'] == 5]
	user2 = user1[user1['votes.cool_y'] >= 1]
	user3 = user2[user2['votes.funny_y'] >= 1]
	user4 = user3[user3['votes.useful_y'] >= 10]
	user4.reset_index().drop('index', 1)
	user4['coolratio'] = user4['votes.cool_y']/(user4['votes.cool_y'] + user4['votes.funny_y'])
	user5 = user4[['coolratio']]
	kmeans = KMeans(n_clusters=5, random_state=0).fit(user5)
	user4['labels'] = kmeans.labels_

	cluster0 = user4[user4['labels'] == 0][['user_id', 'business_id', 'name_x', 'stars_x', 'review_count_x', 'attributes.Ambience.touristy', 'attributes.Ambience.intimate', \
                'attributes.Ambience.casual', 'attributes.Ambience.romantic', 'attributes.Ambience.upscale', 'categories', \
                'attributes.Good For.breakfast', 'attributes.Good For.lunch', 'attributes.Good For.dinner', 'attributes.Good For.latenight', \
                'attributes.Attire', 'attributes.Price Range', 'latitude', 'longitude']]
	cluster0 = cluster0.drop_duplicates()
	cluster0 = cluster0

	cluster1 = user4[user4['labels'] == 1][['user_id', 'business_id', 'name_x', 'stars_x', 'review_count_x', 'attributes.Ambience.touristy', 'attributes.Ambience.intimate', \
                'attributes.Ambience.casual', 'attributes.Ambience.romantic', 'attributes.Ambience.upscale', 'categories', \
                'attributes.Good For.breakfast', 'attributes.Good For.lunch', 'attributes.Good For.dinner', 'attributes.Good For.latenight', \
                'attributes.Attire', 'attributes.Price Range', 'latitude', 'longitude']]
	cluster1 = cluster1.drop_duplicates()

	cluster2 = user4[user4['labels'] == 2][['user_id', 'business_id', 'name_x', 'stars_x', 'review_count_x', 'attributes.Ambience.touristy', 'attributes.Ambience.intimate', \
                'attributes.Ambience.casual', 'attributes.Ambience.romantic', 'attributes.Ambience.upscale', 'categories', \
                'attributes.Good For.breakfast', 'attributes.Good For.lunch', 'attributes.Good For.dinner', 'attributes.Good For.latenight', \
                'attributes.Attire', 'attributes.Price Range', 'latitude', 'longitude']]
	cluster2 = cluster2.drop_duplicates()

	cluster3 = user4[user4['labels'] == 3][['user_id', 'business_id', 'name_x', 'stars_x', 'review_count_x', 'attributes.Ambience.touristy', 'attributes.Ambience.intimate', \
                'attributes.Ambience.casual', 'attributes.Ambience.romantic', 'attributes.Ambience.upscale', 'categories', \
                'attributes.Good For.breakfast', 'attributes.Good For.lunch', 'attributes.Good For.dinner', 'attributes.Good For.latenight', \
                'attributes.Attire', 'attributes.Price Range', 'latitude', 'longitude']]
	cluster3 = cluster3.drop_duplicates()

	cluster4 = user4[user4['labels'] == 4][['user_id', 'business_id', 'name_x', 'stars_x', 'review_count_x', 'attributes.Ambience.touristy', 'attributes.Ambience.intimate', \
                'attributes.Ambience.casual', 'attributes.Ambience.romantic', 'attributes.Ambience.upscale', 'categories', \
                'attributes.Good For.breakfast', 'attributes.Good For.lunch', 'attributes.Good For.dinner', 'attributes.Good For.latenight', \
                'attributes.Attire', 'attributes.Price Range', 'latitude', 'longitude']]
	cluster4 = cluster4.drop_duplicates()

	def recommend1_1(cool,funny):

		if funny == 'f1':
			funnynum = 1
		if funny == 'f2':
			funnynum = 2
		if funny == 'f3':
			funnynum = 3
		if funny == 'f4':
			funnynum = 4
		if funny == 'f5':
			funnynum = 5

		if cool == 'c1':
			coolnum = 1
		if cool == 'c2':
			coolnum = 2
		if cool == 'c3':
			coolnum = 3
		if cool == 'c4':
			coolnum = 4
		if cool == 'c5':
			coolnum = 5

		ratio = coolnum/(funnynum+coolnum)
		mycluster = kmeans.predict(ratio)[0]
		if mycluster == 0:
			result = cluster0
		if mycluster == 1:
			result = cluster1
		if mycluster == 2:
			result = cluster2
		if mycluster == 3:
			result = cluster3
		if mycluster == 4:
			result = cluster4
		
		return result


	if form.validate_on_submit():
		funny = request.form.get('funny')
		cool = request.form.get('cool')

		global recommend_1
		recommend_1 = recommend1_1(cool, funny)
		
		return redirect(url_for('recommend2'))

	return render_template('recommend1.html', form=form)

@app.route('/recommend0/recommend1/recommend2/',methods=['GET','POST'])
def recommend2():

	form = recommendForm2()

	global recommend_1

	def recommend2_1(category, time, purpose):
		business = recommend_1[recommend_1['categories'].str.contains(category, case = False)]

		if time == 't1':
			business1 = business[business['attributes.Good For.breakfast'] == True]
		if time == 't2':
			business1 = business[business['attributes.Good For.lunch'] == True]
		if time == 't3':
			business1 = business[business['attributes.Good For.dinner'] == True]
		if time == 't4':
			business1 = business[business['attributes.Good For.latenight'] == True]
		if time == 't5':
			business1 = business

		intimate = business1[business1['attributes.Ambience.intimate'] == True]
		touristy = business1[business1['attributes.Ambience.touristy'] == True]
		casual = business1[business1['attributes.Ambience.casual'] == True]
		romantic = business1[business1['attributes.Ambience.romantic'] == True]
		upscale = business1[business1['attributes.Ambience.upscale'] == True]

		if purpose == "p1":
			business2 = pd.concat([intimate, romantic])
		if purpose == "p2":
			business2 = pd.concat([intimate, upscale])
		if purpose == "p3":
			business2 = pd.concat([intimate, casual])
		if purpose == "p4":
			business2 = pd.concat([intimate, casual])
		if purpose == "p5":
			business2 = pd.concat([intimate, casual, upscale])
		if purpose == "p6":
			business2 = pd.concat([casual, touristy])

		return business2.drop('user_id', 1).drop_duplicates()
	
	if form.validate_on_submit():
		category = request.form.get('category')
		time = request.form.get('time')
		purpose = request.form.get('purpose')
		global recommend_2
		recommend_2 = recommend2_1(category, time, purpose)
		recommend_2 = recommend_2.reset_index().drop('index', 1)
		if len(recommend_2) == 0:
			return render_template('recommend2r-1.html', form=form)
		else:
			return redirect(url_for('recommend3'))

	return render_template('recommend2.html', form=form)

@app.route('/recommend0/recommend1/recommend2/recommend3/',methods=['GET','POST'])
def recommend3():
	
	form = recommendForm3()

	restaurant_pic1 = ['cheap1.jpg', 'business2.jpg', 'romantic1.jpg','cheap2.jpg']
	restaurant_pic2 = ['tourist1.jpg', 'tourist2.jpg', 'romantic2.jpg', 'business1.jpg']

	global recommend_2

	myframe = recommend_2[['attributes.Ambience.touristy', 'attributes.Ambience.intimate', 'attributes.Ambience.casual', \
						'attributes.Ambience.romantic', 'attributes.Ambience.upscale', 'attributes.Price Range', 'attributes.Attire']]
	myframe[['attributes.Ambience.touristy', 'attributes.Ambience.intimate', 'attributes.Ambience.casual', 'attributes.Ambience.romantic', \
         	'attributes.Ambience.upscale']] = myframe[['attributes.Ambience.touristy', 'attributes.Ambience.intimate', 'attributes.Ambience.casual', \
            'attributes.Ambience.romantic', 'attributes.Ambience.upscale']].astype(int)
	myframe = myframe.replace(to_replace=['casual', 'formal', 'dressy'], value=[0, 1, 0.8])
	#myframe1 = np.array(myframe)
	myframe1 = preprocessing.scale(myframe)
	#myframe
	
	fea_matrix = np.array([[0.1,0.3,0.8,0.6,0,1,0],[0.1,0.5,0.1,0.4,0.9,4,0.8],[0.1,0.6,0.5,0.9,0.7,4,0.7],[0.6,0.1,1,0,0,1,0],[0.8,0.1,0.9,0.1,0.2,1,0],[0.9,0.5,0.7,0.2,0.4,3,0.1],[0.8,0.8,0.5,1,0.8,4,0.6],[0.1,1,0,0.3,1,4,1]])
	fea_matrix = preprocessing.scale(fea_matrix)

	def recommend3_1(pic_choice):
		if pic_choice == "p1":
			X = np.concatenate((myframe1, [fea_matrix[0]]))
			nbrs = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(X)
		if pic_choice == "p2":
			X = np.concatenate((myframe1, [fea_matrix[1]]))
			nbrs = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(X)
		if pic_choice == "p3":
			X = np.concatenate((myframe1, [fea_matrix[2]]))
			nbrs = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(X)
		if pic_choice == "p4":
			X = np.concatenate((myframe1, [fea_matrix[3]]))
			nbrs = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(X)
		if pic_choice == "p5":
			X = np.concatenate((myframe1, [fea_matrix[4]]))
			nbrs = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(X)
		if pic_choice == "p6":
			X = np.concatenate((myframe1, [fea_matrix[5]]))
			nbrs = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(X)
		if pic_choice == "p7":
			X = np.concatenate((myframe1, [fea_matrix[6]]))
			nbrs = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(X)
		if pic_choice == "p8":
			X = np.concatenate((myframe1, [fea_matrix[7]]))
			nbrs = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(X)
		distances, indices = nbrs.kneighbors(X)
		myindex = np.delete(indices[-1], 0)
		recommend_3 = recommend_2[['business_id', 'name_x', 'stars_x', 'review_count_x', 'latitude', 'longitude']].ix[myindex]
		return recommend_3

	if form.validate_on_submit():
		pic_choice = request.form.get('pic_choice')
		global recommend_3
		if len(recommend_2) <= 5:
			recommend_3 = recommend_2[['business_id', 'name_x', 'stars_x', 'review_count_x', 'latitude', 'longitude']]
		else:
			recommend_3 = recommend3_1(pic_choice)

		result = recommend_3.sort_values('review_count_x', ascending = False).head(1)

		lat = float(result["latitude"])
		lnt = float(result["longitude"])

		#name=str(result["name_x"])[0]
		name = list(result["name_x"])[0]

		from yelp.client import Client
		from yelp.oauth1_authenticator import Oauth1Authenticator

		auth = Oauth1Authenticator(
    		consumer_key='dr8aE-pryV4EwOTn1AOrgQ',
    		consumer_secret='Vppa6lir0US1wr76S-qkilN-Bgk',
    		token='oFoNB1dOAUd5gt1lKqYhTM3NYp5VDXX1',
    		token_secret='GQEAGbEaNpk50C6_92MyzomHF5o'
			)

		client = Client(auth)

		params = {"sort": 0, 'radius_filter': 100}

		this_count = 0


		response = client.search_by_coordinates(lat, lnt, **params)
		business_list = response.businesses
		for this_bus in business_list:
			if this_bus.name == name:
				myurl = this_bus.url
				this_count = 1
				break

		#this_count = 0			
		 
		#myurl = response.businesses[0].url

		if this_count == 1:
			return redirect(myurl)
		else:
			lat = list(result["latitude"])
			lnt = list(result["longitude"])
			gmap = gmplot.GoogleMapPlotter(np.mean(lat),np.mean(lnt),12)
			gmap.scatter(lat, lnt, '#3B0B39', size=200, marker=False)
			gmap.draw("templates/reviewmap.html")

			return render_template('recommendoutput.html', data=result.to_html(), mapfile = 'reviewmap.html', name=list(result["name_x"])[0], 
				stars=list(result["stars_x"])[0], reviewcount=int(list(result["review_count_x"])[0])) 
	return render_template('recommend3.html',  form=form, pics=list(form.pic_choice), labels1=restaurant_pic1, labels2=restaurant_pic2)

if __name__ == '__main__':
	app.run(debug = True)