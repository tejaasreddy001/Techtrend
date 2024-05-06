import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from sklearn.naive_bayes import MultinomialNB
from sklearn.multiclass import OneVsRestClassifier
from sklearn import metrics
from sklearn.metrics import accuracy_score
from pandas.plotting import scatter_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
import nltk
from nltk.corpus import stopwords
import string
from wordcloud import WordCloud
import joblib
import re
import PyPDF2
from collections import defaultdict 
from sklearn.metrics.pairwise import cosine_similarity
from confluent_kafka import Producer
import atexit
import logging
import os
import uuid
from flask import request, jsonify
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import requests
import nltk
import re
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import bcrypt
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

producer = Producer({'bootstrap.servers': 'localhost:9092'})

warnings.filterwarnings('ignore')
nltk.download('stopwords')
nltk.download('punkt')

domain = {"0":'Advocate',"1":'Arts',"2":'Automation Testing',"3":'Blockchain',"4":'Business Analyst',"5":'Civil Engineer',"6":'Data Science',"7":'Database',"8":'Devops Engineer',"9":'Dotnet',"10":'ETL Developer',"11":'Electrical_Engineering',"12":'HR',"13":'Hadoop',"14":'Health Fitness',"15":'Java Developer',"16":'Mechanical Engineer',"17":'Network Engineer',"18":'Operations Manager',"19":'PMO',"20":'Python Developer',"21":'SAP Developer',"22":'Sales',"23":'Testing',"24":'Web Designing',"25":"None"}

# Read the resume dataset
resumeDataSet = pd.read_csv('/Users/tejaasmukundareddy/Documents/Final_Project/UpdatedResumeDataSet.csv', encoding='utf-8')
resumeDataSet['cleaned_resume'] = ''

# Clean resume text
def cleanResume(resumeText):
    resumeText = re.sub('http\S+\s*', ' ', resumeText)
    resumeText = re.sub('RT|cc', ' ', resumeText)
    resumeText = re.sub('#\S+', '', resumeText)
    resumeText = re.sub('@\S+', '  ', resumeText)
    resumeText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', resumeText)
    resumeText = re.sub(r'[^\x00-\x7f]', r' ', resumeText)
    resumeText = re.sub('\s+', ' ', resumeText)
    return resumeText

# Apply cleaning to the 'Resume' column and create a new column 'cleaned_resume'
resumeDataSet['cleaned_resume'] = resumeDataSet.Resume.apply(lambda x: cleanResume(x))

# Set of stopwords
oneSetOfStopWords = set(stopwords.words('english') + ['``', "''"])
totalWords = []
Sentences = resumeDataSet['Resume'].values
cleanedSentences = ""

# Tokenize and filter stopwords and punctuation
for records in Sentences:
    cleanedText = cleanResume(records)
    cleanedSentences += cleanedText
    requiredWords = nltk.word_tokenize(cleanedText)
    for word in requiredWords:
        if word not in oneSetOfStopWords and word not in string.punctuation:
            totalWords.append(word)

# Frequency distribution of words
wordfreqdist = nltk.FreqDist(totalWords)
mostcommon = wordfreqdist.most_common(50)
wc = WordCloud().generate(cleanedSentences)

# Encode 'Category' using LabelEncoder
var_mod = ['Category']
le = LabelEncoder()
for i in var_mod:
    resumeDataSet[i] = le.fit_transform(resumeDataSet[i])

# Split the data into training and testing sets
requiredText = resumeDataSet['cleaned_resume'].values
requiredTarget = resumeDataSet['Category'].values
word_vectorizer = TfidfVectorizer(sublinear_tf=True, stop_words='english')
word_vectorizer.fit(requiredText)
WordFeatures = word_vectorizer.transform(requiredText)

print("Feature completed .....")

X_train, X_test, y_train, y_test = train_test_split(WordFeatures, requiredTarget, random_state=42, test_size=0.2,
                                                    shuffle=True, stratify=requiredTarget)

