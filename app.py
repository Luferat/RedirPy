from flask import Flask, render_template, request
from datetime import datetime, timedelta
from flask_mysqldb import MySQL


app = Flask(__name__)

# Configurações de acesso ao MySQL
app.config['MYSQL_HOST'] = 'localhost'              # Servidor do MySQL
app.config['MYSQL_USER'] = 'root'                   # Usuário do MySQL
app.config['MYSQL_PASSWORD'] = ''                   # Senha do MySQL
app.config['MYSQL_DB'] = 'redirpydb'                # Nome da base de dados
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'      # Retorna dados como DICT
app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'    # CRUD em UTF-8


# Variável de conexão com o MySQL
mysql = MySQL(app)


# Configura a conexão com o MySQL para usar utf8mb4 e português do Brasil
@app.before_request
def before_request():
    cur = mysql.connection.cursor()
    cur.execute("SET NAMES utf8mb4")                    # MySQL com UTF-8
    cur.execute("SET character_set_connection=utf8mb4")  # MySQL com UTF-8
    cur.execute("SET character_set_client=utf8mb4")     # MySQL com UTF-8
    cur.execute("SET character_set_results=utf8mb4")    # MySQL com UTF-8
    # dias da semana e meses em PT-BR
    cur.execute("SET lc_time_names = 'pt_BR'")
    cur.close()


@app.route('/<short>')
def home(short):
    return f"Vamos para {short}"


@app.route('/edit/<id>')
def edit(id):
    return f'Editando {id}'


@app.route('/admin')
def admin():
    return 'Listando todo mundo'


@app.route('/new', methods=['GET', 'POST'])
def new():

    sended = False
    error = False

    if request.method == 'POST':  # Processa formulário enviado
        form = dict(request.form)

        # print('\n\n\n', form, '\n\n\n')

        sql = '''
            SELECT COUNT(id) AS total FROM redir
            WHERE (name = %s OR short = %s)
                AND status = 'on' AND expire > NOW();
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (form['name'], form['short'],))
        total = int(cur.fetchone())

        # BUG HERE
        # print('\n\n\n', total['total'], '\n\n\n')

        if total > 0:
            error = True

        else:

            sql = '''
                INSERT INTO redir (
                    name, link, short, expire
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s
                )
            '''            
            cur.execute(sql, (form['name'], form['link'], form['short'], form['expire'],))
            mysql.connection.commit()
        
        cur.close()

        sended = True

    data_atual = datetime.now()                             # Data atual
    data_futura = data_atual + timedelta(days=365)          # Adicionando 1 ano
    one_year = data_futura.strftime("%Y-%m-%d %H:%M:%S")    # Formatando a data

    page = {
        'expire_sugest': one_year,
        'sended': sended,
        'error': error
    }

    return render_template('new.html', page=page)


@app.route('/about')
def about():
    return 'Sobre...'


@app.errorhandler(404)
def page_not_found(e):
    return 'Oooops! Erro 404', 404


if __name__ == '__main__':
    app.run(debug=True)
