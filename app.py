from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime
from googlesearch import search


app=Flask(__name__)

#MySQL connection
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= 'Pamagon2000*'
app.config['MYSQL_DB']= 'searchemtool'

conection = MySQL(app)


#Defining routes (aka barritas de la url)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=["POST", "GET"])
def results():
    mol = request.form.get("search")
    agonist = request.form.get("agonsit")
    antagonist = request.form.get("antagonist")
    fisher = request.form.get("fisher")
    selleckchem = request.form.get("selleckchem")
    sigma = request.form.get("sigma")
    type = request.form.get("type")
    data={}
    role=[]
    brands=[] 
    
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
            counter += 1

        data['message']=activity
    except Exception as ex:
        data['message']=''
    return render_template('output.html', mol=data, brands=brands)


@app.route('/<user>', methods=["POST", "GET"])
def user(user):
    return render_template('user.html', name=user)

@app.route('/<user>/result', methods=["POST", "GET"])
def result(user):
    mol = request.form.get("search_user")
    agonist = request.form.get("agonsit")
    antagonist = request.form.get("antagonist")
    fisher = request.form.get("fisher")
    selleckchem = request.form.get("selleckchem")
    sigma = request.form.get("sigma")
    type = request.form.get("type")
    data={}
    role=[]
    brands=[] 
    
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
            counter += 1

        data['message']=activity
    except Exception as ex:
        data['message']=''
    return render_template('output_user.html', name=user, mol=data, brands=brands)


@app.route('/<user>/favourites', methods=["POST", "GET"])
def favourites(user):
    return render_template('favourites.html', name=user)




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
