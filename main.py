# -*- coding: utf-8 -*-

import argparse
import json
import os
import requests

from dotenv import load_dotenv
from constants import *
from hotspots_parser import parse_hotspots
from issues_parser import parse_issues
from sonarqube import SonarCloudClient


if __name__ == "__main__":
    
    componentKeys = input('>> Введите название проекта: ')

    load_dotenv()

    sonar = SonarCloudClient(sonarqube_url=URL, username=USERNAME, token=os.getenv("TOKEN"))
    sonarIssues = sonar.issues.search_issues(componentKeys=componentKeys, p=1, ps=500)
    total = sonarIssues['total']
    
    for i in range(1, (total//500)+2):
        sonarIssues = sonar.issues.search_issues(componentKeys=componentKeys, p=i, ps=500)
        
        with open('issues.json', 'w') as reportFile:
            json.dump(sonarIssues, reportFile)
            reportFile.close()
        
        with open('issues.json', 'r') as reportFile:
            report = json.load(reportFile)
            parse_issues(report, componentKeys, page = i)
            reportFile.close()


    response = requests.post(url=f'{URL}/api/authentication/login', data={'login':'admin', 'password':os.getenv("PASSWORD")})
    jwt_token = requests.utils.dict_from_cookiejar(response.cookies)['JWT-SESSION']
    response = requests.get(url=f"{URL}/api/hotspots/search?projectKey={componentKeys}&resolution=ACKNOWLEDGED&status=REVIEWED", cookies={'JWT-SESSION':jwt_token})
    
    with open('hotspots.json', 'w') as reportFile:
        data = response.json()
        json.dump(data, reportFile)
        reportFile.close()

    with open('hotspots.json', 'r') as reportFile:
        report = json.load(reportFile)
        parse_hotspots(report)
        reportFile.close()

    from pdf import PDFGenerator
    pdf = PDFGenerator()
    pdf.generate_report()
    

        



        
        