import requests,os

from models import Repository, Contributor
from logger import setup_logger
from config import TOKEN

errorlogger = setup_logger('Main','errorlog.log')

Token = os.environ.get('TOKEN')
if Token == '':
	Token = TOKEN

	
headers = {
    "Authorization": "Token " + Token
}
# print(headers)

def get_repository_committee(organisation_name, repo_name, committees):
	url = f'https://api.github.com/repos/{organisation_name}/{repo_name}/stats/contributors'

	content = requests.get(url = url , headers=headers)
	all_author_data = []
	# print(content.text)
	try:
		content = content.json()
	except Exception as e :
		# errorlogger.warning(f'Error on Json extraction- {e}')
		# NO Data 
		return []

	if isinstance(content,dict) and 'message' in content.keys():
		# Data Not accessible
		return []

	for record in content:
		if 'author' not in record.keys() or record.get('author',None) == None:
			# No Data about commiters
			continue

		all_author_data.append(Contributor(record['author']['login'],record['author']['html_url'],record['total']))


	all_author_data = all_author_data[::-1]
	min_val = min(len(all_author_data),committees)

	return all_author_data[:min_val]


def get_organisation_repository(organisation_name, repo_count, committees,per_page,offset):
	url = 'https://api.github.com/search/repositories'

	organisation_query = f'org:{organisation_name}'

	parameters = {
		'q': organisation_query,
		'sort':'forks',
		'order':'desc',
		'per_page':repo_count
		}

	content = requests.get(url = url , params=parameters,headers=headers).json()
	# print(content)

	# Invalid Organisation 
	if 'message' in content.keys() or len(content['items']) == 0 :
		data = {
			'status' : 'Failed',
			'count' :0, 
			'message' : f'No data Found '
		}
		

		return data

	data = {
		'status':'Success',
		'data':[],
		'count' : len(content['items'])
	}

	low = min(repo_count,offset)
	high = min(repo_count,per_page+offset)
	
	for record in content['items'][low:high]:
		# print(record['name'])

		contributor = get_repository_committee(organisation_name = organisation_name, 
				repo_name = record['name'], 
				committees = committees
				)

		data['data'].append( Repository(record['name'], record['html_url'], record['forks'],contributor))

	return data

def get_data(org_name, repo_count, committees,per_page,offset):

	data = get_organisation_repository(organisation_name=org_name, repo_count=repo_count, committees=committees,per_page=per_page,offset=offset)
	print(data)

	return data


