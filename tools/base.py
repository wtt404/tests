from abc import ABC, abstractmethod


class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, *args, **kwargs):
        pass