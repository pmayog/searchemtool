from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt
from datetime import datetime, timedelta
from googlesearch import search
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import NotFound


app=Flask(__name__)

#MySQL connection
app.config['MYSQL_HOST']= 'searchemtool'
app.config['MYSQL_USER']= 'searchemtool'
app.config['MYSQL_PASSWORD']= 'dbw2o23'
app.config['MYSQL_DB']= 'searchemtool'
app.config['SECRET_KEY']='pedrosehacaido'
app.config['PERMANENT_SESSION_LIFETIME']=timedelta(minutes=30)

hostedApp=Flask(__name__)

#MySQL connection
hostedApp.config['MYSQL_HOST']= 'searchemtool'
hostedApp.config['MYSQL_USER']= 'searchemtool'
hostedApp.config['MYSQL_PASSWORD']= 'dbw2o23'
hostedApp.config['MYSQL_DB']= 'searchemtool'
hostedApp.config['SECRET_KEY']='pedrosehacaido'
hostedApp.config['PERMANENT_SESSION_LIFETIME']=timedelta(minutes=30)



global COOKIE_TIME_OUT  

conection = MySQL(app)

COOKIE_TIME_OUT=(60*30)
    


#Defining routes (aka barritas de la url)
@app.route('/')
def index():
    print(session, len(session))
    session.pop('_flasher', None)
    if len(session)!=0:
        print('hello')
        session.clear

    return render_template('index.html')

@app.route('/results', methods=["POST", "GET"])
def results():
    session.pop('_flasher', None)
    mol = request.form.get("search")
    agonist = request.form.get("agonsit")
    antagonist = request.form.get("antagonist")
    fisher = request.form.get("fisher")
    selleckchem = request.form.get("selleckchem")
    sigma = request.form.get("sigma")
    type = request.form.get("type")
    session['type'] = type
    data={}
    role=[]
    brands=[] 
    
    if 'email' in session or 'username' in session:
       session.clear
    
    if agonist == 'on':
        role.append ('AGONIST')
    if antagonist == 'on':
        role.append('ANTAGONIST')

    if fisher == 'on':
        brands.append ('Fisher Scientific')
    if selleckchem == 'on':
        brands.append('Selleckchem')
    if sigma == 'on':
        brands.append ('Sigma-Aldrich')

    if len(brands)== 0:
        brands.extend(['Fisher Scientific','Selleckchem','Sigma-Aldrich'])

    try:
           
        if type =='molecule' or type==None:
            if len(role)==0 or len(role)==2:
                sql="select distinct m.chembl_id,m.name,t.uniprot_id,t.protein_name,tm.type_of_activity FROM molecule m, target t, target_has_molecule tm WHERE m.chembl_id=tm.molecule_chembl_id AND t.uniprot_id=tm.target_uniprot_id AND tm.target_uniprot_id = (select target_uniprot_id from target_has_molecule where molecule_chembl_id=(select chembl_id from molecule where name='%s'));" %(mol)
            else:
                sql="select distinct m.chembl_id,m.name,t.uniprot_id,t.protein_name,tm.type_of_activity FROM molecule m, target t, target_has_molecule tm WHERE m.chembl_id=tm.molecule_chembl_id AND t.uniprot_id=tm.target_uniprot_id AND tm.target_uniprot_id = (select target_uniprot_id from target_has_molecule where molecule_chembl_id=(select chembl_id from molecule where name='%s')) AND tm.type_of_activity='%s';" %(mol,role[0])       
        if type=='target':
            if len(role)==0 or len(role)==2:
                sql="select distinct m.chembl_id,m.name,t.uniprot_id,t.protein_name,tm.type_of_activity FROM molecule m, target t, target_has_molecule tm WHERE m.chembl_id=tm.molecule_chembl_id AND t.uniprot_id=tm.target_uniprot_id AND t.protein_name='%s';" %(mol)
            else:
                sql="select distinct m.chembl_id,m.name,t.uniprot_id,t.protein_name,tm.type_of_activity FROM molecule m, target t, target_has_molecule tm WHERE m.chembl_id=tm.molecule_chembl_id AND t.uniprot_id=tm.target_uniprot_id AND t.protein_name='%s' AND tm.type_of_activity='%s';" %(mol,role[0])
        
        cursor=conection.connection.cursor() 
        cursor.execute(sql)
        activity=cursor.fetchall()
        activity=[list(x) for x in activity]
        cursor.close()
        print(activity)
        
        counter=0
        for a in activity :
            for b in brands:
                query = a[1]+" "+b
                for result in search(query, tld="co.in", num=1, stop=1, pause=2):
                    link = result
                    activity[counter].append(link)
            counter += 1
        data['message']=activity
    except Exception as ex:
        data['message']=''
    return render_template('output.html', mol=data, brands=brands)


@app.route('/<user>', methods=["POST", 'GET'])
def user(user):
    if len(session)==0:
        print(session)
        return redirect(url_for('index'))
    elif session['username']==user:
        return render_template('user.html', name=user)
    else:
        return render_template('404.html'), 404

