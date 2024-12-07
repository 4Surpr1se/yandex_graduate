import logging

import aiohttp
from yookassa.client import ApiClient
from yookassa.domain.common import RequestObject
from aiohttp_retry import RetryClient, ExponentialRetry
from yookassa.domain.exceptions import ApiError, BadRequestError, ForbiddenError, NotFoundError, \
    ResponseProcessingError, TooManyRequestsError, UnauthorizedError, InternalServerError


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class AsyncApiClient(ApiClient):
    async def request(self, method="", path="", query_params=None, headers=None, body=None):
        """
        Подготовка запроса.

        :param method: HTTP метод
        :param path: URL запроса
        :param query_params: Массив GET параметров запроса
        :param headers: Массив заголовков запроса
        :param body: Тело запроса
        :rtype: str
        """
        if isinstance(body, RequestObject):
            body.validate()
            body = dict(body)

        request_headers = self.prepare_request_headers(headers)

        try:
            raw_response = await self.execute(body, method, path, query_params, request_headers)
        except aiohttp.ClientResponseError as e:
            logger.exception(e)
            self.__handle_error(e.status, e.message)
        except Exception as e:
            logger.exception(e)

        if raw_response.status != 200:
            self.__handle_error(raw_response.status, raw_response.json())

        return await raw_response.json()

    async def execute(self, body, method, path, query_params, request_headers):
        """
        Выполнение запроса.

        :param body: Тело запроса
        :param method: HTTP метод
        :param path: URL запроса
        :param query_params: Массив GET параметров запроса
        :param request_headers: Массив заголовков запроса
        :return: Response
        """

        retry_options = ExponentialRetry(methods={'POST'},
                                         statuses={429, 500, 502, 503, 504, 202},
                                         attempts=self.max_attempts)
        async with RetryClient(retry_options=retry_options) as session:

            self.log_request(body, method, path, query_params, request_headers)

            async with session.request(
                method=method,
                url=self.endpoint + path,
                params=query_params,
                headers=request_headers,
                json=body,
                ssl=self.configuration.verify
            ) as raw_response:

                self.log_response(raw_response.content, self.get_response_info(raw_response), raw_response.headers)

        return raw_response

    @staticmethod
    def get_response_info(response):
        """
        Получение информации из ответа.

        :param response: Объект ответа
        :return: dict[str, Any]
        """
        return {
            "cookies": response.cookies,
            "encoding": response.get_encoding,
            "ok": response.ok,
            "raise_for_status": response.raise_for_status(),
            "reason": response.reason,
            "status_code": response.status,
            "url": response.url,
        }

    @staticmethod
    def __handle_error(http_code, json_response):
        """
        Выбрасывает исключение по коду ошибки.
        """
        if http_code == BadRequestError.HTTP_CODE:
            raise BadRequestError(json_response)
        elif http_code == ForbiddenError.HTTP_CODE:
            raise ForbiddenError(json_response)
        elif http_code == NotFoundError.HTTP_CODE:
            raise NotFoundError(json_response)
        elif http_code == TooManyRequestsError.HTTP_CODE:
            raise TooManyRequestsError(json_response)
        elif http_code == UnauthorizedError.HTTP_CODE:
            raise UnauthorizedError(json_response)
        elif http_code == ResponseProcessingError.HTTP_CODE:
            raise ResponseProcessingError(json_response)
        elif http_code == InternalServerError.HTTP_CODE:
            raise InternalServerError(json_response)
        else:
            raise ApiError(json_response)