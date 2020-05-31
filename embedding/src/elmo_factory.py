from pathlib import Path
from allennlp.commands.elmo import ElmoEmbedder
from logging import getLogger
import owncloud
import threading
from enum import Enum


class FileStatus(Enum):
    Fetching = 1
    Ready = 2


class ELMoFactory:
    __logger = getLogger(__name__)
    __RESOURCE_PATH = (Path.cwd() / "src/resources/models").resolve()
    __OPTIONS_PATH = (__RESOURCE_PATH / "elmo_2x4096_512_2048cnn_2xhighway_5.5B_options.json").resolve()
    __DEFAULT_WEIGHT_FILE = "elmo_2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5"
    ELMo_models_cache = {}
    ELMo_to_status = {__DEFAULT_WEIGHT_FILE: FileStatus.Ready}
    cloud = owncloud.Client("https://nextcloud.in.tum.de/")
    remote_models_path = "Athene/models"

    def __init__(self):
        ELMoFactory.cloud.login('khachnao@in.tum.de', 'JaZP6-oN8sG-xyTxk-w6NGT-7MxC3')

    @staticmethod
    def __fetch_remote_model(file_name):
        try:
            ELMoFactory.__logger.info("fetching remote model {}".format(file_name))
            ELMoFactory.ELMo_to_status[file_name] = FileStatus.Fetching
            success = ELMoFactory.cloud.get_file(ELMoFactory.remote_models_path + "/" + file_name,
                                                 (ELMoFactory.__RESOURCE_PATH / file_name).resolve())
            if success:
                ELMoFactory.ELMo_to_status[file_name] = FileStatus.Ready
                ELMoFactory.__logger.info("successfully loaded remote model {}".format(file_name))
            else:
                del ELMoFactory.ELMo_to_status[file_name]
                ELMoFactory.__logger.info("model {} was not found remotely".format(file_name))

        except owncloud.HTTPResponseError:
            del ELMoFactory.ELMo_to_status[file_name]
            ELMoFactory.__logger.error("unable to load model {}".format(file_name))

    def __course_id_to_file_name(self, course_id):
        file_name = "weights_course_{}.hdf5".format(course_id)

        if file_name not in ELMoFactory.ELMo_to_status:
            thr = threading.Thread(target=ELMoFactory.__fetch_remote_model, args=(file_name,))
            thr.start()
            return ELMoFactory.__DEFAULT_WEIGHT_FILE

        if ELMoFactory.ELMo_to_status[file_name] == FileStatus.Ready and \
                (ELMoFactory.__RESOURCE_PATH / file_name).resolve().exists():
            return file_name

        return ELMoFactory.__DEFAULT_WEIGHT_FILE

    def get_model_for_course(self, course_id=None):
        if course_id is None:
            model_name = self.__DEFAULT_WEIGHT_FILE
        else:
            model_name = self.__course_id_to_file_name(course_id)

        if model_name not in ELMoFactory.ELMo_models_cache:
            weights_path = (self.__RESOURCE_PATH / model_name).resolve()
            ELMoFactory.ELMo_models_cache[model_name] = ElmoEmbedder(ELMoFactory.__OPTIONS_PATH, weights_path)

        self.__logger.info("Using the ELMo Model {}".format(model_name))
        return ELMoFactory.ELMo_models_cache[model_name]
