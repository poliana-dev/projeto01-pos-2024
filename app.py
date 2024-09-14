from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
from view.main import oauthRegister, User
from datetime import date
import os

app = Flask(__name__)
app.debug = True
app.secret_key = os.getenv('SECRET_KEY')  
oauth = OAuth(app)

# config para integração com o SUAP
oauthRegister(oauth, 
              name="suap", 
              api_base_url="https://suap.ifrn.edu.br/api/", 
              request_token_url=None, 
              access_token_method="POST", 
              access_token_url="https://suap.ifrn.edu.br/o/token/", 
              authorize_url="https://suap.ifrn.edu.br/o/authorize/",
              logout_url = 'https://suap.ifrn.edu.br/o/logout/',
              token="suap_token")


@app.route('/')
def index():
    if 'suap_token' in session:
        user = User(oauth)
        user_data = user.UserDados()
        data = {"user_data": user_data.json()}
        return render_template('user.html', data=data)
    else:
        return render_template('index.html')

@app.route("/boletim", methods=["GET"])
def boletim():
    ano_atual = date.today().year
    user = User(oauth)
    user_data = user.UserDados()
    data = {
        "user_data": user_data.json(),
        "anos_letivos": [ano_atual - i for i in range(4)],  # Últimos 4 anos
    }

    # Verifica se o ano letivo foi selecionado
    if request.args.get('ano_letivo'):
        ano_letivo = int(request.args.get('ano_letivo'))
        boletim = user.UserBoletim(ano_letivo)
        data["boletim"] = boletim.json()

    return render_template("boletim.html", data=data)

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.suap.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    session.pop('suap_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def auth():
    token = oauth.suap.authorize_access_token()
    session['suap_token'] = token
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()