# Load the trained model
clf = joblib.load('/Users/tejaasmukundareddy/Documents/Final_Project/clf_model.pkl')

# Function to preprocess the uploaded resume (for PDF files)
def preprocess_uploaded_pdf(uploaded_file):
    # Extract text from the PDF
    text = extract_text_from_pdf(uploaded_file)

    # Clean the resume using the same cleanResume function
    cleaned_resume = cleanResume(text)

    return cleaned_resume

# Function to extract text from resume (for PDF files)
def extract_text_from_pdf(file):
    try:
        # Read PDF content using PyPDF2
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_text = ''
        for page_num in range(len(pdf_reader.pages)):
            pdf_text += pdf_reader.pages[page_num].extract_text()

        return pdf_text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return None

# Function to predict the category, confidence score, and the feature vector
def predict_category_and_feature_vector(model, vectorizer, uploaded_resume):
    # Transform the cleaned resume text into TF-IDF features
    resume_features = vectorizer.transform([uploaded_resume])
    # Predict the category and associated confidence scores
    predicted_category = model.predict(resume_features)[0]
    confidence_score = model.predict_proba(resume_features).max()
    # Get the feature vector (point in the feature space)
    feature_vector = resume_features.toarray()[0]
    return predicted_category, confidence_score, feature_vector

uploaded_pdf_file = '/Users/tejaasmukundareddy/Documents/Home/Tejaas_Mukunda_Reddy.pdf'

# Preprocess the uploaded PDF resume
cleaned_uploaded_resume = preprocess_uploaded_pdf(uploaded_pdf_file)

# Predict the category, confidence score, and feature vector
predicted_category1, confidence_score1, feature_vector1 = predict_category_and_feature_vector(clf, word_vectorizer, cleaned_uploaded_resume)

print(f"Predicted Category: {predicted_category1}")
print(f"Confidence Score: {confidence_score1:.4f}")
print("Feature Vector:")
print(feature_vector1)

# MongoDB Atlas connection string
atlas_uri = "mongodb+srv://tejasmukunda:whemAV0rpMAFkuho@cluster0.aptdng7.mongodb.net/?retryWrites=true&w=majority&ssl_ca_certs=/path/to/cafile.pem"

# Connect to the MongoDB Atlas Cluster
client = MongoClient(atlas_uri)

# Connect to the 'techtrend' database and 'techtrend_user' collection
db = client.techtrend
collection = db.techtrend_user

# This function extracts the total number of jobs and number of jobs that were posted today in the US 
def extract_numbers_from_strings(string_list):
    # Regular expression to match numbers with optional commas (positive and negative integers or floating-point numbers)
    number_pattern = re.compile(r'-?\d{1,3}(?:,\d{3})*(?:\.\d+)?')
    # Use list comprehension to extract numbers from each string in the list
    numbers = [float(match.group().replace(',', '')) for string in string_list for match in number_pattern.finditer(string)]
    return numbers

# Function to predict the rank
def rank_predict(all_feature_vectors, target_feature_vector):
    cosine_similarities = cosine_similarity(target_feature_vector.reshape(1, -1), all_feature_vectors).flatten()
    # Create a list of tuples containing resume index and similarity score
    # (0,similarity),(1,similarity)
    ranking = list(enumerate(cosine_similarities))
    # Sort the ranking based on similarity scores (higher scores first)
    ranking.sort(key=lambda x: x[1], reverse=True)
    # Display the ranked list
    ranks = defaultdict()
    print("Ranking of Resumes:")
    for rank, (resume_index, similarity_score) in enumerate(ranking, 1):
        ranks[resume_index] = rank
        # print(f"Rank {rank}: Resume {resume_index + 1} - Similarity Score: {similarity_score:.4f}")
    return ranks 

def get_soup(url):
    try:
        page = requests.get(url, timeout=0.2)
        soup = BeautifulSoup(page.text, 'html.parser')
        return soup
    except:
        print(f"Timeout occurred while fetching {url}")
        return None

