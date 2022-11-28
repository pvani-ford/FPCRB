import pandas as pd
import requests
from google_play_scraper import Sort, reviews, app
from datetime import date, timedelta
from flair.models import TARSClassifier
from flair.data import Sentence
import datetime
from collections import Counter
from dateutil import parser
import matplotlib.pyplot as plt
import time
import requests

def call_api(country, appid):
    country_name = str(country).upper()
    df = pd.DataFrame()
    for i in range(1,11):
        response_API = requests.get('https://itunes.apple.com/'+str(country)+'/rss/customerreviews/page='+str(i)+'/id='+str(appid)+'/sortBy=mostRecent/json')
        if response_API.status_code == 200:
            data = response_API.json()
    
            feed = data['feed']
            if len(feed) < 8:
                break
            else:
                entry = feed['entry']
                df1 = pd.json_normalize(entry)
                df1['Name'] = df1['author.name.label']
                df1['Date'] = df1['updated.label']
                df1['Rating'] = df1['im:rating.label']
                df1['Review'] = df1['content.label']
                df1['Version'] = df1['im:version.label']
                df1['Platform'] = "iOS"
                df1['Country'] = country_name
                df1 = df1[['Name','Date','Rating','Review','Version', 'Platform', 'Country']]
                df1['Date'] = [parser.parse(i) for i in df1['Date']]
                df1['Date'] =[i.date() for i in df1['Date']]
                df1['Rating'] = pd.to_numeric(df1['Rating'])
                df = pd.concat([df,df1])
            
        else:
            print("Error fetching on page "+i)
    return df

def fetch_ios_reviews():
    
     #app ids
    us_app_id = "1095418609"
    nz_app_id = "1413892033"
    gb_app_id = "1141464928"
    mx_app_id = "1095418609"
    za_app_id = "1548761721"
    au_app_id = "1413892033"
    in_app_id = "1462652145"
    ca_app_id = "1095418609"
    
    us_df = call_api(country='us', appid = us_app_id)
    nz_df = call_api(country='nz', appid = nz_app_id)
    gb_df = call_api(country='gb', appid = gb_app_id)
    mx_df = call_api(country='mx', appid = mx_app_id)
    za_df = call_api(country='za', appid = za_app_id)
    au_df = call_api(country='au', appid = au_app_id)
    in_df = call_api(country='in', appid = in_app_id)
    ca_df = call_api(country='ca', appid = ca_app_id)
    
    combine_dfs = [us_df, nz_df, gb_df, mx_df, za_df, au_df, in_df, ca_df]
    all_reviews = pd.concat(combine_dfs, ignore_index = True)
    
    
    return all_reviews
def fetch_android_reviews():
    app_img = 'com.ford.fordpassimg' #com.ford.fordpass
    app_us ='com.ford.fordpass'
    app_eu = 'com.ford.fordpasseu'
    app_ap = 'com.ford.fordpassap' 


    app_img_reviews = []
    app_us_reviews = []
    app_eu_reviews = []
    app_ap_reviews = []

    #fetch the reviews from play store using 'reviews' method
    img_reviews, token1 = reviews(
        app_img,
        country = 'za',
        sort = Sort.NEWEST,
        count = 500,
        filter_score_with = None
    )

    us_reviews, token2 = reviews(
        app_us,
        country = 'us',
        sort = Sort.NEWEST,
        count = 500,
        filter_score_with = None
    )

    eu_reviews, token3 = reviews(
        app_eu,
        country = 'uk',
        sort = Sort.NEWEST,
        count = 500,
        filter_score_with = None
    )

    ap_reviews, token4 = reviews(
        app_img,
        country = 'au',
        sort = Sort.NEWEST,
        count = 500,
        filter_score_with = None
    )


    #convert the reviews into dataframe
    #IMG
    for img_review in img_reviews:
        review = {}
        review['Name'] = img_review["userName"]
        review['Rating'] = img_review["score"]
        review['Review'] = img_review["content"]
        review['Rated_at'] = img_review['at']
        review['Country'] = "ZA"
        review['Version'] = img_review['reviewCreatedVersion']
        app_img_reviews.append(review)
    img_reviews_df = pd.DataFrame(app_img_reviews)

    #US
    for us_review in us_reviews:
        review = {}
        review['Name'] = us_review["userName"]
        review['Rating'] = us_review["score"]
        review['Review'] = us_review["content"]
        review['Rated_at'] = us_review['at']
        review['Country'] = "US"
        review['Version'] = us_review['reviewCreatedVersion']
        app_us_reviews.append(review)
    us_reviews_df = pd.DataFrame(app_us_reviews)

    #EU
    for eu_review in eu_reviews:
        review = {}
        review['Name'] = eu_review["userName"]
        review['Rating'] = eu_review["score"]
        review['Review'] = eu_review["content"]
        review['Rated_at'] = eu_review['at']
        review['Country'] = "UK"
        review['Version'] = eu_review['reviewCreatedVersion']
        app_eu_reviews.append(review)
    eu_reviews_df = pd.DataFrame(app_eu_reviews)

    #AP
    for ap_review in ap_reviews:
        review = {}
        review['Name'] = ap_review["userName"]
        review['Rating'] = ap_review["score"]
        review['Review'] = ap_review["content"]
        review['Rated_at'] = ap_review['at']
        review['Country'] = "AU"
        review['Version'] = ap_review['reviewCreatedVersion']
        app_ap_reviews.append(review)
    ap_reviews_df = pd.DataFrame(app_ap_reviews)
    
    joined_df = [img_reviews_df, us_reviews_df, eu_reviews_df, ap_reviews_df]
    all_reviews = pd.concat(joined_df, ignore_index = True)
    
    all_reviews['Platform'] = 'Android'
    all_reviews['Date'] = [d.date() for d in all_reviews['Rated_at']]

    return all_reviews

