import logging

from .generator import Generator

class Scheduling:
    def __init__(self, generator: Generator):
        self.generator = generator

    def is_scheduled(self, client_id: str, template_id: str | None = None) -> bool:
        function = '(aloha) Scheduling:is_scheduled'

        try:
            if client_id is None:
                raise TypeError("Missing client_id")
            if template_id is None:
                raise TypeError("Missing scheduling_template_id")

            scheduled = self.generator.generate_boolean(
                client_id=client_id,
                template_id=template_id)
            return scheduled
        except:
            logging.error(f'{function} unable to determine scheduling for {client_id} with template: {template_id}')
            return False
