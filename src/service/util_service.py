# import getpass
import glob
import os.path
import logging
import datetime as dt
import asyncio
# import time
import random

from settings import PROJECT_ROOT
# import distutils

def get_logger(name="app", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(
        logging.Formatter("%(levelname)s - %(name)s - %(message)s")
    )
    logger.addHandler(console_handler)
    return logger

logger = get_logger(__name__)
import sys
import platform
import os

import signal
from settings import config
from src.service.nodriver_service import NoDriverService
from src.service.selenium_service import SeleniumUndetectableDriverService

drivers = {
    'selenium': SeleniumUndetectableDriverService,
    'nodriver': NoDriverService
}
# get the driver from config or default to nodriver library
MyDriver = drivers[config.get('driver', 'nodriver')]

class CustomDriver(MyDriver):
    """This class abstracts away the external driver initialization logic"""
    def __init__(self, timeout=5):
        super().__init__(sleep, implicit_wait=timeout)
        # print(dir(self))

async def sleep(timeout):
    # max_range = timeout / 10
    min_range = .9 * timeout
    random_num = random.uniform(min_range, timeout)
    # sleep = timeout + random_num
    # time.sleep(random_num)
    await asyncio.sleep(random_num)

def get_date_range_tuple(relative_to=dt.datetime.today()):
    """Returns a tuple of datetimes for the previous Monday to the previous Sunday
    Example: Run on Thursday Jan 1, 2024. it would return ( 2024/01/01,  2024/01/07 )
    Example: Run on Monday Jan 8, 2024. it would return ( 2024/01/01,  2024/01/07 )
    Example: Run on Saturday Jan 13, 2024. it would return ( 2024/01/01,  2024/01/07 )
    """
    last_sunday = relative_to - dt.timedelta(days=relative_to.weekday() + 1)
    previous_monday = last_sunday - dt.timedelta(days=6)
    return previous_monday, last_sunday

def get_most_recent_downloaded_file(folder):
    # /Users/{getpass.getuser()}/Downloads/*
    list_of_files = glob.glob(folder)
    return max(list_of_files, key=os.path.getctime)


def check_path(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except PermissionError:
            output_folder = os.path.split(path)[0]
            logger.error(f'Permission denied to the output folder: {output_folder}')
            raise


###################################################### For Testing #####################################################
import pickle  # Barry
from functools import wraps  # Barry

def pickled_memoize(cache_dir=f'{PROJECT_ROOT}/pickle_cache'):
    check_path(cache_dir)

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # --- Argument & Cache Key Handling ---
            cache_key = kwargs.get('cache_key')
            if not cache_key:
                # Create a robust key from args and kwargs
                key_args_str = "_".join(map(str, args)) + "_" + "_".join(f"{k}{v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{func.__name__}_{hash(key_args_str)}.pkl"
            else:
                cache_key += ".pkl"

            cache_file_path = os.path.join(cache_dir, cache_key)

            result = func(self, *args, **kwargs)
            if not self.debug:
                return result
            if isinstance(result, list):
                cache_els = []
                for el in result:
                    cache_els.append(HtmlAttributes().set_element(el))
                write_pickle_file(cache_els, cache_file_path)
            else:
                cache_el = HtmlAttributes().set_element(result)
                write_pickle_file(cache_el, cache_file_path)
            return result
        return wrapper
    return decorator


def write_pickle_file(cacheable_data, file_path):
    """
    Write the data to pickle cache
    :param cacheable_data: data to be cached, any datatype
    :param file_path: path to cache file, str
    :return:
    """
    future_time = dt.datetime.now() + dt.timedelta(hours=24 * 3)

    # Convert the future_time datetime object to a Unix timestamp (seconds since epoch)
    # .timestamp() returns a float, so int() can be used for an integer timestamp
    future_timestamp = int(future_time.timestamp())
    data = {
        "cached_html": cacheable_data,
        "expiration_date": future_timestamp
    }
    logger = get_logger(__name__)
    output_folder = os.path.split(file_path)[0]

    check_path(output_folder)

    try:
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
    except PermissionError:
        logger.error(f'Permission denied to the output folder: {output_folder}')
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


# import inspect
# def add_sync_wrappers(cls):
#     """
#     Class decorator to find all '_async' methods and add
#     synchronous wrapper versions of them to the class.
#     """
#
#     def create_sync_wrapper(async_func):
#         async def wrapper(self, *args, **kwargs):
#             # 'self' is passed automatically
#             return await async_func(self, *args, **kwargs)#  asyncio.run(async_func(self, *args, **kwargs))
#
#         return wrapper
#
#     # Iterate over all members of the class
#     for name, func in inspect.getmembers(cls):
#         if name.endswith('_async') and inspect.iscoroutinefunction(func):
#             sync_name = name.split('_async')[0].lstrip('_')
#             # Add the new synchronous method to the class
#             print(sync_name)
#             setattr(cls, sync_name, create_sync_wrapper(func))
#
#     return cls

class HtmlElement:
    """
    Use this class to read the cached selenium element back into a
    selenium-like element for testing
    """
    pass

class HtmlAttributes:
    """
    Transform selenium element attributes to and from cacheable dictionary values
    """
    def __init__(self):
        self.__element = None
        self.attributes = {}
        attr_list = ['id', 'name', 'class', 'href', 'src', 'value', 'style', 'alt', 'innerHTML', 'outerHTML']
        for attr in attr_list:
            self.attributes[attr] = None
        self.funcs = ['is_displayed', 'is_enabled']
        self.builtin_values = ['text', 'tag_name', 'size', 'location']

    def set_element(self, element):
        """
        Transform the selenium attributes to key values to be cached
        :param element: selenium element, selenium.webdriver.remote.webelement.WebElement
        :return: cacheable dictionary, dict
        """
        el_dict = {}
        for attr in self.attributes.keys():
            el_dict[attr] = element.get_attribute(attr) #
        for f in self.funcs:
            method_to_call = getattr(element, f)
            el_dict[f] = method_to_call()
        for b in self.builtin_values:
            el_dict[b] = getattr(element, b)
            # setattr(self, f, method_to_call())
        self.__element = element
        return el_dict

    def get_attribute(self, attr):
        """
        mimic the selenium get_attribut method
        :param attr: attribute name
        :return: attribute value
        """
        return self.attributes[attr]

    def get_element(self, el_dict):
        """
        Transform the cached selenium element dictionary back into a selenium-like element
        """
        my_el = HtmlElement # initialize a class with no attributes
        setattr(my_el, 'get_attribute', self.get_attribute)

        for f in self.funcs:
            # method_to_call = el_dict[f]
            setattr(my_el, f,  lambda : el_dict[f])

        for b in self.builtin_values:
            setattr(my_el, b, el_dict[b])

        return my_el