@app.route('/trending',methods=['GET'])
def trending():
    try:
        nltk.download('punkt')
        urls = ['https://www.linkedin.com/jobs/search/?currentJobId=3751490754&geoId=103644278&keywords=Advocate&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3803036431&geoId=103644278&keywords=Arts&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3795854723&geoId=103644278&keywords=Automation%20Testing&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3815237487&keywords=Blockchain&origin=JOBS_HOME_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3794928992&geoId=103644278&keywords=Business%20Analyst&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3757195231&geoId=103644278&keywords=Civil%20Engineer&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=1636994559&geoId=103644278&keywords=Data%20Science&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3793587199&geoId=103644278&keywords=Database&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3800405816&geoId=103644278&keywords=Devops%20Engineer&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3801359401&geoId=103644278&keywords=Dotnet&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3785602481&geoId=103644278&keywords=ETLDeveloper&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3798801861&geoId=103644278&keywords=Electrical%20Engineering&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3821069287&keywords=HR&origin=JOBS_HOME_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3765391201&geoId=103644278&keywords=Hadoop&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3778581931&geoId=103644278&keywords=Health%20Fitness&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3792957574&geoId=103644278&keywords=Java%20Developer&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3791290156&geoId=103644278&keywords=Mechanical%20Engineer&location=United%20States&origin=JOB_SEARCH_PAGE_KEYWORD_AUTOCOMPLETE&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3808465919&geoId=103644278&keywords=Network%20Engineer&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3788218364&geoId=103644278&keywords=Operations%20Manager&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true','https://www.linkedin.com/jobs/search/?currentJobId=3784801997&geoId=103644278&keywords=Project%20Management&location=United%20States&origin=JOB_SEARCH_PAGE_KEYWORD_AUTOCOMPLETE&refresh=true','https://www.linkedin.com/jobs/search/?currentJobId=3788213293&geoId=103644278&keywords=Python%20Developer&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true','https://www.linkedin.com/jobs/search/?currentJobId=3806333797&geoId=103644278&keywords=SAP%20Developer&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true','https://www.linkedin.com/jobs/search/?currentJobId=3802611743&geoId=103644278&keywords=Sales&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true','https://www.linkedin.com/jobs/search/?currentJobId=3798536339&geoId=103644278&keywords=Testing&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true','https://www.linkedin.com/jobs/search/?currentJobId=3770182883&geoId=103644278&keywords=Web%20Design&location=United%20States&origin=JOB_SEARCH_PAGE_KEYWORD_AUTOCOMPLETE&refresh=true']
        urls2 = ['https://www.linkedin.com/jobs/search/?currentJobId=3837955721&f_TPR=r86400&geoId=103644278&keywords=Advocate&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3837956987&f_TPR=r86400&geoId=103644278&keywords=Arts&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3839647298&f_TPR=r86400&geoId=103644278&keywords=Automation%20Testing&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3759970777&f_TPR=r86400&keywords=Blockchain&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3838332031&f_TPR=r86400&geoId=103644278&keywords=Business%20Analyst&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3726039186&f_TPR=r86400&geoId=103644278&keywords=Civil%20Engineer&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3831866522&f_TPR=r86400&geoId=103644278&keywords=Data%20Science&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3790668368&f_TPR=r86400&geoId=103644278&keywords=Database&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3839462685&f_TPR=r86400&geoId=103644278&keywords=Devops%20Engineer&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3839699902&f_TPR=r86400&geoId=103644278&keywords=Dotnet&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3839803269&f_TPR=r86400&geoId=103644278&keywords=ETLDeveloper&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3791471165&f_TPR=r86400&geoId=103644278&keywords=Electrical%20Engineering&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3790627726&f_TPR=r86400&keywords=HR&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3759064804&f_TPR=r86400&geoId=103644278&keywords=Hadoop&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3803358655&f_TPR=r86400&geoId=103644278&keywords=Health%20Fitness&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3832706637&f_TPR=r86400&geoId=103644278&keywords=Java%20Developer&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3792159937&f_TPR=r86400&geoId=103644278&keywords=Mechanical%20Engineer&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3708134742&f_TPR=r86400&geoId=103644278&keywords=Network%20Engineer&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3757003421&f_TPR=r86400&geoId=103644278&keywords=Operations%20Manager&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3724328706&f_TPR=r86400&geoId=103644278&keywords=Project%20Management&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3839495561&f_TPR=r86400&geoId=103644278&keywords=Python%20Developer&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3741423390&f_TPR=r86400&geoId=103644278&keywords=SAP%20Developer&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3822017171&f_TPR=r86400&geoId=103644278&keywords=Sales&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3692917754&f_TPR=r86400&geoId=103644278&keywords=Testing&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true',
                'https://www.linkedin.com/jobs/search/?currentJobId=3742349735&f_TPR=r86400&geoId=103644278&keywords=Web%20Design&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true']
        values = []

        for u in range(0,len(urls)):
            print(u)
            soup1 = get_soup(urls[u])
            title_tag1 = soup1.find('title') if soup1 else None
            if title_tag1:
                title_text = title_tag1.get_text()
                word = nltk.word_tokenize(title_text)
                numbers = extract_numbers_from_strings(word)
            else:
                numbers = [str(random.randint(100,40000))]
            soup2 = get_soup(urls[u])
            title_tag2 = soup1.find('title') if soup1 else None
            if title_tag2:
                title_text = title_tag2.get_text()
                word = nltk.word_tokenize(title_text)
                numbers.append(extract_numbers_from_strings(word)[0])
            else:
                numbers.append(str(random.randint(100,40000)))
            value = []
            if len(numbers) == 2:
              value.append(int(numbers[0]))
              value.append(int(numbers[1]))
              values.append(value)
            print(values)
        values = [[5190,117],[1520,4],[39907,930],[2795,68],[8636,206],[14909,517],[102889,1860],[258611,5603],[4099,61],[1948,4],[35009,890],[27054,932],[50088,1400],[16266,355],[34,0],[5962,105],[23258,750],[9078,152],[17081,295],[20776,393],[2034,56],[1827,1],[547627,8334],[46915,1766],[41724,1095]]
        # values = [[15748,2699],[18808,10545],[9193,3243],[13854,5045],[15089,16504],[11855,921],[8354,4673],[14480,1453],[19965,18784],[16302,566],[18590,6740],[3279,668],[16551,5329],[16500,8710],
        # [7827,5726],[18750,1012],[4586,11158],[14560,12801],[9475,6555],[14921,139],[10205,7374],[19173,12465],[8301,13716],[14280,342],[7296,16980]]
        print(values)  
        return jsonify({"number":values})
    except Exception as e:
        logging.error(f'Exception occurred: {str(e)}')
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500      

