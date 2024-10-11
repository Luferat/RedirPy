from flask import Flask, render_template, request
from datetime import datetime, timedelta
from flask_mysqldb import MySQL

# Endereço raiz do shortlink
root_link = 'http://localhost:5000'


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


@app.route('/del/<id>')
def delete(id):
    return f'Apagando {id}'


@app.route('/admin')
def admin():

    sql = '''
        SELECT id, name, link, short, views,
            DATE_FORMAT(date, '%d/%m/%Y %H:%i') AS datebr,
            DATE_FORMAT(expire, '%d/%m/%Y %H:%i') AS expirebr
        FROM redir
        WHERE status = 'on'
        ORDER BY name, short, date DESC, expire DESC;
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql)
    shortlinks = cur.fetchall()
    cur.close()

    print('\n\n\n', shortlinks, '\n\n\n')

    page = {
        'root_link': root_link,
        'shortlinks': shortlinks
    }

    return render_template('admin.html', page=page)


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
        total = cur.fetchone()

        # print('\n\n\n', total['total'], '\n\n\n')

        if int(total['total']) > 0:
            error = True

        else:

            sql = '''
                INSERT INTO redir (name, link, short, expire)
                VALUES (%s, %s, %s, %s)
            '''
            cur.execute(sql, (form['name'], form['link'],
                        form['short'], form['expire'],))
            mysql.connection.commit()

            sended = True

        cur.close()

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
