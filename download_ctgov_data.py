# Author : A.Duigou
# Company : Data Boost
# The goal of this code snippet is to download for a specific indication the clinical studies-related data from CT.gov
# This transfer use the APi service provide by CT.gov : https://classic.clinicaltrials.gov/api/

# Dependancies & modules
import json
import boto3
import time
from urllib.request import urlopen
import pandas as pd
from io import StringIO
import requests

start = time.time() 

def json_flattening(df, column_name):
    flatten_columns = pd.json_normalize(df[column_name], max_level=1)
    df = df.drop(column_name, axis=1)
    df = pd.concat([df, flatten_columns], axis=1)
    return df

def export_creation(df, column_list):
    df = pd.DataFrame(data['FullStudiesResponse']['FullStudies'])
    df = df.drop('Rank', axis=1)

    df = json_flattening(df, 'Study')
    df = json_flattening(df, 'ProtocolSection.IdentificationModule')
    df = df[column_list + ['NCTId']]
    for i in column_list:
        df = json_flattening(df, i)
        
    return df

master_data = pd.DataFrame()
status = pd.DataFrame()
primary_outcome = pd.DataFrame()
secondary_outcome = pd.DataFrame()
eligibility = pd.DataFrame()
sponsors = pd.DataFrame()
collaborators = pd.DataFrame()
location = pd.DataFrame()
design = pd.DataFrame()

# Initialization of the s3 client
s3 = boto3.client('s3', aws_access_key_id='AKIA4CZKLK4EPXCZGA5R', aws_secret_access_key='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', region_name='eu-west-3')

# Parameters
disease="parkinson" # Indication to search & download
min_r="1" 
max_r="100" # number of full studies per query
step = 100

# First request to get the number of results to download
url = "https://classic.clinicaltrials.gov/api/query/full_studies?expr=" + disease + "&min_rnk=" + min_r + "&max_rnk=" + max_r + "&fmt=json"
response = urlopen(url)
# response = requests.get(url, headers={'Accept': 'application/json'})
json_data = json.loads(response.read())
number_of_studies = json_data['FullStudiesResponse']['NStudiesFound']
number_of_studies = number_of_studies // step