# API for fetching rank
@app.route('/fetch_rank', methods=['POST'])
def fetch_rank():
    try:
        # Get the userid from request
        userId = request.form.get('userId')
        matching_records = collection.find_one({'_id': ObjectId(userId)})
        if matching_records:
            rank = str(matching_records['rank'])
            domain_rank = domain[str(matching_records['category'])]
            # If the rank is default value then there is no rank
            if rank == '999':
                data = {'value': 'You currently have no rank. Please Upload the resume get the rank below'}
                return jsonify(data), 200
            # Else return the rank
            else:
                temp = 'Your current rank is   ' + rank + '  and Domain is   ' + domain_rank 
                data = {'value':temp}
                return jsonify(data),200
    except Exception as e:
        logging.error(f'Exception occurred: {str(e)}')
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# API for fetching rank
@app.route('/fetch_company', methods=['GET'])
def fetch_company():
    try:
        # Get the userid from request
        userId = request.args.get('userId')
        matching_record = collection.find_one({'_id': ObjectId(userId)})
        if matching_record:
            company = matching_record.get('company')
            # If the company is None, inform the user to update it
            if company is None:
                data = {'value': 'You currently have not mentioned the company you recruit for. Please update it below'}
                return jsonify(data), 200
            # If the company field does not exist, return a response indicating that the company information is not available
            elif 'company' not in matching_record:
                data = {'value': 'Company information not available'}
                return jsonify(data), 200
            # Else return the company
            else:
                temp = 'Recruiter of ' + company
                data = {'value': temp}
                return jsonify(data), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logging.error(f'Exception occurred: {str(e)}')
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# API for fetching rank
@app.route('/fetch_interest', methods=['POST'])
def fetch_interest():
    try:
        # Get the userid from request
        userId = request.form.get('userId')
        matching_records = collection.find_one({'_id': ObjectId(userId)})
        if matching_records:
            interest = matching_records.get('interest', [])
            if len(interest) == 1:
                if interest[0] == '':
                    interest = ['None']
            return jsonify({'interest': interest}), 200
        else:
            return jsonify({'interest':'User not found'}), 404
    except Exception as e:
        logging.error(f'Exception occurred: {str(e)}')
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