@app.route('/<user>/result', methods=["POST", "GET"])
def result(user):
    mol = request.form.get("search_user")
    agonist = request.form.get("agonsit")
    antagonist = request.form.get("antagonist")
    fisher = request.form.get("fisher")
    selleckchem = request.form.get("selleckchem")
    sigma = request.form.get("sigma")
    type = request.form.get("type")
    session['type'] = type
    data={}
    role=[]
    brands=[] 
    
    if len(session)==0:
        return redirect(url_for('index'))
    elif session['username']!=user:
        return render_template('404.html'), 404
    else:
        
        if agonist == 'on':
            role.append ('AGONIST')
        if antagonist == 'on':
            role.append('ANTAGONIST')

        if fisher == 'on':
            brands.append ('Fisher Scientific')
        if selleckchem == 'on':
            brands.append('Selleckchem')
        if sigma == 'on':
            brands.append ('Sigma-Aldrich')

        if len(brands)== 0:
            brands.extend(['Fisher Scientific','Selleckchem','Sigma-Aldrich'])

        try:
            
            if type =='molecule' or type==None:
                if len(role)==0 or len(role)==2:
                    sql="select distinct m.chembl_id,m.name,t.uniprot_id,t.protein_name,tm.type_of_activity FROM molecule m, target t, target_has_molecule tm WHERE m.chembl_id=tm.molecule_chembl_id AND t.uniprot_id=tm.target_uniprot_id AND tm.target_uniprot_id = (select target_uniprot_id from target_has_molecule where molecule_chembl_id=(select chembl_id from molecule where name='%s'));" %(mol)
                else:
                    sql="select distinct m.chembl_id,m.name,t.uniprot_id,t.protein_name,tm.type_of_activity FROM molecule m, target t, target_has_molecule tm WHERE m.chembl_id=tm.molecule_chembl_id AND t.uniprot_id=tm.target_uniprot_id AND tm.target_uniprot_id = (select target_uniprot_id from target_has_molecule where molecule_chembl_id=(select chembl_id from molecule where name='%s')) AND tm.type_of_activity='%s';" %(mol,role[0])      
            if type=='target':
                if len(role)==0 or len(role)==2:
                    sql="select distinct m.chembl_id,m.name,t.uniprot_id,t.protein_name,tm.type_of_activity FROM molecule m, target t, target_has_molecule tm WHERE m.chembl_id=tm.molecule_chembl_id AND t.uniprot_id=tm.target_uniprot_id AND t.protein_name='%s';" %(mol)
                else:
                    sql="select distinct m.chembl_id,m.name,t.uniprot_id,t.protein_name,tm.type_of_activity FROM molecule m, target t, target_has_molecule tm WHERE m.chembl_id=tm.molecule_chembl_id AND t.uniprot_id=tm.target_uniprot_id AND t.protein_name='%s' AND tm.type_of_activity='%s';" %(mol,role[0])
            
            cursor=conection.connection.cursor() 
            cursor.execute(sql)
            activity=cursor.fetchall()
            activity=[list(x) for x in activity]
            cursor.close()
            
            counter=0
            for a in activity :
                for b in brands:
                    query = a[1]+" "+b
                    for result in search(query, tld="co.in", num=1, stop=1, pause=2):
                        link = result
                        activity[counter].append(link)
                activity[counter].append('favourite'+str(counter))
                counter += 1
            data['message']=activity
            session['output']=activity
        except Exception as ex:
            data['message']=''
        return render_template('output_user.html', name=user, mol=data, brands=brands)

@app.route('/<user>/favourites', methods=["POST", "GET"])
def favourites(user):
    if len(session)==0:
        return redirect(url_for('index'))
    elif session['username']!=user:
        return render_template('404.html'), 404
    else:
        sql="select um.molecule_chembl_id FROM user_has_molecule um WHERE um.user_user_id=\'%s\';" %(session['username'])
        cursor=conection.connection.cursor() 
        cursor.execute(sql)
        favourites_mol=cursor.fetchall()
        sql="select ut.target_uniprot_id FROM user_has_target ut WHERE ut.user_user_id=\'%s\';" %(session['username'])
        cursor=conection.connection.cursor() 
        cursor.execute(sql)
        favourites_tar=cursor.fetchall()
        cursor.close()

        favourites = []
        if favourites_mol:
            for mol in favourites_mol:
                sql="select m.name, m.chembl_id, m.type FROM molecule m WHERE m.chembl_id=\'%s\';" %(mol)
                cursor=conection.connection.cursor() 
                cursor.execute(sql)
                info_mol=cursor.fetchall()
                info_mol=[list(x) for x in info_mol]
                favourites.append(info_mol)
        if favourites_tar:
            for tar in favourites_tar:
                sql="select t.protein_name, t.uniprot_id, t.organism_taxa_id FROM target t WHERE t.uniprot_id=\'%s\';" %(tar)
                cursor=conection.connection.cursor() 
                cursor.execute(sql)
                info_tar=cursor.fetchall()
                info_tar=[list(x) for x in info_tar]
                favourites.append(info_tar)
        session['favs']=favourites
        print(session['favs'])
        return render_template('favourites.html', name=user, favs=favourites)




