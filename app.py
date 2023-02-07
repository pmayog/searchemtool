from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime


app=Flask(__name__)

#MySQL connection
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= 'Pamagon2000*'
app.config['MYSQL_DB']= 'information_schema'

conection = MySQL(app)


#Defining routes (aka barritas de la url)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=["POST", "GET"])
def results():
    search = request.form.get("search")
    #search="no"
    #agonist = request.form.get("agonsit")
    #antagonist = request.form.get("antagonist")
    #fisher = request.form.get("fisher")
    #selleckchem = request.form.get("selleckchem")
    #sigma = request.form.get("sigma")
    data={}
    try:
        cursor=conection.connection.cursor()
        sql="SELECT privilege_type FROM user_privileges WHERE is_grantable='"+search+"';"
        cursor.execute(sql)
        activity=cursor.fetchall()
        cursor.close()
        data['message']=activity
    except Exception as ex:
        #error=No results found'
        data['message']='no_result'
        #print(len(data.get('message')))
    return render_template('output.html', search=data)

@app.route('/user/<username>/favourites')
def favourites(username):
    return render_template('favourites.html', name=username)

@app.route('/user/<username>')
def user(username):
    return render_template('user.html', name=username)

def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/signin')
def signin():
    return render_template('sign_in.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/presentations')
def presentations():
    return render_template('presentations.html')

def query_string():
    print(request)
    print(request.args)
    print(request.args.get('param1'))
    return "OK"


if __name__=='__main__':
    app.add_url_rule('/query_string', view_func=query_string)
    app.register_error_handler(404, page_not_found)
    app.run(debug=True,port=5000)
