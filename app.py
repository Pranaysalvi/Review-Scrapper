from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
import csv
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

app = Flask(__name__)

@app.route('/',methods=['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')

@app.route('/review',methods=['POST','GET'])
@cross_origin()
def review_scrapper():
    if request.method == 'POST':
        try:
            search_url = request.form['content'].replace(" ","")
            amazon_url = "https://www.amazon.in/s?k=" + search_url
            uClient = uReq(amazon_url)
            pagedata = uClient.read()
            amazon_html = bs(pagedata,"html.parser")
            html_boxs = amazon_html.find_all("div",{"class":"s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16"})
            box = html_boxs[0]
            product_link = "https://www.amazon.in/" + box.div.div.div.div.div.h2.a["href"]
            product_req = uReq(product_link)
            product_data = product_req.read()
            product_req_data = bs(product_data,"html.parser")
            review_box = product_req_data.find_all("div",{"class":"a-section review aok-relative"})
            filename = search_url + ".csv"

            reviews = []
            for review in review_box:
                try:
                    name = review.div.div.div.a.find_all("div",{"class":"a-profile-content"})[0].text

                except:
                    name = "no name"

                try:
                    ratting = review.div.div.find_all("i",{"data-hook":"review-star-rating"})[0].text

                except:
                    ratting = "no ratting"

                try:
                    heading = review.div.div.find_all("a",{"data-hook":"review-title"})[0].text

                except:
                    heading = "no heading"

                try:
                    comments = review.div.div.find_all("div",{"class":"a-expander-content reviewText review-text-content a-expander-partial-collapse-content"})[0].text

                except:
                    comments = "no comments"

                mydict = {"Product":search_url, "Name":name, "Rating":ratting, "CommentHead":heading, "Comment": comments}
                reviews.append(mydict)

            field_names = ['Product', 'Name', 'Rating', 'CommentHead', "Comment"]
            try:
                with open(filename, 'w', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=field_names)
                    writer.writeheader()
                    writer.writerows(reviews)
            except Exception as e:
                print("error in file creation : ", e)

            return render_template('results.html',reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)


