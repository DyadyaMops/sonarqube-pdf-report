import requests
import re
import os

from constants import *

def translate_severity(severity):
    if severity == 'CRITICAL':
        severity = 'КРИТИЧНЫЙ'
    elif severity == 'BLOCKER':
        severity = 'БЛОКАДА'
    elif severity == 'MINOR':
        severity = 'НИЗКИЙ'
    elif severity == 'INFO':
        severity = 'ИНФО'
    elif severity == 'MAJOR':
        severity = 'ВЫСОКИЙ'
    return severity


def parse_issues(report, componentKeys, page):

    # получаем jwt-токен для последующего обращения к api при импорте участков кода

    response = requests.post(url=f'{URL}/api/authentication/login', data={'login':'admin', 'password':os.getenv("PASSWORD")}) 
    jwt_token = requests.utils.dict_from_cookiejar(response.cookies)['JWT-SESSION']
    
    # для более удобного парсинга записываем только нужную информацию в отдельный txt

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
            severity = translate_severity(severity)
            component = issue["component"]
            pieceOfCode = None
            if "textRange" in issue:
                pieceOfCode = issue["textRange"]
                if "startLine" in pieceOfCode:
                    startLine = pieceOfCode["startLine"]
                if "endLine" in pieceOfCode:
                    endLine = pieceOfCode["endLine"]
            
                if startLine > 5 :
                #     если участок кода находится не в начале файла (на 1 строке), то захватываем ещё несколько
                #     строк сверху и снизу (по пять)
                    code = requests.get(url=f'{URL}/api/sources/lines?key={component}&from={startLine-5}&to={endLine+5}', 
                                    cookies={'JWT-SESSION':jwt_token})
                else:
                    code = requests.get(url=f'{URL}/api/sources/lines?key={component}&from={startLine}&to={endLine+5}', 
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
                        
                # чтобы код внутри pdf отображался корректно, и не было смещений
                # добавляем переносы строк, пока количество строк кода не будет равно 11
                if countLineOfCode < 11:
                    while countLineOfCode != 11:
                        code += '\n'
                        countLineOfCode += 1

            discription = issue["message"]
            typeOfIssue = issue["type"]

            if typeOfIssue != 'CODE_SMELL':
            
                if pieceOfCode != None:
                    finallReport.write(f"Серьёзность: {severity}, Компонент: {component}, Начальная строка: {startLine}, Конечная строка: {endLine}, Участок кода:\n{code}, Описание: {discription}, Тип: {typeOfIssue}\n")
                    
                else:
                    finallReport.write(f"Серьёзность: {severity}, Компонент: {component}, Описание: {discription}, Тип: {typeOfIssue}\n")

        finallReport.close()



    

    

    


    









    
    



    