fetched_ios = fetch_ios_reviews()
fetched_android = fetch_android_reviews()
today = date.today()
tars = TARSClassifier.load('tars-base')
def flair_prediction(x):
    sentences = Sentence(x)
    tars.predict(sentences) 
    score = sentences.labels
    if "positive" in str(score):
        return "Positive"
    elif "negative" in str(score):
        return "Negative"
    elif "neutral" in str(score):
        return "Neutral"

def flair_prediction_value(x):
    sentence = Sentence(x)
    tars.predict(sentence)
    score = sentence.get_label().score
    return score

def sentiment(df1):
    df1 = df1[["Name", "Rating", "Review", "Date","Country","Version","Platform"]]
    start = time.time()
    df1["sentiment"] = df1["Review"].apply(flair_prediction)
    df1["sentiment_score_mean"] = df1["Review"].apply(flair_prediction_value)
    end = time.time()
    return df1

androidSentiment = sentiment(fetched_android)
iOSSentiment = sentiment(fetched_ios)

def send_mail(positive_reviews, negative_reviews, total_reviews, avg_rating, star_1, star_2, star_3, star_4, star_5, words, date_format):
    from redmail import outlook
    outlook.username = 'newusecasetesting@outlook.com'

    outlook.password = 'Xyz@456123'
    outlook.send(
    subject="Reporting Weekly Reviews - Android & iOS",
    sender="newusecasetesting@outlook.com",    
    receivers="ipm_in@groups.ford.com",
    html = """ 

    <!DOCTYPE html>
    <html>
    <head>
    <title>HTML CSS JS</title>
    </head>
    <body>
        <div>
          <div class="x_x_expired_banner" align="center" style="background:#461599; color:#ffffff; box-sizing:border-box; padding:10px">
            <div align="center" style="color:#dee609; box-sizing:border-box">Good Morning, weekly report is generated</div>
            <br style="box-sizing:border-box" aria-hidden="true">
            <div style="box-sizing:border-box">
              <a href="http://19.39.78.32:8099/" target="_blank" rel="noopener noreferrer" data-auth="NotApplicable" style="background-color:#3498db; border-radius:4px; color:#ffffff!important; display:inline-block; font-family:sans-serif; font-size:13px; line-height:30px; text-align:center; text-decoration:none; width:200px; box-sizing:border-box" data-safelink="true" data-linkindex="0">Goto Dashboard</a> 
            </div>
          </div>

          <div class="zVKDv" has-hovered="true" style="height: 811px; width: 100%;">
            <table id="x_x_main-rows" border="0" cellpadding="0" cellspacing="0" width="100%" style="width: 100%; padding-top: 10px; box-sizing: border-box; transform: scale(0.984776, 0.984776); transform-origin: left top;" min-scale="0.9847764034253093">
              <tbody>
                <tr style="box-sizing:border-box">
                  <td style="border-collapse:collapse; box-sizing:border-box">
                    <center style="box-sizing:border-box">
                      <table class="x_x_fixed-width" width="650" style="box-sizing:border-box; margin:15px 0 10px">
                        <tbody>
                          <tr style="box-sizing:border-box">
                            <td id="x_x_header" valign="middle" align="left" style="border-collapse:collapse; box-sizing:border-box; padding:0 0 40px">
                                          <h1 class="x_x_card-app-name" align="left" style="color:#333; box-sizing:border-box; font-weight:400; margin:0; padding:0">FordPass</h3>
                                          <span class="x_x_card-store-name" style="box-sizing:border-box; color:#8E8E8E; font-size:18px; font-weight:500">Customer Review Board
                                </span> 
                            </td>
                            <td align="right" style="border-collapse:collapse; box-sizing:border-box; padding:0 0 40px">
                              <h1 style="color:#88898c; font-size:18px; font-weight:400; box-sizing:border-box; margin:0; padding:0">Weekly Summary </h1>
                              <h2 style="color:#000; font-size:25px; font-weight:400; box-sizing:border-box; margin:5px 0 0; padding:0">{{date}}</h2>
                            </td>
                          </tr>
                          <tr style="box-sizing:border-box">
                            <td class="x_x_table" colspan="2" style="border-collapse:collapse; box-sizing:border-box">
                              <div class="x_x_data-note" style="color:#88898c; font-weight:400; box-sizing:border-box">
                                Ordered by
                                <strong style="color:#000; font-weight:400; box-sizing:border-box">Max Stars</strong>
                                rating.
                              </div>
                              <div class="x_x_card-list" style="box-sizing:border-box; margin-bottom:40px">
                                <div class="x_x_card x_x_full-card" style="box-sizing:border-box; max-width:650px; background-color:#FFFFFF; border-radius:10px; margin:20px 0; padding:0 0 5px">
                                  <table class="x_x_card-title" style="box-sizing:border-box; border-bottom-width:2px; border-bottom-color:#f2f2f2; border-bottom-style:solid; width:100%; margin:0; padding:2px 10px">
                                    <tbody style="box-sizing:border-box">
                                      <tr style="box-sizing:border-box">
                                        <td class="x_x_card-icon" align="center" style="border-collapse:collapse; box-sizing:border-box; width:1%">
                                          <img data-imagetype="External" src="https://play-lh.googleusercontent.com/ko6qZ--hANpFN94B4xTTEkqtLq5UINNRnYBdxEGFJN9vCiIdFzkwVO7gs4SnPgx6ReOX" alt="" width="32" height="32" style="border-radius:6px; height:32px; line-height:100%; outline:none; text-decoration:none; box-sizing:border-box; margin-right:7px; width:32px; border:0 none">
                                        </td>
                                        <td style="border-collapse:collapse; box-sizing:border-box">
                                          <h3 class="x_x_card-app-name" align="left" style="color:#333; box-sizing:border-box; font-size:17px; font-weight:400; margin:0; padding:0">FordPass</h3>
                                          <span class="x_x_card-store-name" style="box-sizing:border-box; color:#8E8E8E; font-size:11px; font-weight:500">IOS, Android</span> 
                                        </td>
                                        <td class="x_x_card-open-link" align="right" valign="top" style="border-collapse:collapse; box-sizing:border-box; white-space:nowrap; padding:20px 10px">
                                          <a href="http://19.39.78.32:8099/" target="_blank" rel="noopener noreferrer" data-auth="NotApplicable" style="color:#C48C15!important; box-sizing:border-box; font-size:13px; font-weight:500; text-decoration:none" data-safelink="true" data-linkindex="2">Open in Dashboard</a> 
                                        </td>
                                      </tr>
                                    </tbody>
                                  </table>
                                  <table class="x_x_vital-stats" style="box-sizing:border-box; width:100%; margin:20px 0">
                                    <tbody style="box-sizing:border-box">
                                      <tr style="box-sizing:border-box">
                                        <td style="width:70px; border-collapse:collapse; box-sizing:border-box">
                                          <div class="x_x_grade-container" align="center" style="background-color:#088508; box-sizing:border-box; width:30px; height:30px; border-radius:24px; margin-left:10px; padding:0">
                                            <span class="x_x_grade" style="box-sizing:border-box; line-height:30px; color:#FFF; font-size:15px; font-weight:400">{{pos_reviews}}</span>
                                          </div>
                                          <div class="x_x_grade-container" align="center" style="background-color:#FF5D48; box-sizing:border-box; width:30px; height:30px; border-radius:24px; margin-left:10px; margin-top: 10px;padding:0">
                                            <span class="x_x_grade" style="box-sizing:border-box; line-height:30px; color:#FFF; font-size:15px; font-weight:400">{{neg_reviews}}</span>
                                          </div>
                                        </td>
                                        <td style="border-collapse:collapse; box-sizing:border-box">
                                          <div class="x_x_sentiment-sentence" style="box-sizing:border-box; margin-top:-5px; font-weight:400">
                                            <span class="x_x_sentiment-same" style="box-sizing:border-box">Positive Reviews</span>
                                          </div>
                                          <div class="x_x_sentiment-sentence" style="box-sizing:border-box; margin-top:20px; font-weight:400">
                                            <span class="x_x_sentiment-same" style="box-sizing:border-box">Negative Reviews</span>
                                          </div>
                                        </td>
                                        <td class="x_x_numeric-stat-box" align="left" style="border-collapse:collapse; box-sizing:border-box; border-left-width:2px; border-left-color:#E9E9EB; border-left-style:solid; padding-left:20px; width:25%">
                                          <span class="x_x_title-label" style="box-sizing:border-box; color:#8E8E8E!important; font-size:13px; font-weight:500">Reviews</span>
                                          <div class="x_x_review-statistic-large" style="box-sizing:border-box; margin-top:5px">
                                            <span class="x_x_numeric-actual" style="box-sizing:border-box; font-size:20px; font-weight:400">{{total_reviews}}</span> 
                                          </div>
                                        </td>
                                        <td class="x_x_numeric-stat-box" align="left" style="border-collapse:collapse; box-sizing:border-box; border-left-width:2px; border-left-color:#E9E9EB; border-left-style:solid; padding-left:20px; width:25%">
                                          <span class="x_x_title-label" style="box-sizing:border-box; color:#8E8E8E!important; font-size:13px; font-weight:500">Avg Stars</span>
                                          <div class="x_x_review-statistic-large" style="box-sizing:border-box; margin-top:5px">
                                            <span class="x_x_numeric-actual" style="box-sizing:border-box; font-size:20px; font-weight:400">{{avg_ratings}}</span> 

                                          </div>
                                        </td>
                                      </tr>
                                    </tbody>
                                  </table>
                                  <div class="x_x_breakdowns" style="box-sizing:border-box; background-color:#F9F9F9; border-radius:6px; margin:0 5px; padding:8px 0">
                                    <table style="box-sizing:border-box; table-layout:fixed">
                                      <tbody style="box-sizing:border-box">
                                        <tr style="box-sizing:border-box">
                                          <td class="x_x_title-cell" valign="top" style="border-collapse:collapse; box-sizing:border-box; white-space:nowrap; padding:0 20px 7px 10px">
                                            <span class="x_x_title-label" style="box-sizing:border-box; color:#8E8E8E!important; font-size:13px; font-weight:500">Stars Breakdown</span> 
                                          </td>
                                          <td class="x_x_title-cell" valign="top" style="border-collapse:collapse; box-sizing:border-box; white-space:nowrap; padding:0 20px 7px">
                                             <span class="x_x_title-label" style="box-sizing:border-box; color:#8E8E8E!important; font-size:13px; font-weight:500">Popular Words</span> 
                                          </td>
                                          <td class="x_x_title-cell" valign="top" style="border-collapse:collapse; box-sizing:border-box; white-space:nowrap; padding:0 20px 7px">
                                             <span class="x_x_title-label" style="box-sizing:border-box; color:#8E8E8E!important; font-size:13px; font-weight:500">Hot Regions</span>
                                          </td>
                                        </tr>
                                        <tr style="box-sizing:border-box">
                                          <td rowspan="3" class="x_x_content-cell x_x_breakdown-cell" valign="top" style="border-collapse:collapse; box-sizing:border-box; font-size:10px; font-weight:500; line-height:20px; width:1%; white-space:nowrap; padding:0 10px 0 10px">
                                            <div style="box-sizing:border-box">
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span> 
                                              <span class="x_x_topic" style="color:#C48C15!important; box-sizing:border-box; font-size:13px; font-weight:500; text-decoration:none; margin-left:10px">{{star_5}}</span> 
                                            </div>
                                            <div style="box-sizing:border-box">
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-off" style="box-sizing:border-box; font-size:14px; color:#E1E6EA">★</span> 
                                              <span class="x_x_topic" style="color:#C48C15!important; box-sizing:border-box; font-size:13px; font-weight:500; text-decoration:none; margin-left:10px">{{star_4}}</span> 
                                            </div>
                                            <div style="box-sizing:border-box">
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-off" style="box-sizing:border-box; font-size:14px; color:#E1E6EA">★</span>
                                              <span class="x_x_star-off" style="box-sizing:border-box; font-size:14px; color:#E1E6EA">★</span> 
                                              <span class="x_x_topic" style="color:#C48C15!important; box-sizing:border-box; font-size:13px; font-weight:500; text-decoration:none; margin-left:10px">{{star_3}}</span> 
                                            </div>
                                            <div style="box-sizing:border-box">
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-off" style="box-sizing:border-box; font-size:14px; color:#E1E6EA">★</span>
                                              <span class="x_x_star-off" style="box-sizing:border-box; font-size:14px; color:#E1E6EA">★</span>
                                              <span class="x_x_star-off" style="box-sizing:border-box; font-size:14px; color:#E1E6EA">★</span> 
                                              <span class="x_x_topic" style="color:#C48C15!important; box-sizing:border-box; font-size:13px; font-weight:500; text-decoration:none; margin-left:10px">{{star_2}}</span>
                                            </div>
                                            <div style="box-sizing:border-box">
                                              <span class="x_x_star-on" style="box-sizing:border-box; font-size:14px; color:#F3B636">★</span>
                                              <span class="x_x_star-off" style="box-sizing:border-box; font-size:14px; color:#E1E6EA">★</span>
                                              <span class="x_x_star-off" style="box-sizing:border-box; font-size:14px; color:#E1E6EA">★</span>
                                              <span class="x_x_star-off" style="box-sizing:border-box; font-size:14px; color:#E1E6EA">★</span>
                                              <span class="x_x_star-off" style="box-sizing:border-box; font-size:14px; color:#E1E6EA">★</span> 
                                              <span class="x_x_topic" style="color:#C48C15!important; box-sizing:border-box; font-size:13px; font-weight:500; text-decoration:none; margin-left:10px">{{star_1}}</span>
                                            </div>
                                          </td>
                                          <td class="x_x_content-cell x_x_words-cell" valign="top" style="border-collapse:collapse; box-sizing:border-box; font-size:14px; font-weight:500; width:40%; padding:0 20px"> {{words}} </td>
                                          <td class="x_x_content-cell x_x_topics-cell" valign="top" style="border-collapse:collapse; box-sizing:border-box; font-size:14px; font-weight:500; width:40%; padding:0 20px">

                                        <img data-imagetype="External" src="{{pie_chart.src}}" alt="" width="130" height="130" style="border-radius:6px; height:130px; line-height:100%; outline:none; text-decoration:none; box-sizing:border-box; margin-right:7px; width: 130px; border:0 none">

                                          </td>
                                        </tr>
                                      </tbody>
                                    </table>
                                  </div>
                                </div>
                              </div>
                             </td>
                          </tr>
                          <tr style="box-sizing:border-box">
                            <td id="x_x_footer" colspan="2" align="center" style="font-size:11px; line-height:1.5; color:#000; border-collapse:collapse; box-sizing:border-box; padding:20px">
                              <div style="box-sizing:border-box">Any issues with this email or Need Support? Email us:  <b>pvani@ford.com | skeshav@ford.com</b> 
                              </div>
                              <img data-imagetype="External" src="https://hooks.appbot.co/sent_emails/26466880.gif" alt="" style="height:auto; line-height:100%; outline:none; text-decoration:none; box-sizing:border-box; border:0 none">
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </center>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
       </div>    
    </body>
    </html>


    """,
        body_params={
            'pos_reviews': positive_reviews,
            'neg_reviews': negative_reviews,
            'total_reviews': total_reviews,
            'avg_ratings': f'{avg_rating}',
            'star_1': star_1,
            'star_2': star_2,
            'star_3': star_3,
            'star_4': star_4,
            'star_5': star_5,
            'words': ', '.join(words),
            'date': date_format
        },
        body_images={
            'pie_chart': 'pie.png',
        }
    )

