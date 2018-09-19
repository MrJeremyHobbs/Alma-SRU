#!/usr/bin/python3
import concurrent.futures
import requests
import xmltodict

# configs #####################################################################
SRU_PATHS = {
    'IZ': 'https://yourinst.alma.exlibrisgroup.com/view/sru/01*****',
    'NZ': 'https://yournetwork.alma.exlibrisgroup.com/view/sru/01*****',
}

inst_code = '01******'

script_version = '0.1.3'
api_version = '1.2'

# main class ##################################################################
class SRU():
    def __init__(self, r, zone="", inst_code="", sru_path=""):
        self.zone = zone
        self.r = r
        self.inst_code = inst_code
        self.xml = r.text or ""
        self.dict = xmltodict.parse(self.xml, dict_constructor=dict)
        
        self.print_holdings = []
        self.e_holdings = []
        
        self.call_number = ""
        self.location = ""
        
        # get number of records, check for errors
        try:
            self.numberOfRecords = int(self.dict['searchRetrieveResponse']['numberOfRecords'])
            self.ok = True
            self.errors = None
        except Exception as e:
            self.numberOfRecords = 0
            self.ok = False
            self.errors = self.dict['searchRetrieveResponse']['diagnostics']['diag:diagnostic']['diag:message']
            print(f"{e}\n{self.xml}")
            
        # get print holdings
        if self.numberOfRecords > 0 and zone == "IZ":
            try:
                self.records = self.dict['searchRetrieveResponse']['records']['record']
                self.print_holdings, self.location, self.call_number = get_print_holdings(self.records)
            except Exception as e:
                self.print_holdings = []
                print(f"{e}\n\n{self.xml}")
                
        # get e-holdings
        if self.numberOfRecords > 0:
            try:
                self.records = self.dict['searchRetrieveResponse']['records']['record']
                self.e_holdings = get_e_holdings(self.records, zone=self.zone, inst_code = self.inst_code)
            except Exception as e:
                self.e_holdings = []
                print(f"{e}\n\n{self.xml}")
                
        # set e-availability
        if self.e_holdings != []:
            self.have_e_holdings = True
        else:
            self.have_e_holdings = False
            
# search functions ############################################################
def search(query=""):
    r = requests.get(query)
    return r
    
def load_url(url):
    r = requests.get(url)
    return r
    
def searches(urls="", workers=""):
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        r_array = executor.map(load_url, urls)    
    return r_array
    
def make_url(zone="", query="", operation="searchRetrieve", 
                   recordSchema="marcxml", maximumRecords="10", startRecord="1"):
    sru_path = SRU_PATHS[zone]
    url = f"{sru_path}?version={api_version}&operation={operation}&recordSchema={recordSchema}&maximumRecords={maximumRecords}&startRecord={startRecord}&query={query}"
    return url
    
# parse functions #############################################################
def parse(r, zone="", inst_code=inst_code):
    sru_object = SRU(r, zone, inst_code)
    return sru_object
    
def get_print_holdings(records):
    print_holdings = []
    
    # parse SRU response
    for record in records:
        try:
            datafields = record['recordData']['record']['datafield']
        except Exception as e:
            #print(e)
            datafields = records['recordData']['record']['datafield']
            
        for field in datafields:
            code_c = ""
            code_d = ""
            range = ""
            code_t = []
            # Check for print holdings
            if field['@tag'] == "AVA":
                for subfield in field['subfield']:
                    if subfield['@code'] == '8':
                        code_8 = subfield['#text']
                    if subfield['@code'] == 'c':
                        code_c = subfield['#text']
                    if subfield['@code'] == 'd':
                        code_d = subfield['#text']
                    if subfield['@code'] == 'e':
                        code_e = subfield['#text']
                    if subfield['@code'] == 'm':
                        code_m = subfield['#text']
                    if subfield['@code'] == 's':
                        code_s = subfield['#text']
                    if subfield['@code'] == 't':
                        #code_t = subfield['#text']
                        code_t.append(subfield['#text'])
                
                # Join code_t string
                range = "\n".join(code_t)
                
                # Check for print holdings
                if code_e == "available" or code_e == "Available":
                    print_holdings_statement = f"{range} ({code_c})"
                    if print_holdings_statement not in print_holdings:
                        print_holdings.append(print_holdings_statement)
                
    return print_holdings, code_c, code_d
    
def get_e_holdings(records, zone="", inst_code=""):
    e_holdings = []

    # parse SRU response
    for record in records:
        try:
            datafields = record['recordData']['record']['datafield']
        except Exception as e:
            #print(e)
            datafields = records['recordData']['record']['datafield']
            
        for field in datafields:
            code_e = ""
            code_m = ""
            code_s = ""
        
            # Check for electronic access
            if field['@tag'] == "AVE":
                for subfield in field['subfield']:
                    if subfield['@code'] == '8':
                        code_8 = subfield['#text']
                    if subfield['@code'] == 'c':
                        code_c = subfield['#text']
                    if subfield['@code'] == 'e':
                        code_e = subfield['#text']
                    if subfield['@code'] == 'm':
                        code_m = subfield['#text']
                    if subfield['@code'] == 's':
                        code_s = subfield['#text']
                    if subfield['@code'] == 't':
                        code_t = subfield['#text']
                    
                    # Check for e-holdings in NZ
                    if zone == "NZ":
                        # Check for campus availability in NZ
                        if subfield['@code'] == "i" and code_e == "Available" and subfield['#text'] == inst_code:
                            e_holdings_statement = f"{code_m} ({code_s})"
                            if e_holdings_statement not in e_holdings:
                                e_holdings.append(e_holdings_statement)
            
                # Check for e-holdings in IZ
                if zone == "IZ" and code_e == "Available":
                    e_holdings_statement = f"{code_m} ({code_s})"
                    if e_holdings_statement not in e_holdings:
                        e_holdings.append(e_holdings_statement)
                
    return e_holdings