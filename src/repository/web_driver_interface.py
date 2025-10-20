
from abc import ABC, abstractmethod

class WebDriverInterface(ABC):
    """Web Driver Interface to ensure compatibility with multiple different driver libraries"""
    @abstractmethod
    def get(self, url: str):
        pass

    @abstractmethod
    def get_original_page(self):
        pass

    @abstractmethod
    def find_elements(self, value: str, by: str, action: dict):
        pass

    @abstractmethod
    def find_element(self, by: str, value: str, action: dict):
        pass

    @abstractmethod
    def click_element(self, element: any):
        pass

    @abstractmethod
    def type_input(self, action: dict, element: any):
        pass

    @abstractmethod
    def dropdown_select(self, action: dict, element: any):
        pass

    @abstractmethod
    def upload(self, value: str, element: any):
        pass

    @abstractmethod
    def switch_window(self):
        pass

    @abstractmethod
    def return_to_original_window(self):
        pass

    @abstractmethod
    def close(self):
        pass