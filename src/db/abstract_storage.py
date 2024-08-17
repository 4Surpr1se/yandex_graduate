import abc


class AbstractDataStorage(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, *args, **kwargs):
        """Получение элемента из хранилища по идентификатору"""

    @abc.abstractmethod
    async def get_list(self, *args, **kwargs):
        """Получение множества объектов по запросу"""


class AbstractCache(abc.ABC):
    @abc.abstractmethod
    async def get(self, *args, **kwargs):
        """Получение элемента из кеша"""

    @abc.abstractmethod
    async def set(self, *args, **kwargs):
        """Сохранение элемента в кеш"""
