from flask import Flask, request,session, render_template,redirect, current_app as app
from flask_paginate import Pagination, get_page_args

from config import TOKEN,PER_PAGE
from main import get_data
from logger import setup_logger


Token = os.environ.get('TOKEN')
if Token == '':
	Token = TOKEN

	
app = Flask(__name__)
app.secret_key = TOKEN

accesslogger = setup_logger('app','Logs/accesslog.log')

def process_data():
	page = int(request.args.get('page', 1))
	per_page = PER_PAGE
	offset = (page - 1) * per_page
	data = get_data(org_name=session['org_name'],repo_count=session['repo_count'],committees=session['committees'],per_page=per_page,offset=offset)
	total = data['count']
	pagination = Pagination(page=page, per_page=per_page, total=total,css_framework='bootstrap4',error_out=False)

	return (data,page,per_page,pagination) 

@app.route('/',methods=['POST', 'GET'])
def home():
	if 'flag' in session and session['flag'] == True and 'page' in request.args:

		data,page,per_page,pagination = process_data()
		max_page = pagination.pages[-1] 
		if page > max_page :
			return redirect(f'/?page={max_page}')

		return render_template(
	    	'index.html',
	    	data=data,
	    	page=page,
	    	per_page=per_page,
	    	pagination=pagination
			)

	if request.method == 'POST':
		
		session['flag'] = True
		session['org_name'] = request.form.get('org_name', type=str)
		session['repo_count'] = request.form.get('repo_count', default = 5, type=int)
		session['committees'] = request.form.get('contri_count', default = 3, type=int)

		data,page,per_page,pagination = process_data()

		accesslogger.info(f"org_name - {session['org_name']} \t repo_count - {session['repo_count']} \t committees - {session['committees']}")

		return render_template(
			'index.html',
			data=data,
			page=page,
			per_page=per_page,
			pagination=pagination
			)
	session.clear()
	try:
		header = dict(request.headers)
	except:
		header = {}

	accesslogger.info(f"client - {header.get('X-Forwarded-For','') }")
	accesslogger.info(f"user agent - {header.get('User-Agent','') }")
	
	data =None
	return render_template(
		'index.html',
		data=data,
		)


@app.errorhandler(404)
def page_not_found(e):
	header = dict(request.headers)

	accesslogger.info(f"client - {header.get('X-Forwarded-For','')} ")
	accesslogger.info(f"user agent - {header.get('User-Agent','') }")
	accesslogger.warning(f"user accessed - {request.url}")

	return render_template('error/404.html')


@app.errorhandler(500)
def server_error(e):

	header = dict(request.headers)
	
	accesslogger.info(f"client - {header.get('X-Forwarded-For','')} ")
	accesslogger.info(f"user agent - {header.get('User-Agent','') }")
	accesslogger.warning(f"user accessed - {request.url}")

	return render_template('error/500.html')



if __name__ == '__main__':
    app.run(debug=True)
    # app.run()