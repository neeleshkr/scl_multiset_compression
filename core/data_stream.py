import abc
import tempfile
import os
import typing
from core.data_block import DataBlock

Symbol = typing.Any


class DataStream(abc.ABC):
    """abstract class to represent a Data Stream

    The DataStream facilitates the block interface.
    From the interface standpoint, the two functions which are useful are:
    - get_block(block_size) -> returns a DataBlock of the given block_size from the stream
    - write_block(block) -> writes the block of data to the stream

    The DataStream can act as a stream object for both writing and reading blocks
    The two more useful sub-classes of the abstract class are FileDataStream and ListDataStream.
    (see their description for more details)
    """

    @abc.abstractmethod
    def reset(self):
        """resets the data stream"""
        pass

    @abc.abstractmethod
    def get_symbol(self):
        """returns a symbol from the data stream, returns None if the stream is finished

        This is an abstract method, and hence needs to be implemented by the subclasses
        """
        pass

    def get_block(self, block_size: int) -> DataBlock:
        """returns a block of data (of the given max size) from the stream

        get_block function tries to return a block of size `block_size`.
        In case the remaining stream is shorter, a smaller block will be returned

        Args:
            block_size (int): the (max) size of the block of data to be returned.

        Returns:
            DataBlock:
        """
        # returns the next data block
        data_list = []
        for _ in range(block_size):
            # get next symbol
            s = self.get_symbol()
            if s is None:
                break
            data_list.append(s)

        # if data_list is empty, return None to signal the stream is over
        if not data_list:
            return None

        return DataBlock(data_list)

    @abc.abstractmethod
    def write_symbol(self, s):
        """writes the given symbol to the stream

        The symbol can be appropriately converted to a particular format before writing.
        This is an abstract method and so, the subclass will have to implement it

        Args:
            s (Any): symbol to be written to the stream
        """
        pass

    def write_block(self, data_block: DataBlock):
        """write the input block to the stream

        Args:
            data_block (DataBlock): block to be written to the stream
        """
        for s in data_block.data_list:
            self.write_symbol(s)

    def __enter__(self):
        """function executed while opening the context

        See: https://realpython.com/python-with-statement/. More details in FileDataStream.__enter__ docstring
        """
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Function executed which exiting the context

        Note that the arguments exc_type, exc_value, exc_traceback are as required by python for a context
        """
        pass


class ListDataStream(DataStream):
    """
    ListDataStream is a wrapper around a list of symbols.
    It is useful to:
    - extract data from the list block by block
    - write data to the list block by block

    In practice, this class might be used mainly for testing
    (as usually you would read data from a file.. see FileDataStream for that)
    """

    def __init__(self, input_list: typing.List):
        """initialize with input_list and reset the stream

        Args:
            input_list (List): the list of symbols, around which the class is a wrapper

        Usage:
            with ListDataStream(input_list) as ds:
                block = ds.get_block(block_size=5)
                # do something with the block
        """
        # assert whether the input_list is indeed a list
        assert isinstance(input_list, list)
        self.input_list = input_list

        # reset counter
        self.reset()

    def reset(self):
        """resets the current_ind counter"""
        self.current_ind = 0

    def get_symbol(self) -> Symbol:
        """returns the next symbol from the self.input_list"""

        # retrieve the next symbol
        if self.current_ind >= len(self.input_list):
            return None
        s = self.input_list[self.current_ind]

        # increment the current_ind counter
        self.current_ind += 1
        return s

    def write_symbol(self, s: Symbol):
        """adds a symbol to the stream"""
        self.input_list.append(s)


class FileDataStream(DataStream):
    """Abstract class to create a data stream from a File

    The FileDataStream defines __exit__, __enter__ methods on top of DataStream.
    These methods handle file obj opening/closing

    Subclasses (eg: TextDataStream) need to imeplement methods get_symbol, write_symbol
    to get a functional object.
    """

    def __init__(self, file_path: str, permissions="r"):
        """Initialize the FileDataStream object

        Args:
            file_path (str): path of the file to read from/write to
            permissions (str, optional): Permissions to open the file obj. Use "r" to read, "w" to write to
            (other pyhton file obj permissions also can be used). Defaults to "r".
        """
        self.file_path = file_path
        self.permissions = permissions

    def __enter__(self):
        """open the file object context based on the permissions specified

        NOTE: One way of cleanly managing resources in python is using the with statement
        as shown in the example below. This ensures the resource is released when exiting the context.

        One way to support allow using with statement is defining __enter__ and __exit__ statements,
        which allow for executing functions while entering or exiting the context.
        Reference: https://realpython.com/python-with-statement/

        Example:
        with TextFileDataStream(path, "w") as fds:
            # get a text block
            block = fds.get_block(5)

        """
        self.file_obj = open(self.file_path, self.permissions)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """close the file object at the end of context"""
        self.file_obj.close()

    def reset(self):
        """resets the file object to the beginning"""
        self.file_obj.seek(0)


class TextFileDataStream(FileDataStream):
    """FileDataStream to read/write text data"""

    def get_symbol(self):
        """get the next character from the text file

        as we read character data from file by default, the get_symbol function does not need to do anything special
        conversions

        Returns:
            (str, None): the next character, None if we reached the end of stream
        """
        s = self.file_obj.read(1)
        if not s:
            return None
        return s

    def write_symbol(self, s):
        """write a character to the text file"""
        self.file_obj.write(s)


class Uint8FileDataStream(FileDataStream):
    """reads Uint8 numbers written to a file

    FIXME: need to immplement
    """

    pass


#################################


def test_list_data_stream():
    """simple testing function to check if list data stream is getting generated correctly"""
    input_list = list(range(10))
    with ListDataStream(input_list) as ds:
        for i in range(3):
            block = ds.get_block(block_size=3)
            assert block.size == 3

        block = ds.get_block(block_size=2)
        assert block.size == 1

        block = ds.get_block(block_size=2)
        assert block is None


def test_file_data_stream():
    """function to test file data stream"""

    # create a temporary file
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_file_path = os.path.join(tmpdirname, "tmp_file.txt")

        # write data to the file
        data_gt = DataBlock(list("This_is_a_test_file"))
        with TextFileDataStream(temp_file_path, "w") as fds:
            fds.write_block(data_gt)

        # read data from the file
        with TextFileDataStream(temp_file_path, "r") as fds:
            block = fds.get_block(block_size=4)
            assert block.size == 4
