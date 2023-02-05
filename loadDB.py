import pymysql
import sys 
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

#Database connection
database = "searchemtool";
host = "localhost";
user="root"; 
passwd = "Raqpp00*";

connection = pymysql.connect(host='localhost',
                user=user,
                password=passwd,
                db=database,
                charset='utf8mb4',
                autocommit=True
            )

## Turn off FKs
connection.cursor().execute("SET FOREIGN_KEY_CHECKS=0")

## Clean Tables !!
for tab in (
    'molecule', 'organism', 'target', 'target_has_molecule', 'provider', 
    'molecule_has_provider', 'user', 'user_has_molecule', 'user_has_target'):
    try:
        print("Cleaning {}".format(tab))
        connection.cursor().execute("DELETE FROM "+ tab)
    except OSError as e:
        sys.exit(e.msg)
    
        
for tab in  ('molecule', 'organism', 'target', 'target_has_molecule', 'provider',
             'molecule_has_provider'):
    connection.cursor().execute("ALTER TABLE " + tab + " AUTO_INCREMENT=1")

target_conversion = {}
with open ("chembl_uniprot_mapping.txt", 'r') as CHEMBLPDB:
    for line in CHEMBLPDB:
        line = line.strip()
        if line.startswith("#"):
            continue
        else: 
            fields = line.split("\t")
            uniprot_id = fields[0]
            chembl_id = fields[1]
            target_conversion[chembl_id] = uniprot_id

print ("Organisms...")
ORGANISMS = {9606 : 'Homo sapiens', 10090: 'Mus musculus', 9986 : 'Oryctolagus cuniculus',
                  10116 : 'Rattus norvegicus', 10141 : 'Cavia porcellus'}
organisms_list = list(ORGANISMS.keys())

sthOrganism = "INSERT INTO organism (taxa_id, scientific_name) VALUES (%s, %s)"
for organism in ORGANISMS: 
    organism_name = ORGANISMS[organism]
    with connection.cursor() as c:
        c.execute(sthOrganism, (organism, organism_name))

print("ok")
##
##
print ("Providers...")
PROVIDERS = {1 : 'Sigma Aldrich', 2: 'Fisher Scientific', 3 : 'Selleckchem'}

sthProvider = "INSERT INTO provider (provider_id, provider_name) VALUES (%s, %s)"
for provider in PROVIDERS: 
    provider_name = PROVIDERS[provider]
    with connection.cursor() as c:
        c.execute(sthProvider, (provider, provider_name))

print("ok")
##
##
print ("Targets...")

TARGETS = {}
sthTarget = "INSERT INTO target (uniprot_id, protein_name, organism_taxa_id) VALUES (%s, %s, %s)"
with open ("uniprot_sprot.dat", 'r') as SWISSPROT:
    for line in SWISSPROT:
        line = line.strip()
        if line.startswith("AC   "):
            line = line.rstrip(";")
            target = line.split("   ")[1].split(";")[0]
            target_name = ''
            target_organism = ''
        elif line.startswith("DE   RecName:"):
            line = line.rstrip(";")
            target_name = line.split("   ")[1].split("=")[1].split("{")[0]
        elif line.startswith("OX   "):
            line = line.rstrip(";")
            target_organism = int(line.split("   ")[1].split("=")[1].split("{")[0])
        else: 
            continue
        if target_name != '' and target_organism != '':
            if target_organism in organisms_list:
                if target not in TARGETS:
                    with connection.cursor() as c:
                        c.execute(sthTarget, (target, target_name, target_organism))
                        target_id = c.lastrowid
                        TARGETS[target] = target_id

print("ok")
##
##
print("Molecules...")

MOLECULES = {}
target_has_molecule = {}
sthMolecule = "INSERT INTO molecule (chembl_id, name, formula, type) VALUES (%s,%s,%s,%s)"
sthTargetMolecule = "INSERT INTO target_has_molecule (target_uniprot_id, molecule_chembl_id, reference_id, type_of_activity) VALUES (%s,%s,%s,%s)"
with open ("chembl_31.sdf", 'r') as CHEMBL:
    for line in CHEMBL:
        line = line.strip()
        if line.startswith("CHEMBL"):
            molecule = line
        else:
            continue
        response_API_mol = requests.get('https://www.ebi.ac.uk/chembl/api/data/molecule/'+molecule+'.json')
        response_json_mol = response_API_mol.json() 
        molecule_name = response_json_mol["pref_name"]
        molecule_formula = response_json_mol["molecule_properties"]["full_molformula"]
        molecule_type = response_json_mol["molecule_type"]
        if molecule_type == 'Small molecule' and molecule_name != None:
                if molecule not in MOLECULES:
                    with connection.cursor() as c:
                        c.execute(sthMolecule, (molecule, molecule_name, molecule_formula,
                                                molecule_type))
                        molecule_id = c.lastrowid
                        MOLECULES[molecule] = molecule_id
                response_API_act = requests.get('https://www.ebi.ac.uk/chembl/api/data/mechanism.json?molecule_chembl_id='+molecule+'&limit=1')
                response_json_act = response_API_act.json()
                response_text_act = json.dumps(response_json_act, sort_keys=True, indent=4)
                print(response_text_act)  
                if response_json_act["mechanisms"]:
                    target = response_json_act["mechanisms"][0]["target_chembl_id"]
                    if target in target_conversion:
                        target = target_conversion[target]
                        reference = response_json_act["mechanisms"][0]["mechanism_refs"][0]["ref_url"]
                        activity = response_json_act["mechanisms"][0]["action_type"]
                        if activity == 'AGONIST' or activity == 'ANTAGONIST':
                            thm = "{}{}".format(molecule, target)
                            if thm not in target_has_molecule:
                                with connection.cursor() as c:
                                    c.execute(sthTargetMolecule, (target, molecule, reference, activity))
                                    target_has_molecule[thm] = True

print("ok")
##
##