# Main loop to query and concatenate the multiple responses of the API
data_concat = {}
for i in range(1, number_of_studies + 1 ):
    min_r = str((i - 1) * step + 1)
    max_r = str(i * step)

    url = "https://classic.clinicaltrials.gov/api/query/full_studies?expr=" + disease + "&min_rnk=" + min_r + "&max_rnk=" + max_r + "&fmt=json"
    response = urlopen(url)
    # response = requests.get(url, headers={'Accept': 'application/json'})
    data = json.loads(response.read())
    raw_df = data["FullStudiesResponse"]["FullStudies"]

    # master data module management
    df_master_data = export_creation(raw_df, ['ProtocolSection.DescriptionModule', 'ProtocolSection.ConditionsModule'])
    # status module management
    df_status = export_creation(raw_df, ['ProtocolSection.StatusModule'])
    # outcome module management
    df = pd.DataFrame(data["FullStudiesResponse"]["FullStudies"])
    df = df.drop('Rank', axis=1)
    df = json_flattening(df, 'Study')
    df_outcome = df[['ProtocolSection.IdentificationModule', 'ProtocolSection.OutcomesModule']]
    df_outcome = json_flattening(df_outcome, 'ProtocolSection.IdentificationModule')
    df_outcome = df_outcome[['NCTId', 'ProtocolSection.OutcomesModule']]
    df_outcome = pd.concat([df_outcome['NCTId'], pd.json_normalize(df_outcome['ProtocolSection.OutcomesModule'])], axis=1)
    df_outcome_primary = df_outcome[['NCTId', 'PrimaryOutcomeList.PrimaryOutcome']].explode(['PrimaryOutcomeList.PrimaryOutcome']).reset_index(drop=True)
    df_outcome_primary = pd.concat([df_outcome_primary['NCTId'], pd.json_normalize(df_outcome_primary['PrimaryOutcomeList.PrimaryOutcome'])], axis=1)
    df_outcome_secondary = df_outcome[['NCTId', 'SecondaryOutcomeList.SecondaryOutcome']].explode(['SecondaryOutcomeList.SecondaryOutcome']).reset_index(drop=True)
    df_outcome_secondary = pd.concat([df_outcome_secondary['NCTId'], pd.json_normalize(df_outcome_secondary['SecondaryOutcomeList.SecondaryOutcome'])], axis=1)
    # eligibility module management
    df_eligibility = export_creation(raw_df, ['ProtocolSection.EligibilityModule'])
    # sponsors module management  
    df_sponsors = export_creation(raw_df, ['ProtocolSection.SponsorCollaboratorsModule'])
    # colaborators module management
    df_collaborators = df_sponsors[['NCTId','CollaboratorList.Collaborator']]
    df_collaborators = df_collaborators.explode('CollaboratorList.Collaborator').reset_index(drop=True) 
    df_collaborators = pd.concat([df_collaborators['NCTId'], pd.json_normalize(df_collaborators['CollaboratorList.Collaborator'])], axis=1)
    # sites module management
    df = pd.DataFrame(data["FullStudiesResponse"]["FullStudies"])
    df = df.drop('Rank', axis=1)
    df = json_flattening(df, 'Study')
    df_location = df[['ProtocolSection.IdentificationModule','ProtocolSection.ContactsLocationsModule']]
    df_location = json_flattening(df_location, 'ProtocolSection.IdentificationModule')
    df_location = df_location[['NCTId', 'ProtocolSection.ContactsLocationsModule']]
    df_location = pd.concat([df_location['NCTId'], pd.json_normalize(df_location['ProtocolSection.ContactsLocationsModule'])], axis=1)
    df_location = df_location[['NCTId', 'LocationList.Location']].explode(['LocationList.Location']).reset_index(drop=True)
    df_location = pd.concat([df_location['NCTId'], pd.json_normalize(df_location['LocationList.Location'])], axis=1)
    # design module management
    df_design = export_creation(raw_df, ['ProtocolSection.DesignModule'])
    df_design['DesignInfo.DesignObservationalModelList'] = df_design['DesignInfo.DesignObservationalModelList'].apply(lambda x: ', '.join(map(str, x.values())) if isinstance(x, dict) else x)
    df_design['DesignInfo.DesignTimePerspectiveList'] = df_design['DesignInfo.DesignTimePerspectiveList'].apply(lambda x: ', '.join(map(str, x.values())) if isinstance(x, dict) else x)
    df_design['PhaseList.Phase'] = df_design['PhaseList.Phase'].apply(lambda x: ', '.join(map(str, x.values())) if isinstance(x, dict) else x)

    master_data = pd.concat([master_data, df_master_data], axis=0)
    status = pd.concat([status, df_status], axis=0)   
    primary_outcome = pd.concat([primary_outcome, df_outcome_primary], axis=0)   
    secondary_outcome = pd.concat([secondary_outcome, df_outcome_secondary], axis=0)   
    eligibility = pd.concat([eligibility, df_eligibility], axis=0)   
    sponsors = pd.concat([sponsors, df_sponsors], axis=0)   
    collaborators = pd.concat([collaborators, df_collaborators], axis=0)   
    location = pd.concat([location, df_location], axis=0)   
    design = pd.concat([design, df_design], axis=0)     

# Convert DataFrame into CSV
csv_buffer = StringIO()
master_data.to_csv(csv_buffer, index=False)
# AWS parameters
bucket_name = 'ctgov-raw-data'
sub_directory = 'full-studies-per-indication/'
file_name = sub_directory + disease + '_master_data.csv'
# Upload of the compiled JSON file into the s3 bucket
try:
    response = s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
    print("Upload success for file : ", file_name, " (", response, ")")
except Exception as e:
    print("Upload error :", e)
print("Code executed in :", round(time.time() - start, 1), " sec")

# Convert DataFrame into CSV
csv_buffer = StringIO()
status.to_csv(csv_buffer, index=False)
# AWS parameters
bucket_name = 'ctgov-raw-data'
sub_directory = 'full-studies-per-indication/'
file_name = sub_directory + disease + '_status.csv'
# Upload of the compiled JSON file into the s3 bucket
try:
    response = s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
    print("Upload success for file : ", file_name, " (", response, ")")
