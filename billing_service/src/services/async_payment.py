# -*- coding: utf-8 -*-
import uuid

from yookassa import Payment
from yookassa.domain.common import HttpVerb
from yookassa.domain.request import CapturePaymentRequest, PaymentRequest
from yookassa.domain.response import PaymentListResponse, PaymentResponse

from src.services.async_yookassa import AsyncApiClient


class AsyncPayment(Payment):
    """
    Класс, представляющий модель Payment, работающую асинхронно.
    """  # noqa: E501

    def __init__(self):
        self.client = AsyncApiClient()

    @classmethod
    async def find_one(cls, payment_id) -> PaymentResponse:
        """
        Возвращает информацию о платеже

        :param payment_id: Уникальный идентификатор платежа
        :return: PaymentResponse Объект ответа, возвращаемого API при запросе платежа
        """
        instance = cls()
        if not isinstance(payment_id, str) or not payment_id:
            raise ValueError('Invalid payment_id value')

        path = instance.base_path + '/' + payment_id
        response = await instance.client.request(HttpVerb.GET, path)
        return PaymentResponse(response)

    @classmethod
    async def create(cls, params, idempotency_key=None):
        """
        Создание платежа

        :param params: Данные передаваемые в API
        :param idempotency_key: Ключ идемпотентности
        :return: PaymentResponse Объект ответа, возвращаемого API при запросе платежа
        """
        instance = cls()
        path = cls.base_path

        if not idempotency_key:
            idempotency_key = uuid.uuid4()

        headers = {
            'Idempotence-Key': str(idempotency_key)
        }

        if isinstance(params, dict):
            params_object = PaymentRequest(params)
        elif isinstance(params, PaymentRequest):
            params_object = params
        else:
            raise TypeError('Invalid params value type')

        params_object = instance.add_default_cms_name(params_object)

        response = await instance.client.request(HttpVerb.POST, path, None, headers, params_object)
        return PaymentResponse(response)

    @classmethod
    async def capture(cls, payment_id, params=None, idempotency_key=None):
        """
        Подтверждение платежа

        :param payment_id: Уникальный идентификатор платежа
        :param params: Данные передаваемые в API
        :param idempotency_key: Ключ идемпотентности
        :return: PaymentResponse Объект ответа, возвращаемого API при запросе платежа
        """
        instance = cls()
        if not isinstance(payment_id, str) or not payment_id:
            raise ValueError('Invalid payment_id value')

        path = instance.base_path + '/' + payment_id + '/capture'

        if not idempotency_key:
            idempotency_key = uuid.uuid4()

        headers = {
            'Idempotence-Key': str(idempotency_key)
        }

        if isinstance(params, dict):
            params_object = CapturePaymentRequest(params)
        elif isinstance(params, CapturePaymentRequest):
            params_object = params
        else:
            params_object = None

        response = await instance.client.request(HttpVerb.POST, path, None, headers, params_object)
        return PaymentResponse(response)

    @classmethod
    async def cancel(cls, payment_id, idempotency_key=None):
        """
        Отмена платежа

        :param payment_id: Уникальный идентификатор платежа
        :param idempotency_key: Ключ идемпотентности
        :return: PaymentResponse Объект ответа, возвращаемого API при запросе платежа
        """
        instance = cls()
        if not isinstance(payment_id, str) or not payment_id:
            raise ValueError('Invalid payment_id value')

        if not idempotency_key:
            idempotency_key = uuid.uuid4()

        path = instance.base_path + '/' + payment_id + '/cancel'
        headers = {
            'Idempotence-Key': str(idempotency_key)
        }
        response = await instance.client.request(HttpVerb.POST, path, None, headers)
        return PaymentResponse(response)

    @classmethod
    async def list(cls, params=None):
        """
        Возвращает список платежей

        :param params: Данные передаваемые в API
        :return: PaymentListResponse Объект ответа, возвращаемого API при запросе списка платежей
        """
        if params is None:
            params = {}
        instance = cls()
        path = cls.base_path

        response = await instance.client.request(HttpVerb.GET, path, params)
        return PaymentListResponse(response)