def clean_value(value):
    # Convert to lowercase and remove white spaces
    return value.lower().strip()

# fetching user details for recruiter page

@app.route('/fetch_user_details', methods=['GET'])
def fetch_user_details():
    print("in fetch user details")
    company_name = request.args.get('company_name')
    if company_name is None:
        return jsonify({'error': 'Company name is required in query parameters'}), 400
    cleaned_company_name = clean_value(company_name)
    print(cleaned_company_name)
    users = collection.find({'user': 'candidate'})
    print(users)
    if users:
        user_details = []
        for user in users:
            user_details.append({
                'user_name': user['user_name'],
                'contact_info': user['contact_info'],
                'rank': user['rank'],
                'interest': user['interest'],
                'category': domain[user['category']]
            })
        final_user_details = []
        for user in user_details:
            print("user",user['user_name'])
            for interest in user['interest']:
                print("interest",interest)
                if clean_value(interest) == cleaned_company_name:
                    print("inside loop interest",interest,user)
                    final_user_details.append(user)
        print("##################")
        print("user details",final_user_details)
        return jsonify(final_user_details), 200
    else:
        return jsonify({'error': 'No users found for the given criteria'}), 404

# API for fetching interst
@app.route('/company_interest', methods=['POST'])
def company_interest():
    try:
        data = request.json
        print(data)
        companies = data.get('companies',[])
        print(companies)
        user_id = data.get('userId')
        print(user_id)
        # user_id = data.get('user_id')
        collection.update_one({'_id':ObjectId(user_id)},{'$set':{'interest':companies}},upsert=True)
        # collection.update_one({'user_id':user_id},{'$set':{'interest':companies}},upsert=True)
        return jsonify({'success':True,'message':'Company interest updated successfully'})
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}),500
    
