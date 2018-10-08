from docassemble.webapp.config import daconfig
from docassemble.base.core import DAObject
import psycopg2
import base64
import json
import random

#drop table if exists survey_answers; create table survey_answers (submissiontime timestamp default now(), content text);

class Storage(DAObject):
    def init(self):
        return super(Storage, self).init()
    def save_survey_results(self, the_dict):
        storage = daconfig.get('storage', None)
        if storage is None:
            raise Exception("Could not get database connection information")
        try:
            conn = psycopg2.connect("dbname='" + storage['database'] + "' user='" + storage['username'] + "' host='" + storage['host'] + "' password='" + storage['password'] + "'")
        except Exception as e:
            raise Exception("Could not connect to database: " + str(e))
        answer_json = json.dumps(the_dict)
        cur = conn.cursor()
        cur.execute("""insert into survey_answers (content) values (%s)""", (str(answer_json),))
        conn.commit()
        cur.close()
        conn.close()
        return
    
class LegalServer(DAObject):
    def init(self):
        self.connected = False
        return super(LegalServer, self).init()
    def __del__(self):
        if self.connected:
            self.conn.close()
        return
    def connect(self):
        legalserver = daconfig.get('legalserver', None)
        if legalserver is None:
            raise Exception("Could not get Legal Server connection information")
        try:
            self.conn = psycopg2.connect("dbname='" + legalserver['database'] + "' user='" + legalserver['username'] + "' host='" + legalserver['host'] + "' password='" + legalserver['password'] + "'")
        except Exception as e:
            raise Exception("Could not connect to Legal Server: " + str(e))
        self.connected = True
        return
    def lookup_unique_id(self, unique_id):
        cur = self.conn.cursor()
        cur.execute("""select m.identification_number, up.first as sfname, up.last as slname, up.email as semail, c.first as cfname, c.last as clname, c.email as cemail, map.office_name, lookup_citizenship_statuses.name as cstatus, up.phone_business as sphone, lookup_legal_problem_code.name as pcode from matter as m left outer join matter_assignment_primary as map on (m.id=map.matter_id) left outer join users as u on (map.user_id=u.id) left outer join person as up on (u.person_id=up.id) left outer join person as c on (m.person_id=c.id) left outer join lookup_citizenship_statuses on (m.citizenship_status=lookup_citizenship_statuses.id) left outer join lookup_legal_problem_code on (m.legal_problem_code = lookup_legal_problem_code.id) where m.unique_id=%s""", (str(unique_id),))
        rows = cur.fetchall()
        result = dict()
        for row in rows:
            result['identification_number'] = row[0]
            result['sfname']                = row[1]
            result['slname']                = row[2]
            result['semail']                = row[3]
            result['cfname']                = row[4]
            result['clname']                = row[5]
            result['cemail']                = row[6]
            result['office_name']           = row[7]
            result['cstatus']               = row[8]
            result['sphone']                = row[9]
            result['pcode']                 = row[10]
        if 'identification_number' not in result:
            raise Exception("Could not retrieve information about unique_id")
        return(result)
            
class LegalServerCase(DAObject):
    def init(self):
        self.retrieved = False
        return super(LegalServerCase, self).init()
    def retrieve(self, encoded_unique_id):
        unique_id = base64.b64decode(encoded_unique_id)
        legalserver = LegalServer()
        legalserver.connect()
        self.fields = legalserver.lookup_unique_id(unique_id)
        self.retrieved = True
        return

