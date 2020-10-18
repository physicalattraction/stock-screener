from abc import ABC
from typing import Any, Callable, Dict, List, Optional, Union
from unittest.mock import patch

import requests
from requests import RequestException, Response
from rest_framework import status

OptionalJSON = Union[list, dict, float, int, str, bool, None]
Headers = Dict[str, Union[str, int]]
Params = Dict[str, Union[str, int]]


def mock_head_call(return_value: OptionalJSON = None, side_effect: Any = None):
    if side_effect:
        return patch.object(BaseService, '_make_head_call', side_effect=side_effect)
    else:
        return patch.object(BaseService, '_make_head_call', return_value=return_value)


def mock_get_call(return_value: OptionalJSON = None, side_effect: Any = None):
    if side_effect:
        return patch.object(BaseService, '_make_get_call', side_effect=side_effect)
    else:
        return patch.object(BaseService, '_make_get_call', return_value=return_value)


def mock_post_call(return_value: OptionalJSON = None, side_effect: Any = None):
    if side_effect:
        return patch.object(BaseService, '_make_post_call', side_effect=side_effect)
    else:
        return patch.object(BaseService, '_make_post_call', return_value=return_value)


def mock_put_call(return_value: OptionalJSON = None, side_effect: Any = None):
    if side_effect:
        return patch.object(BaseService, '_make_put_call', side_effect=side_effect)
    else:
        return patch.object(BaseService, '_make_put_call', return_value=return_value)


class BaseService(ABC):

    # Default headers to add to any API call. Can be overwritten per Service, for instance to add authentication
    headers: Params = {}

    # Flag indicating whether the response should be parsed as JSON
    response_in_json: bool = True

    @classmethod
    def _make_head_call(cls, url: str, params: Params = None) -> Response:
        """
        Wrapper around a HEAD call returning the response
        """

        return requests.head(url=url, headers=cls.headers, params=params)

    @classmethod
    def _make_get_call(cls, url: str, params: Params = None, error_msg: str = None) -> OptionalJSON:
        """
        Wrapper around a GET call returning a JSON object

        :param url: URL to make the GET call to
        :param params: Query parameters of the GET call in JSON format (list or dict)
        :param error_msg: Error message to return if the call fails
        :return: JSON object (list or dict) returned by the GET call (if successful call)
        """

        response = requests.get(url=url, headers=cls.headers, params=params)
        return cls._process_response(response, error_msg)

    @classmethod
    def _make_post_call(cls, url: str, body: OptionalJSON, params: Params = None,
                        error_msg: str = None) -> OptionalJSON:
        """
        Wrapper around a POST call returning a JSON object

        :param url: URL to make the POST call to
        :param body: Body of the POST call in JSON format (list or dict)
        :param params: Query parameters of the GET call in JSON format (list or dict)
        :param error_msg: Error message to return if the call fails
        :return: JSON object (list or dict) returned by the POST call (if successful call)
        """

        response = requests.post(url=url, json=body, headers=cls.headers, params=params)
        return cls._process_response(response, error_msg)

    @classmethod
    def _make_put_call(cls, url: str, body: OptionalJSON, params: Params = None,
                       error_msg: str = None, files=None) -> OptionalJSON:
        """
        Wrapper around a PUT call returning a JSON object

        :param url: URL to make the PUT call to
        :param body: Body of the PUT call in JSON format (list or dict)
        :param params: Query parameters of the PUT call
        :param error_msg: Error message to return if the call fails
        :param files: a dictionary in the following format:  {'file': (filename, contents)}
               If this argument is filled, the request is sent as
               a multipart request. If not, the request is sent as a JSON request.
        :return: JSON object (list or dict) returned by the PUT call (if successful call)
        """

        if files:
            response = requests.put(url=url, data=body, headers=cls.headers, params=params, files=files)
        else:
            response = requests.put(url=url, json=body, headers=cls.headers, params=params)
        return cls._process_response(response, error_msg)

    @classmethod
    def _make_delete_call(cls, url: str, body: OptionalJSON = None, params: Params = None,
                          error_msg: str = None) -> OptionalJSON:
        """
        Wrapper around a DELETE call returning a JSON object

        :param url: URL to make the DELETE call to
        :param body: Body of the DELETE call in JSON format (list or dict)
        :param params: Query parameters of the DELETE call
        :param error_msg: Error message to return if the call fails
        :return: JSON object (list or dict) returned by the DELETE call (if successful call)
        """

        response = requests.delete(url=url, headers=cls.headers, data=body, params=params)
        return cls._process_response(response, error_msg)

    @classmethod
    def _process_response(cls, response: Response, error_msg: Optional[str]) -> OptionalJSON:
        if status.is_success(response.status_code):
            if cls.response_in_json:
                return cls._optional_json(response)
            else:
                return response.text.strip()
        if not error_msg:
            error_msg = f'Error from {response.url}'
        msg = f'{error_msg}. Status code: {response.status_code}. Response: {response.text}'
        raise RequestException(msg)

    @classmethod
    def _process_paginated_results(cls, data: Dict, result_processor: Callable, error_msg: Optional[str]) -> List[Dict]:
        """
        Process a dictionary which represents paginated results
        """

        result = [result_processor(obj) for obj in data['results']]
        while data.get('next'):
            data = cls._make_get_call(url=data['next'], error_msg=error_msg)
            result.extend([result_processor(obj) for obj in data['results']])
        return result

    @staticmethod
    def _optional_json(response: Response) -> OptionalJSON:
        """
        If there is a response body, return as a JSON object. If not, return None
        """

        if response.text.strip():
            try:
                return response.json()
            except ValueError as e:
                msg = f'Response from {response.url} is invalid JSON: {response.text}'
                raise ValueError(msg) from e
        else:
            return None
