from typing import List, Dict
from model.app_model import AppModel

class History:
    
    def __init__(self):
        self.promtHistory: List[Dict] = []
        self.configHistory: List[AppModel] = []

    def addSystemPromt(self, systemPromt):
        self.systemPromt = systemPromt

    def addPromt_withDict(self, promt:dict):
        self.promtHistory.append(dict)

    def addPromt_withStrs(self, role:str, message:str):
        self.promtHistory.append({"role": role, "content": message})

    def addConfig(self, config: AppModel):
        self.configHistory.append(config)
    
    def getPromtHistory(self) -> List[Dict]:
        return self.promtHistory
    
    def getPromtHistory_withoutSysPromts(self) -> List[Dict]:
        promtHistory_withoutSysPromts = []
        for promt in self.promtHistory:
            if promt["role"] != "system":
                promtHistory_withoutSysPromts += [promt]

        return promtHistory_withoutSysPromts
    
    def getLatestPromtAsStr(self, role:str = "any") -> str: 
        for promt in reversed(self.promtHistory):
            if promt["role"] == role or role == "any":
                return promt["content"]
        return ""
    
    def getLatestPromtAsDict(self, role:str = "any") -> Dict: 
        for promt in reversed(self.promtHistory):
            if promt["role"] == role or role == "any":
                return promt
        return ""
    
    def getLatestPromts(self, n:int = 1) -> List[Dict]: 
        return self.promtHistory[-n:]
    
    # TODO: improve and maybe put somewhere else
    def genConfigPromt(self, index):
        return {"role": "system", "content": "The current configuration is: " + self.configHistory[index].generate_prompt_string()}

    def genPromtForLLM(self, n_oldAnswerResponsePairs = 1) -> List[Dict]:
        """ Structure of promtHistory:
                [...]
                user: old promt
                Optional[system: old validationPromt]
                assistent: old response
                user: new promt
                Optional[system: new validationPromt]

            Wanted llmPromt for e.g. n_oldAnswerResponsePairs = 1:
                system: system promt
                system: very old config promt
                user: old promt
                Optional[system: old validationPromt]
                system: old config promt
                assistent: old response
                user: new promt
                Optional[system: new validationPromt]
                system: new config promt
        """

        
        llmPromt: List[Dict] = []

        if self.systemPromt:
            llmPromt.append({"role": "system", "content": self.systemPromt})
        
        index_promtHistory = -1
        index_configHistory = -1
        n_addedUserPromts = 0


        llmPromt.insert(1, self.genConfigPromt(index_configHistory))

        # adds as many promts from promtHistory to llmPromt as wanted through iterating backwards over promtHistory
        try:
            while n_addedUserPromts < n_oldAnswerResponsePairs + 1: # + 1 because new user promt should not be counted

                llmPromt.insert(1, self.promtHistory[index_promtHistory])
                if self.promtHistory[index_promtHistory]["role"] == "user":
                    n_addedUserPromts += 1
                if self.promtHistory[index_promtHistory]["role"] == "assistent":
                    llmPromt.insert(1, self.genConfigPromt(index_configHistory))
                index_promtHistory -= 1
        except IndexError:
            pass # stop adding to llmPromt at latest when end of promtHistory is reached
        llmPromt.insert(1, self.genConfigPromt(index_configHistory))

        return llmPromt
    

    def printPromtHistory(self):
        print("Promt History:")
        for promt in self.promtHistory:
            print(f"{promt['role']}: {promt['content']}")
        print("\n\n")

    def printConfigHistory(self):
        print("Config History:")
        for config in self.configHistory:
            print(config)
        print("\n\n")