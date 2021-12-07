from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

host = os.environ.get("DB_URL")
client = MongoClient(host=host)
db = client.get_default_database()
donations = db.donations
charities = db.charities


app = Flask(__name__)

# get info hompage donations from index
@app.route('/')
def donations_index():
  return render_template('donations_index.html', donations=donations.find())

# shows a specific donation
@app.route('/donations/<donation_id>')
def donation_show_one(donation_id):
  donation = donations.find_one({'_id': ObjectId(donation_id)})
  return render_template('donation_show_one.html', donation=donation)

# page that adds new donation
@app.route('/donations/new')
def track_donation():
  donation = {}
  return render_template('donations_new.html', title='New Donation', donation=donation, charities=charities.find()) 

# create or submit donation
@app.route('/donations', methods=['POST'])
def donation_submit():
  donation = {
    'charity_name': request.form.get('charity_name').title(),
    'donation_amount': request.form.get('donation_amount'),
    'date_donated': request.form.get('date_donated'),
  }
  donations.insert_one(donation)

  create_new_charity(donation)

  return redirect(url_for('donations_index'))

# edit charity form
@app.route('/donations/<donation_id>/edit')
def donation_edit_page(donation_id):
  donation = donations.find_one({'_id': ObjectId(donation_id)})
  return render_template('donations_edit.html', donation=donation, title='Edit Donation', charities=charities.find())

# update a donation
@app.route('/donations/<donation_id>', methods=['POST'])
def donation_update(donation_id):
  updated_donation = {
    'charity_name': request.form.get('charity_name').title(),
    'donation_amount': request.form.get('donation_amount'),
    'date_donated': request.form.get('date_donated'),
  }
  donations.update_one(
    {'_id': ObjectId(donation_id)},
    {'$set': updated_donation}
  )
  create_new_charity(updated_donation)

  return redirect(url_for('donations_index'))

# delete donation
@app.route('/donations/<donation_id>/delete')
def donations_delete(donation_id):
  donations.delete_one({'_id': ObjectId(donation_id)})
  return redirect(url_for('donations_index'))

#  new charity
def create_new_charity(donation):

  existing_charity = charities.find_one({'name': donation['charity_name']})
  if not existing_charity:
    charity = {
      'name': donation['charity_name'],
      'category': '',
      'about': '',
    }
    charities.insert_one(charity)

# profile page
@app.route('/profile')
def donor_profile():
  total_donated = 0
  for donation in donations.find():
    total_donated += int(donation['donation_amount'])
  print(total_donated)

  user = {
    'name': 'Jeremy Gonzales',
    'total_donated': total_donated,
    'charities_donated_to': donations.find()
  }
  return render_template('profile.html', user=user, donations=donations.find(), charities=charities.find())

# update charity info
@app.route('/charities/<charity_name>', methods=['POST'])
def charities_update(charity_name):
  updated_charity = {
    'name': request.form.get('charity_name'),
    'category': request.form.get('charity_category'),
    'about': request.form.get('about_charity')
  }
  charities.update_one(
    {'name': charity_name},
    {'$set': updated_charity}
  )
  return redirect(url_for('charity_profile', charity_name=updated_charity['name']))

# delete charity
@app.route('/charities/<charity_name>/delete')
def charity_delete(charity_name):
  print(charity_name)
  charities.delete_one({'name': charity_name})
  return redirect(url_for('AllCharities'))

@app.route('/login', methods=['POST'])
def login():
  user = {
    'email': request.form.get('email'),
    'password': request.form.get('password')
  }
  print(user)
  return render_template('donations_new.html')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))