except Exception as e:
    print("Upload error :", e)
print("Code executed in :", round(time.time() - start, 1), " sec")

# Convert DataFrame into CSV
csv_buffer = StringIO()
primary_outcome.to_csv(csv_buffer, index=False)
# AWS parameters
bucket_name = 'ctgov-raw-data'
sub_directory = 'full-studies-per-indication/'
file_name = sub_directory + disease + '_primary_outcome.csv'
# Upload of the compiled JSON file into the s3 bucket
try:
    response = s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
    print("Upload success for file : ", file_name, " (", response, ")")
except Exception as e:
    print("Upload error :", e)
print("Code executed in :", round(time.time() - start, 1), " sec")

# Convert DataFrame into CSV
csv_buffer = StringIO()
secondary_outcome.to_csv(csv_buffer, index=False)
# AWS parameters
bucket_name = 'ctgov-raw-data'
sub_directory = 'full-studies-per-indication/'
file_name = sub_directory + disease + '_secondary_outcome.csv'
# Upload of the compiled JSON file into the s3 bucket
try:
    response = s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
    print("Upload success for file : ", file_name, " (", response, ")")
except Exception as e:
    print("Upload error :", e)
print("Code executed in :", round(time.time() - start, 1), " sec")

# Convert DataFrame into CSV
csv_buffer = StringIO()
eligibility.to_csv(csv_buffer, index=False)
# AWS parameters
bucket_name = 'ctgov-raw-data'
sub_directory = 'full-studies-per-indication/'
file_name = sub_directory + disease + '_eligibility.csv'
# Upload of the compiled JSON file into the s3 bucket
try:
    response = s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
    print("Upload success for file : ", file_name, " (", response, ")")
except Exception as e:
    print("Upload error :", e)
print("Code executed in :", round(time.time() - start, 1), " sec")

# Convert DataFrame into CSV
csv_buffer = StringIO()
sponsors.to_csv(csv_buffer, index=False)
# AWS parameters
bucket_name = 'ctgov-raw-data'
sub_directory = 'full-studies-per-indication/'
file_name = sub_directory + disease + '_sponsors.csv'
# Upload of the compiled JSON file into the s3 bucket
try:
    response = s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
    print("Upload success for file : ", file_name, " (", response, ")")
except Exception as e:
    print("Upload error :", e)
print("Code executed in :", round(time.time() - start, 1), " sec")

# Convert DataFrame into CSV
csv_buffer = StringIO()
collaborators.to_csv(csv_buffer, index=False)
# AWS parameters
bucket_name = 'ctgov-raw-data'
sub_directory = 'full-studies-per-indication/'
file_name = sub_directory + disease + '_collaborators.csv'
# Upload of the compiled JSON file into the s3 bucket
try:
    response = s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
    print("Upload success for file : ", file_name, " (", response, ")")
except Exception as e:
    print("Upload error :", e)
print("Code executed in :", round(time.time() - start, 1), " sec")

# Convert DataFrame into CSV
csv_buffer = StringIO()
location.to_csv(csv_buffer, index=False)
# AWS parameters
bucket_name = 'ctgov-raw-data'
sub_directory = 'full-studies-per-indication/'
file_name = sub_directory + disease + '_location.csv'
# Upload of the compiled JSON file into the s3 bucket
try:
    response = s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
    print("Upload success for file : ", file_name, " (", response, ")")
except Exception as e:
    print("Upload error :", e)
print("Code executed in :", round(time.time() - start, 1), " sec")

# Convert DataFrame into CSV
csv_buffer = StringIO()
design.to_csv(csv_buffer, index=False)
# AWS parameters
bucket_name = 'ctgov-raw-data'
sub_directory = 'full-studies-per-indication/'
file_name = sub_directory + disease + '_design.csv'
# Upload of the compiled JSON file into the s3 bucket
try:
    response = s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
    print("Upload success for file : ", file_name)
except Exception as e:
    print("Upload error :", e)
print("Code executed in :", round(time.time() - start, 1), " sec")