import flask

import google.oauth2.credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow

app = flask.Flask(__name__)
app.secret_key = '***REPLACE - value here used as placeholder'

CLIENT_SECRET = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/yt-analytics-monetary.readonly']

args = {
	'onBehalfOfContentOwner': '***REPLACE - ID of content owner', 
	'includeSystemManaged': True
}

def creds_to_dict(creds):
	return {
		'token': creds.token,
		'refresh_token': creds.refresh_token,
		'token_uri': creds.token_uri,
		'client_id': creds.client_id,
		'client_secret': creds.client_secret,
		'scopes': creds.scopes
	}

@app.route('/')
def index():
	if 'credentials' not in flask.session:
		return flask.redirect(flask.url_for('oauth2callback'))
	creds = flask.session['credentials']
	credentials = google.oauth2.credentials.Credentials(**creds)

	youtube = build('youtubereporting', 'v1', credentials=credentials)
	results = youtube.reportTypes().list(**args).execute()
	return flask.jsonify(results)

@app.route('/callback')
def oauth2callback():
	flow = Flow.from_client_secrets_file(
		CLIENT_SECRET,
		scopes=SCOPES,
		redirect_uri=flask.url_for(
			'oauth2callback',
			_external=True
	))
	if 'code' not in flask.request.args:
		auth_url, state = flow.authorization_url(
			access_type="offline",
			include_granted_scopes='true'
		)
		flask.session['state'] = state
		return flask.redirect(auth_url)
	else:
		state = flask.session['state']
		flow.state = state

		auth_code = flask.request.args.get('code')
		flow.fetch_token(code=auth_code)
		credentials = flow.credentials

		flask.session['credentials'] = creds_to_dict(credentials)
		return flask.redirect(flask.url_for('index'))

@app.route('/clear_session')
def clear_session():
	flask.session.clear()
	return flask.redirect(flask.url_for('index'))
