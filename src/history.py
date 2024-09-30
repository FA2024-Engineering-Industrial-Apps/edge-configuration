
class History:
    
    def __init__(self):
        self.promtHistory = []

    def addPromt_withDict(self, promt:dict):
        self.promtHistory.append(dict)

    def addPromt_withStrs(self, role:str, message:str):
        self.promtHistory.append({"role": role, "content": message})
    
    