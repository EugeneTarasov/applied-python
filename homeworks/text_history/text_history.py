from abc import ABC, abstractmethod


class TextHistory:
    def __init__(self, text=''):
        self._text = text
        self._version = 0
        self._version_history = []

    # текущий текст, read only
    @property
    def text(self):
        return self._text

    # текущая версия, read only
    @property
    def version(self):
        return self._version

    def insert(self, text, pos=None):
        """
        Вставить текст с позиции pos.
        Кидает ValueError, если указана недопустимая позиция
        :param text: вставить текст text
        :param pos: вставить текст с позиции pos (по умолчанию — конец строки)
        :return: номер новой версии
        """
        if pos is None:
            pos = len(self.text)
        action = InsertAction(text=text, pos=pos, from_version=self.version, to_version=self.version+1)
        self._version_history.append(action)
        self._text = action.apply(self.text)
        self._version += 1
        return self.version

    def replace(self, text, pos=None):
        """
        Заменить текст с позиции pos
        Кидает ValueError, если указана недопустимая позиция.
        Замена за пределами строки работает как вставка (т. е. текст дописывается).
        :param text: заменить текст на text
        :param pos: заменить текст с позиции pos (по умолчанию — конец строки)
        :return: номер новой версии
        """
        if pos is None:
            pos = len(self.text)
        action = ReplaceAction(text=text, pos=pos, from_version=self.version, to_version=self.version+1)
        self._version_history.append(action)
        self._text = action.apply(self.text)
        self._version += 1
        return self.version

    def delete(self, pos, length):
        """
        Удаляет length символов начиная с позиции pos
        :param pos: удаляет символ начиная с позиции pos
        :param length: удаляет length (количество символов)
        :return: номер новой версии
        """
        action = DeleteAction(pos=pos, length=length, from_version=self.version, to_version=self.version+1)
        self._version_history.append(action)
        self._text = action.apply(self.text)
        self._version += 1
        return self.version

    def action(self, action):
        """
        Применяет действие action
        Версия растет не на 1, а устанавливается та, которая указана в action.
        :param action: действие action
        :return: номер новой версии
        """
        if action.from_version >= action.to_version:
            raise ValueError
        self._text = action.apply(self.text)
        self._version = action.to_version
        return self.version

    def get_actions(self, from_version=0, to_version=None):
        if to_version is None:
            to_version = self.version
        if (from_version < 0) or (from_version > to_version) or \
                (from_version > self.version) or (to_version > self.version):
            raise ValueError
        return self._version_history[from_version:to_version]


class Action(ABC):
    def __init__(self, pos=None, text='', length=0, from_version=0, to_version=1):
        self.pos = pos
        self.text = text
        self.length = length
        if from_version < 0 or from_version > to_version:
            raise ValueError
        self.from_version = from_version
        self.to_version = to_version

    @abstractmethod
    def apply(self, input_str):
        pass


class InsertAction(Action):
    def apply(self, input_str):
        if self.pos is None:
            output_str = input_str + self.text
        elif (self.pos >= 0) & (self.pos <= len(input_str)):
            output_str = input_str[:self.pos] + self.text + input_str[self.pos:]
        else:
            raise ValueError
        return output_str


class ReplaceAction(Action):
    def apply(self, input_str):
        if self.pos is None:
            output_str = input_str + self.text
        elif (self.pos >= 0) and (self.pos <= len(input_str)):
            output_str = input_str[:self.pos] + self.text + input_str[(self.pos + len(self.text)):]
        else:
            raise ValueError
        return output_str


class DeleteAction(Action):
    def apply(self, input_str):
        if self.pos is None:
            output_str = input_str
        elif (self.pos >= 0) and (self.pos <= len(input_str)) and (len(input_str) >= self.pos + self.length):
            output_str = input_str[:self.pos] + input_str[(self.pos + self.length):]
        else:
            raise ValueError
        return output_str
