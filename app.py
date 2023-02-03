from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL


app=Flask(__name__)

#MySQL connection
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= 'Pamagon2000*'
app.config['MYSQL_DB']= 'chembl_31'

conection = MySQL(app)


#Defining routes (aka barritas de la url)
@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/activity')
def activity():
    data={}
    try:
        cursor=conection.connection.cursor()
        sql="SELECT activity_id FROM activities WHERE activity_id='31863';"
        cursor.execute(sql)
        activity=cursor.fetchall()
        cursor.close()
        data['activity']=activity
        data['message']='Well done!'
    except Exception as ex:
        data['message']='Error...'
    return jsonify(data)

def query_string():
    print(request)
    print(request.args)
    print(request.args.get('param1'))
    return "OK"


if __name__=='__main__':
    app.add_url_rule('/query_string', view_func=query_string)
    app.register_error_handler(404, page_not_found)
    app.run(debug=True,port=5000)