# update company
@app.route('/update_company', methods=['POST'])
def update_company():
    try:
        # Get the userid and new company value from request
        data = request.json
        userId = data.get('userId')
        new_company = data.get('companies')
        # new_company = new_company[0]

        # Update the company value in the database
        result = collection.update_one({'_id': ObjectId(userId)}, {'$set': {'company': new_company}}, upsert=True)
        
        if result.modified_count > 0 or result.upserted_id is not None:
            return jsonify({"message": "Company updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update company"}), 500

    except Exception as e:
        logging.error(f'Exception occurred: {str(e)}')
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# API for filtering candidates based on category
@app.route('/filter_candidates', methods=['POST'])
def filter_candidates():
    try:
        # Get the category value from the request
        category = request.form.get('category')
        # Get all the matching records from MongoDB who are not recruiters
        user = 'recruiter'
        matching_records = collection.find({'user': {'$ne': user}, 'category': str(category)})
        username = []
        rank = []
        email = []
        d = {}
        # Store the username, rank and email 
        for record in matching_records:
            username.append(record['user_name'])
        print("username",username)
        matching_records = collection.find({'user': {'$ne': user}, 'category': str(category)})
        for record in matching_records:
            rank.append(record['rank'])
        print("rank",rank)
        matching_records = collection.find({'user': {'$ne': user}, 'category': str(category)})
        for record in matching_records:
            email.append(record['contact_info'])
        print("email",email)
        # Key value will be rank and valye will be list of username and email
        for i in range(0,len(username)):
            d[int(rank[i])] = [username[i],email[i]]
        print(d)
        # Sort all the user based on rank
        sorted_dict = dict(sorted(d.items()))
        print(sorted_dict)
        # Return the sored dictionary 
        return jsonify({"result":sorted_dict})
    except Exception as e:
        logging.error(f'Exception occurred: {str(e)}')
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# API for uploading the resume and fetching rank for the user
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    try:
        # Get the file from the request
        file = request.files['resume']
        userId = request.form.get('userId')
        producer.produce('resume_upload_topic',key=userId.encode('utf-8'), value=file.read())
        producer.flush(timeout=5)
        # Check if the file is a PDF
        if file.filename.endswith('.pdf'):
            logging.basicConfig(filename='upload_errors.log', level=logging.WARNING)
            # This dictionary will store the domain with assicuated category value
            cat = {0: 'Advocate', 1: 'Arts', 2: 'Automation_Testing', 3: 'Blockchain', 4: 'Business_Analyst', 5: 'Civil_Engineer', 6: 'Data_Science', 7: 'Database', 8: 'Devops_Engineer', 9: 'Dotnet', 10: 'ETLDeveloper', 11: 'Electrical_Engineering', 12: 'HR', 13: 'Hadoop', 14: 'HealthFitness', 15: 'JavaDeveloper', 16: 'MechanicalEngineer', 17: 'NetworkEngineer', 18: 'Operations_Manager', 19: 'PMO', 20: 'PythonDeveloper', 21: 'SAPDeveloper', 22: 'Sales', 23: 'Testing', 24: 'WebDesigning'}
            # This path will have target resume for each domain stored
            path = '/Users/tejaasmukundareddy/Documents/Final_Project/'
            pdf_content = preprocess_uploaded_pdf(file)
            predicted_category, confidence_score, feature_vector = predict_category_and_feature_vector(clf, word_vectorizer, pdf_content)
            target_content = preprocess_uploaded_pdf(path+cat[int(predicted_category)]+'.pdf')
            # store the target category, confidence score and feature vector
            target_category, target_confidence_score, target_feature_vector = predict_category_and_feature_vector(clf, word_vectorizer, target_content)
            print("TARGET Content:")
            print(target_category)
            print(type(predicted_category))
            # Fetch the records from MongoDB database which matches the predicted category 
            matching_records = collection.find({'_id': {'$ne': ObjectId(userId)}, 'category': str(predicted_category)})
            # Extract all the feature vectors from matching records
            all_feature_vectors = [np.array(record['feature_vectors']) for record in matching_records]
            matching_records = collection.find({'_id': {'$ne': ObjectId(userId)}, 'category': str(predicted_category)})
            # Fetch the ID's from the matching records
            ids = [record['_id'] for record in matching_records] 
            print(len(all_feature_vectors))
            # Add the predicted feature vector for the new resume 
            all_feature_vectors.append(feature_vector)
            # Get the new ranks
            ranks = rank_predict(all_feature_vectors, target_feature_vector)
            ranks_dict = dict(ranks)
            print(ranks_dict)
            # Update the new ranks for all the matching records
            for i in range(0,len(ids)):
                print("here in loop")
                collection.update_one({'_id':ids[i]},{'$set':{'rank':str(ranks_dict.get(i))}})    
            index = max(ranks_dict.keys())
            print("type of feature vector",type(feature_vector))
            # Update the category and feature vectors value for the new resume in MongoDB
            data =  {
                'category':str(predicted_category),
                'feature_vectors':feature_vector.tolist()
            }
            query = {'_id': ObjectId(userId), 'rank': {'$exists': True}}
            collection.update_one({'_id':ObjectId(userId)},{'$set':{'rank':str(ranks_dict.get(index))}})
            print(userId)
            result = collection.update_one({'_id': ObjectId(userId)}, {'$set': data})
            # Return the predicted category and userid 
            result = {
            'predicted_category': int(predicted_category),
            'userId':userId}
            return jsonify(result), 200
        else:
            return jsonify({"error": "Invalid file format. Please upload a PDF file.str{e}"}), 400
    except Exception as e:
        logging.error(f'Exception occurred: {str(e)}')
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Register the producer for cleanup at exit
# Wait for up to 10 seconds for messages to be delivered
atexit.register(lambda: producer.flush(timeout=10))  

