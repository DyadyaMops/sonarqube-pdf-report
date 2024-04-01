import requests
import re
import os

def parse_issues(report, componentKeys, page):

    # we get a jwt token for subsequent access to the api when importing code sections

    response = requests.post(url=f'{os.getenv("URL")}/api/authentication/login', data={'login':os.getenv("USERNAME"), 'password':os.getenv("PASSWORD")}) 
    jwt_token = requests.utils.dict_from_cookiejar(response.cookies)['JWT-SESSION']
    
    # for more convenient parsing, we record only the necessary information in a separate txt

    if page == 1:
        with open('finall_report.txt', 'w') as finallReport:
            finallReport.write(componentKeys+'\n')
            countOfIssues = report["total"]
            finallReport.write(str(countOfIssues)+'\n')
            finallReport.close()

    with open('finall_report.txt', 'a') as finallReport:
        issues = report["issues"]
        for issue in issues:
            severity = issue["severity"]
            component = issue["component"]
            pieceOfCode = None
            if "textRange" in issue:
                pieceOfCode = issue["textRange"]
                if "startLine" in pieceOfCode:
                    startLine = pieceOfCode["startLine"]
                if "endLine" in pieceOfCode:
                    endLine = pieceOfCode["endLine"]
            
                if startLine > 5 :
                #     if the code section is not at the beginning of the file (on 1 line), then grab a few more
                #     rows at the top and bottom (five each)
                    code = requests.get(url=f'{os.getenv("URL")}/api/sources/lines?key={component}&from={startLine-5}&to={endLine+5}', 
                                    cookies={'JWT-SESSION':jwt_token})
                else:
                    code = requests.get(url=f'{os.getenv("URL")}/api/sources/lines?key={component}&from={startLine}&to={endLine+5}', 
                                    cookies={'JWT-SESSION':jwt_token})
                try:
                    data = code.json()
                except Exception as asd:
                    print(asd)
                code=''
                countLineOfCode = 0
                try:
                    sources = data['sources']
                except:
                    pass
                for codeLine in sources:
                    codeLine = codeLine['code']
                    codeLine = re.sub(r'<[^>]*>', '', codeLine)
                    code += f"{codeLine}\n"
                    countLineOfCode += 1
                    if countLineOfCode == 11: 
                        break
                        
                # so that the code inside the pdf is displayed correctly and there are no offsets
                # add line breaks until the number of lines of code is 11
                if countLineOfCode < 11:
                    while countLineOfCode != 11:
                        code += '\n'
                        countLineOfCode += 1

            discription = issue["message"]
            typeOfIssue = issue["type"]

            if typeOfIssue != 'CODE_SMELL':
            
                if pieceOfCode != None:
                    finallReport.write(f"Severity: {severity}, Component: {component}, Start Line: {startLine}, End Line: {endLine}, Code:\n{code}, Description:  {discription}, Type: {typeOfIssue}\n")
                    
                else:
                    finallReport.write(f"Severity: {severity}, Component: {component}, Description: {discription}, Type: {typeOfIssue}\n")

        finallReport.close()



    

    

    


    









    
    



    