class ProblemListing(DAObject):
    def legal(self):
        return [
            {None: "#### Income and Benefits"},
            "Personal income tax problems",
            "Getting and keeping cash assistance",
            "Getting and keeping food stamps",
            "Getting and keeping Social Security Disability and/or SSI benefits",
            {None: "#### Housing"},
            "Eviction from your rental property",
            "Poor housing condition in rental property",
            "Problems with the Philadelphia Housing Authority",
            "Mortgage delinquency or foreclosure",
            "Real estate tax delinquency or foreclosure",
            "Getting on the deed to a house",
            "Problems with the purchase of real estate",
            "Housing discrimination",
            "Removing someone from your property",
            "Blighted / abandoned property",
            {None: "#### Family"},
            "Divorce",
            "Child abuse / neglect",
            "Domestic Violence",
            "Child custody / visitation",
            "Obtaining an order for child/spousal support",
            "Enforcing an order for child/spousal support",
            "Defending against child/spousal support claims",
            "Adoption / termination of parental rights",
            "Legal responsibility for an adult (guardianship)",
            {None: "#### Money and credit"},
            "Bankruptcy",
            "Identity theft",
            "Credit card collection",
            "Automobile loans",
            "Student loans",
            "Very old judgments against you",
            "Trade school fraud",
            "Rent-to-own agreements",
            "Sales contracts",
            "Garnishing of wages",
            "Harassment by collection agencies",
            "Unfair business practices / predatory lending",
            {None: "#### Employment"},
            "Unemployment compensation",
            "Receiving pay from a job",
            "Denied employment because of criminal records",
            "Wrongful discharge from employment",
            "Employment discrimination",
            "Pension benefits",
            "Unfair labor practices",
            "Unsafe working conditions",
            "Civil service problems",
            {None: "#### Health"},
            "Medical Assistance, Medicaid, or Medicare",
            "Getting and keeping private health insurance",
            "Children's Health Insurance Program (CHIP)",
            "Affordable Care Act",
            "Nursing home care",
            "Access to home health aides",
            {None: "#### Utilities"},
            "Preventing utility shutoffs",
            "Resolving utility billing problems",
            "Telephone problems",
            "Internet access",
            {None: "#### Rights"},
            "Rights of the disabled",
            "LGBT rights",
            "Rights of non-English speakers",
            "Police misconduct",
            "Elder abuse",
            {None: "#### Other"},
            "Veterans' issues",
            "Driver's license issues",
            "Name change",
            "Immigration",
            "Incorporation of business",
            "Incorporation of non-profit",
            "Bench warrants",
            "Prison problems",
            "Special education / school discipline",
            "Lawsuits (e.g., auto accident defense)",
            "Wills/powers of attorney/advance directives"]
    def social(self):
        return [
            "Not having any health insurance",
            "Health insurance too expensive",
            "Lack of access to healthy food",
            "Not enough homeless shelters",
            "Not enough soup kitchens",
            "Lack of affordable housing",
            "Domestic violence",
            "Gentrification",
            "Predatory lenders",
            "Abandoned property / empty lots",
            "Lack of access to financial services (banks, loans)",
            "Youth unemployment",
            "Adult unemployment",
            "Lack of support for youth in foster system who turn 18",
            "Employers do not provide enough sick days",
            "Unhealthy environment",
            "Chronic health problems (asthma, diabetes, obesity)",
            "Violence",
            "Lack of affordable child care",
            "Not enough jobs",
            "Jobs do not pay enough",
            "Guns",
            "Crime",
            "Immoral behavior",
            "Corruption of public officials",
            "Lack of knowledge about how to access services",
            "Discrimination",
            "Mental health issues (depression, bipolar, etc.)",
            "Too difficult to escape burden of debt",
            "People who owe child support don't pay it",
            "Too difficult to pay child support while supporting yourself",
            "Too easy for banks to foreclose on homes",
            "Homes stay in foreclosure for too long",
            "Children being abused / neglected",
            "Bad landlords",
            "Drugs",
            "Houses being neglected",
            "Insufficient policing",
            "Police misconduct",
            "Public areas not well maintained (trash, unsafe sidewalks, potholes in roads, etc.)",
            "Noise",
            "Unfair criminal charges",
            "Unfair job termination",
            "Real estate taxes too high",
            "Income taxes too high",
            "Liens on property",
            "Lack of community centers",
            "Lack of after-school programs",
            "Not enough opportunities for peaceful conflict resolution",
            "Insufficient government services",
            "Unsafe drivers",
            "Poor public transportation services",
            "Transportation too expensive",
            "Not enough community organizations",
            "Lack of support for pregnant and parenting teens",
            "Low quality of schools",
            "Lack of economic opportunity",
            "Too much development",
            "Not enough development",
            "Too difficult to move from one residence to another",
            "People change residences too often",
            "Too easy for landlords to evict people",
            "Too difficult for landlords to evict people",
            "Too difficult to shield children from bad influences",
            "Language barriers to accessing services",
            "Waiting list for public housing is too long",
            "High school dropout rate too high"]