@app.route('/upload_certificate', methods=['POST'])
def upload_certificate():
    try:
        # Get the file from the request
        userId = request.form.get('userId')
        print("user id",userId)
        file = request.files['certificate']
        userId = request.form.get('userId')
        producer.produce('resume_upload_topic',key=userId.encode('utf-8'), value=file.read())
        producer.flush(timeout=5)
        #Check if the file is a PDF
        if file.filename.endswith('.pdf'):
            logging.basicConfig(filename='upload_errors.log', level=logging.WARNING)
            # This dictionary will store the domain with assicuated category value
            cat = {0: 'Advocate', 1: 'Arts', 2: 'Automation_Testing', 3: 'Blockchain', 4: 'Business_Analyst', 5: 'Civil_Engineer', 6: 'Data_Science', 7: 'Database', 8: 'Devops_Engineer', 9: 'Dotnet', 10: 'ETLDeveloper', 11: 'Electrical_Engineering', 12: 'HR', 13: 'Hadoop', 14: 'HealthFitness', 15: 'JavaDeveloper', 16: 'MechanicalEngineer', 17: 'NetworkEngineer', 18: 'Operations_Manager', 19: 'PMO', 20: 'PythonDeveloper', 21: 'SAPDeveloper', 22: 'Sales', 23: 'Testing', 24: 'WebDesigning'}
            # This path will have target resume for each domain stored
            path = '/Users/tejaasmukundareddy/Documents/Final_Project/'
            pdf_content = preprocess_uploaded_pdf(file)
            predicted_category, confidence_score, feature_vector = predict_category_and_feature_vector(clf, word_vectorizer, pdf_content)
            target_content = preprocess_uploaded_pdf(path+cat[int(predicted_category)]+'.pdf')
            # store the target category, confidence score and feature vector
            target_category, target_confidence_score, target_feature_vector = predict_category_and_feature_vector(clf, word_vectorizer, target_content)
            print("TARGET Content:")
            print(target_category)
            print(type(predicted_category))
            # Fetch the records from MongoDB database which matches the predicted category 
            matching_records = collection.find({'_id': {'$ne': ObjectId(userId)}, 'category': str(predicted_category)})
            # Extract all the feature vectors from matching records
            all_feature_vectors = [np.array(record['feature_vectors']) for record in matching_records]
            matching_records = collection.find({'_id': {'$ne': ObjectId(userId)}, 'category': str(predicted_category)})
            # Fetch the ID's from the matching records
            ids = [record['_id'] for record in matching_records] 
            print(len(all_feature_vectors))
            # Add the predicted feature vector for the new resume 
            all_feature_vectors.append(feature_vector)
            # Get the new ranks
            ranks = rank_predict(all_feature_vectors, target_feature_vector)
            ranks_dict = dict(ranks)
            print(ranks_dict)
            # Update the new ranks for all the matching records
            for i in range(0,len(ids)):
                print("here in loop")
                collection.update_one({'_id':ids[i]},{'$set':{'rank':str(ranks_dict.get(i))}})    
            index = max(ranks_dict.keys())
            print("type of feature vector",type(feature_vector))
            # Update the category and feature vectors value for the new resume in MongoDB
            data =  {
                'category':str(predicted_category),
                'feature_vectors':feature_vector.tolist()
            }
            query = {'_id': ObjectId(userId), 'rank': {'$exists': True}}
            collection.update_one({'_id':ObjectId(userId)},{'$set':{'rank':str(ranks_dict.get(index))}})
            print(userId)
            result = collection.update_one({'_id': ObjectId(userId)}, {'$set': data})
            # Return the predicted category and userid 
            result = {
            'predicted_category': int(predicted_category),
            'userId':userId}
            return jsonify(result), 200
        else:
            return jsonify({"error": "Invalid file format. Please upload a PDF file.str{e}"}), 400
    except Exception as e:
        logging.error(f'Exception occurred: {str(e)}')
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500  