bothPlatform = [androidSentiment, iOSSentiment]
df1_final = pd.concat(bothPlatform, ignore_index = True)
df1_final.drop_duplicates(subset="Name", keep='first', inplace=True)
df1_final.reset_index(drop = True, inplace=True)
df1_final.to_csv("finalDF.csv")
positive_reviews = df1_final[(df1_final['sentiment'] == "Positive") & (df1_final['sentiment_score_mean'] > 0.985066)].copy()
positive_reviews.reset_index(drop=True, inplace=True)
negative_reviews = df1_final[(df1_final['sentiment'] == "Negative") & (df1_final['sentiment_score_mean'] > 0.60)].copy()
negative_reviews.reset_index(drop=True, inplace=True)
neutral_reviews = df1_final[(df1_final['sentiment'] == "Neutral") & (df1_final['sentiment_score_mean'] > 0.80)].copy()
neutral_reviews.reset_index(drop=True, inplace=True)
mixed_reviews_1 = df1_final[(df1_final['sentiment'] == "Neutral") & (df1_final['sentiment_score_mean'] < 0.9999)].copy()
mixed_reviews_2 = df1_final[((df1_final['sentiment'] == "Positive") & (df1_final['sentiment_score_mean'] < 0.985))].copy()
mixed_reviews_3 = df1_final[((df1_final['sentiment'] == "Negative") & (df1_final['sentiment_score_mean'] < 0.60))].copy()
mixed_joint = [mixed_reviews_1, mixed_reviews_2,mixed_reviews_3]
mixed_reviews = pd.concat(mixed_joint, ignore_index = True)
mixed_reviews.reset_index(drop=True, inplace=True)
mixed_reviews['sentiment'] = "Mixed"

