# project: p2
# submitter: Smwells3
# partner: none
# hours: 14

import pandas as pd
import csv
import json
from zipfile import ZipFile
from io import TextIOWrapper

class ZippedCSVReader():
    def __init__(self, path):
        self.path = path
        with ZipFile(self.path) as zf:
            self.paths = ZipFile.namelist(zf)
        
    def load_json(self, filename):
        with ZipFile(self.path) as zf:
            with zf.open(filename) as f:
                data = f.read()
                dic = json.loads(data)
        return dic
    
    def rows(self, filename=None):
        row = []
        if filename == None:
            for file in self.paths:
                with ZipFile(self.path) as zf:
                     with zf.open(file) as f:
                        string = TextIOWrapper(f)
                        reader = csv.DictReader(string, delimiter=",")
                        for line in reader:
                            row.append(dict(line))
            return row
        else:
            with ZipFile(self.path) as zf:
                 with zf.open(filename) as f:
                    string = TextIOWrapper(f)
                    reader = csv.DictReader(string, delimiter=",")
                    for line in reader:
                        row.append(dict(line))
                    return row   
                
class Loan():
    def __init__(self, amount, purpose, race, income, decision):
        self.amount = amount
        self.purpose = purpose
        self.race = race
        self.income = income
        self.decision = decision

    def __repr__(self):
        return f"Loan({self.amount}, '{self.purpose}', '{self.race}', {self.income}, '{self.decision}')"

    def __getitem__(self, lookup):
        lookups = []
        lookups.append(self.amount)
        lookups.append(self.purpose)
        lookups.append(self.race)
        lookups.append(self.income)
        lookups.append(self.decision)
        if lookup in lookups:
            return 1
        else:
            try:
                return getattr(self, lookup)
            except:
                return 0
            
class Bank():
    def __init__(self, name, reader):
        self.name = name
        self.reader = reader.rows()
        
    def loans(self):
        loan_list = []
        for row in self.reader:
            agency = row["agency_abbr"]
            amount = row["loan_amount_000s"]
            if amount == "":
                amount = 0
            amount = int(amount)
            purpose = row["loan_purpose_name"]
            race = row["applicant_race_name_1"]
            income = row["applicant_income_000s"]
            if income == "":
                income = 0
            income = int(income)
            action = row["action_taken"]
            if action == "1":
                action = "approve"
            else:
                action = "deny"
            if self.name != None:
                if self.name == agency:
                    loan_list.append(Loan(amount, purpose, race, income, action))
            else:
                loan_list.append(Loan(amount, purpose, race, income, action))
        return loan_list
            
def get_bank_names(reader):
    agencies = []
    for row in reader.rows():
        agencies.append(row["agency_abbr"])
    return sorted(list(set(agencies)))
            
class SimplePredictor():
    def __init__(self):
        self.approved = 0
        self.denied = 0
        
    def predict(self, loan):
        purpose = loan["purpose"]
        if purpose == "Refinancing":
            self.approved += 1
            return True
        else:
            self.denied += 1
            return False
        
    def get_approved(self):
        return self.approved

    def get_denied(self):
        return self.denied

class DTree(SimplePredictor):
    def __init__(self, nodes):
        SimplePredictor()
        self.root = nodes
        self.count = 0
        self.approved = 0
        self.denied = 0

    def dump(self, node=None, indent=0):
        if node == None:
            node = self.root
        if node["field"] == "class":
            line = "class=" + str(node["threshold"])
        else:
            line = node["field"] + " <= " + str(node["threshold"])
        print("  "*indent + line)
        if node["left"]:
            self.dump(node["left"], indent+1)
        if node["right"]:
            self.dump(node["right"], indent+1)
     
    def node_count(self, node=None):
        if node == None:
            node = self.root
        self.count += 1
        if node["left"]:
            self.node_count(node["left"])
        if node["right"]:
            self.node_count(node["right"])
        return self.count

    def predict(self, loan, node=None):
        if node == None:
            node = self.root
        criteria = node["field"]
        if criteria == "class":
            if node["threshold"] == 0:
                self.denied += 1
                return False
            self.approved += 1
            return True
        if loan[criteria] <= node["threshold"]:
            node = node["left"]
            return self.predict(loan, node)
        node = node["right"]
        return self.predict(loan, node)
    
    def get_approved(self):
        return self.approved
    
    def get_denied(self):
        return self.denied
            
def bias_test(bank, predictor, race_override):
    results = {}
    changed = 0
    loan_list = bank.loans()
    for loan in loan_list:
        results[loan] = predictor.predict(loan)
        new_loan = Loan(loan["amount"], loan["purpose"], race_override, loan["income"], loan["action"])
        new_result = predictor.predict(new_loan)
        if new_result != results[loan]:
            changed += 1
    return changed/len(loan_list)       