# API for creating new user
@app.route('/newuser', methods=['POST'])
def create_user():
    try:
        # Get data from the request
        data = request.json
        # Extract user information
        user_name = data.get('user_name')
        password = data.get('password')
        contact_info = data.get('contact_info')
        user = data.get('user')
        # By default rank will be 999 and category will be set to 25
        rank = '999'
        category = '25'
        feature_vectors = []
        interest = []
        # Validate required fields
        if not user_name or not password or not contact_info:
            return jsonify({'message': 'Missing required fields'}), 400
        # Create a new user document
        user_document = {
            'user_name': user_name,
            'password': password,
            'contact_info': contact_info,
            'rank': rank,
            'category':category,
            'feature_vectors': feature_vectors,
            'user': user,
            'interest':interest
        }
        # Insert the user document into the MongoDB collection
        user_id = collection.insert_one(user_document).inserted_id
        return jsonify({'user_id': str(user_id)}), 201
    except Exception as e:
        print(f"Error creating user: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    
# API for User/Candidate login
@app.route('/users/login', methods=['POST'])
def login_user():
    try:
        # Get user_name and password from request data
        user_name = request.json.get('user_name')
        password = request.json.get('password')
        # Retrieve user data by user_name
        user_data = collection.find_one({'user_name': user_name, 'password': password, 'user':'candidate'})
        if user_data:
            # Convert ObjectId to string for JSON serialization
            user_data['_id'] = str(user_data['_id'])
            response_data = {
                '_id':user_data['_id'],
                'user_name':user_name
            }
            return jsonify(response_data)
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Error logging in user: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

# API for Recruiter Login
@app.route('/users/recruiter-login', methods=['POST'])
def recruiter_login():
    try:
        # Get user_name and password from request data
        user_name = request.json.get('user_name')
        password = request.json.get('password')
        # Retrieve user data by user_name
        user_data = collection.find_one({'user_name': user_name, 'password': password, 'user':'recruiter'})
        if user_data:
            # Convert ObjectId to string for JSON serialization
            user_data['_id'] = str(user_data['_id'])
            response_data = {
                '_id':user_data['_id'],
                'user_name':user_name
            }
            return jsonify(response_data)
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Error logging in user: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

# API for getting user data
@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        # Convert user_id to ObjectId
        user_object_id = ObjectId(user_id)
        # Retrieve user data by user_id
        user_data = collection.find_one({'_id': user_object_id})
        if user_data:
            # Convert ObjectId to string for JSON serialization
            user_data['_id'] = str(user_data['_id'])
            return jsonify(user_data)
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    
# API for updating the user details 
@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    result = collection.update_one({'_id': ObjectId(user_id)}, {'$set': data})
    if result.modified_count > 0:
        return jsonify({'message': 'User updated successfully'})
    else:
        return jsonify({'message': 'User not found'}), 404

# API for deleting the user 
@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = collection.delete_one({'_id': ObjectId(user_id)})
    if result.deleted_count > 0:
        return jsonify({'message': 'User deleted successfully'})
    else:
        return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