positive_reviews.to_csv("PositiveFeedback.csv")
negative_reviews.to_csv("NegativeFeedback.csv")
mixed_reviews.to_csv("MixedFeedback.csv")

today = date.today()
end_date = today - timedelta(7)
initial_date = today
email_date_format = f"{initial_date.strftime('%-d')} {initial_date.strftime('%b')} - {end_date.strftime('%-d')} {end_date.strftime('%b')} 2022"

def date_string_to_date(date_string):
   pd.to_datetime(date_string, infer_datetime_format=True).date()

stopwords_list = requests.get("https://gist.githubusercontent.com/rg089/35e00abf8941d72d419224cfd5b5925d/raw/12d899b70156fd0041fa9778d657330b024b959c/stopwords.txt").content
stopwords = set(stopwords_list.decode().splitlines()) 
def stopwordingsk(s):
    s= s.lower()
    return " ".join(w for w in s.split() if w not in stopwords)
words= []
df2_final = df1_final.copy()
df2_final['CleanText'] = df2_final['Review'].apply(lambda x: stopwordingsk(x))
range_df = df2_final[(df2_final['Date']<= pd.to_datetime(today).date()) & (df2_final['Date']>=pd.to_datetime(end_date).date())]
positiveCount = range_df['sentiment'].value_counts()['Positive']
negativeCount = range_df['sentiment'].value_counts()['Negative']

records = Counter()
for word in range_df['CleanText'].values:
    records.update(word.split(" "))
for x in records.most_common(20):
    words.append(x[0])

star_1 = range_df['Rating'].value_counts()[1]
star_2 = range_df['Rating'].value_counts()[2]
star_3 = range_df['Rating'].value_counts()[3]
star_4 = range_df['Rating'].value_counts()[4]
star_5 = range_df['Rating'].value_counts()[5]
totalCount = range_df.shape[0]
avgRating = round(range_df['Rating'].mean())

select_series = range_df[['Country', 'Rating']]
values = select_series.groupby("Country")["Rating"].sum()
labels = values.keys()
    
 # Create subplot
fig, ax = plt.subplots()
    
# Generate pie chart
ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
# Equal aspect ratio ensures that pie is drawn as a circle.
    
# Set Title
ax.set_title('Country Wise Reviews', fontweight="bold")
    
# Save the plot as a PNG
plt.savefig(f"pie.png", dpi=300, bbox_inches='tight', pad_inches=0)

send_mail(positiveCount,negativeCount,totalCount,avgRating, star_1,star_2,star_3,star_4,star_5,words,email_date_format)

