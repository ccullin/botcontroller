from abc import ABC, abstractmethod

class webAPI_abstract(ABC):
 
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def registerController(self):
        pass
        
    @abstractmethod
    def subscribeBot(self):
        pass
    
    @abstractmethod
    def sendMessage(self):
        pass