def page_not_found(error):
    return render_template('404.html'), 404

def method_not_allowed(error):
    return render_template('404.html'), 405

@app.route('/signin', methods=['GET','POST'])
def signin():
    if request.method == 'GET':
        return render_template('sign_in.html')
    else:

        username_email="'"+request.form['enter']+"'"
        password="'"+request.form['password']+"'"

        sql='SELECT * FROM user WHERE (user.user_id=%s OR user.email=%s) AND (user.password=%s);' %(username_email,username_email, password)
        cur= conection.connection.cursor()
        cur.execute(sql)
        user_info=cur.fetchone()
        cur.close

        if user_info==None:
            conection.connection.Error
            flash('Incorrect User/email or password')
            return render_template('sign_in.html')
        else:
            session['username']= user_info[0]
            session['email']= user_info[3]
            return redirect(url_for('user', user=session['username']))
         
        
        

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/favourites_checkboxes/<info>')
def fav_checkbox(info):
    try:
        brands=['Fisher Scientific','Selleckchem','Sigma-Aldrich']
        print(info)
        print('helo')
        for i in range(0,len(session['output']),1):
            print(i)
            if session['output'][i][-1] == info:
                username = session['username']
                molecule_id = session['output'][i][0]
                target_id = session['output'][i][2]
                favourite = 'yes'
                if session['type'] == 'molecule' or session['type']==None:
                    sql='INSERT INTO user_has_molecule (user_user_id, molecule_chembl_id, favourite) VALUES (\'%s\',\'%s\',\'%s\');' %(username,molecule_id,favourite)
                    cur=conection.connection.cursor()
                    cur.execute(sql)
                    conection.connection.commit()
                if session['type'] == 'target':
                    sql='INSERT INTO user_has_target (user_user_id, target_uniprot_id, favourite) VALUES (\'%s\',\'%s\',\'%s\');' %(username,target_id,favourite)
                    cur=conection.connection.cursor()
                    cur.execute(sql)
                    conection.connection.commit()
        print('hi')
    except Exception:
        pass
    return redirect(url_for('favourites', user=session['username']))

@app.route('/del_checkboxes/<info>')
def del_checkbox(info):
    if 'CHEMBL' in info:
        sql='DELETE FROM user_has_molecule WHERE user_has_molecule.molecule_chembl_id=\'%s\';' %(info)
        cur=conection.connection.cursor()
        cur.execute(sql)
        conection.connection.commit()
    else:
        sql='DELETE FROM user_has_target WHERE user_has_target.target_uniprot_id=\'%s\';' %(info)
        cur=conection.connection.cursor()
        cur.execute(sql)
        conection.connection.commit()
    return redirect(url_for('favourites', user=session['username']))



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        try:
            firstname="'"+request.form['firstname']+"'"
            lastname="'"+request.form['lastname']+"'"
            username="'"+request.form['username']+"'"
            email="'"+request.form['email']+"'"
            password="'"+request.form['password']+"'"

            if len(firstname)==2 or len(lastname)==2 or len(username)==2 or len(email)==2 or len(password)==2:
                flash('Sorry, all fields are mandatory')
                return render_template('signup.html')
                
            
            else:
                '''
                try:
                    sql='SELECT email FROM user WHERE user.email=%s' %(email)
                    cur= conection.connection.cursor()
                    err=conection.connection.Error
                    cur.execute(sql)
                    new_email=cur.fetchone()
                    cur.close
                    flash('Sorry, email address or username already exists')
                    return render_template('signup.html')

            '''
                try:
                    sql='INSERT INTO user (user_id, first_name, last_name, email, password) VALUES (%s,%s,%s,%s,%s);' %(username,firstname,lastname,email,password)
                    cur=conection.connection.cursor()
                    err2=conection.connection.Error
                    cur.execute(sql)
                    conection.connection.commit()
                    session['username']=username[1:-1]
                    session['email']=email[1:-1]
                    return redirect(url_for('user', user=username[1:-1]))
                except Exception:
                    pass
                
        
        except Exception:
            flash('Sorry, email address or username already exists')
            return render_template('signup.html')


@app.route('/presentations')
def presentations():
    return render_template('presentations.html')

def query_string():
    print(request)
    print(request.args)
    print(request.args.get('param1'))
    return "OK"


hostedApp.wsgi_app = DispatcherMiddleware(NotFound(), {f"/u218065/searchemtool":app})


if __name__=='__main__':
    hostedApp.add_url_rule('/query_string', view_func=query_string)
    hostedApp.register_error_handler(404, page_not_found)
    hostedApp.register_error_handler(405, method_not_allowed)
    hostedApp.run(debug=True, port=5000)
