import requests
import re
import os

def parse_hotspots(report):
    response = requests.post(url=f'{os.getenv("URL")}/api/authentication/login', data={'login':os.getenv("USERNAME"), 'password':os.getenv("PASSWORD")})
    jwt_token = requests.utils.dict_from_cookiejar(response.cookies)['JWT-SESSION']
    with open('finall_report.txt', 'a') as finallReport:
        hotspots = report["hotspots"]
        for hotspot in hotspots:
            vulnerabilityProbability = hotspot["vulnerabilityProbability"]
            component = hotspot["component"]
            pieceOfCode = None
            if "textRange" in hotspot:
                pieceOfCode = hotspot["textRange"]
                if "startLine" in pieceOfCode:
                    startLine = pieceOfCode["startLine"]
                if "endLine" in pieceOfCode:
                    endLine = pieceOfCode["endLine"]
            
                if startLine > 5 :
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
                        
                if countLineOfCode < 11:
                    while countLineOfCode != 11:
                        code += '\n'
                        countLineOfCode += 1

            message = hotspot["message"]
            
            if pieceOfCode != None:
                finallReport.write(f"Vulnerability Probability: {vulnerabilityProbability}, Component: {component}, Start Line:  {startLine}, End Line:  {endLine}, Code:\n{code}, Description: {message}\n")
            else:
                finallReport.write(f"Vulnerability Probability: {vulnerabilityProbability}, Component: {component}, Description: {message}\n")