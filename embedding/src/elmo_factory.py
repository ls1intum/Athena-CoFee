import os
from pathlib import Path
from allennlp.commands.elmo import ElmoEmbedder
from logging import getLogger
import owncloud
import threading
from enum import Enum
from src.cloud.cloud_connection import CloudConnection


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
    ELMo_to_last_updated = {}

    cloud = CloudConnection.get_cloud_connection()

    def __init__(self):
        pass

    @staticmethod
    def __fetch_remote_model(file_name):
        try:
            ELMoFactory.__logger.info("fetching remote model {}".format(file_name))
            if file_name in ELMoFactory.ELMo_to_status and ELMoFactory.ELMo_to_status[file_name] == FileStatus.Fetching:
                return
            ELMoFactory.ELMo_to_status[file_name] = FileStatus.Fetching
            if os.path.exists((ELMoFactory.__RESOURCE_PATH / file_name).resolve()):
                os.remove((ELMoFactory.__RESOURCE_PATH / file_name).resolve())
            success = ELMoFactory.cloud.get_file(CloudConnection.remote_models_path + "/" + file_name,
                                                 (ELMoFactory.__RESOURCE_PATH / file_name).resolve())
            if success:
                ELMoFactory.ELMo_to_status[file_name] = FileStatus.Ready
                ELMoFactory.ELMo_to_last_updated[file_name] = ELMoFactory.__fetch_remote_model_update_time(file_name)
                if file_name in ELMoFactory.ELMo_models_cache:
                    del ELMoFactory.ELMo_models_cache[file_name]
                ELMoFactory.__logger.info("successfully loaded remote model {}".format(file_name))
            else:
                del ELMoFactory.ELMo_to_status[file_name]
                ELMoFactory.__logger.info("model {} was not found remotely".format(file_name))

        except owncloud.HTTPResponseError:
            del ELMoFactory.ELMo_to_status[file_name]
            ELMoFactory.__logger.warning("unable to load model {}".format(file_name))

    @staticmethod
    def __fetch_remote_model_update_time(file_name):
        try:
            info = ELMoFactory.cloud.file_info(CloudConnection.remote_models_path + "/" + file_name)
            if info is not None:
                ELMoFactory.__logger.info("successfully loaded metadata of model {}".format(file_name))
                return info.get_last_modified()
            else:
                ELMoFactory.__logger.info("model {} was not found remotely".format(file_name))
        except owncloud.HTTPResponseError:
            ELMoFactory.__logger.error("unable to load metadata of model {}".format(file_name))
        return None

    @staticmethod
    def __update_model(file_name):
        if ELMoFactory.ELMo_to_last_updated[file_name] != ELMoFactory.__fetch_remote_model_update_time(file_name):
            ELMoFactory.__fetch_remote_model(file_name)

    @staticmethod
    def __course_id_to_file_name(course_id):
        file_name = "weights_course_{}.hdf5".format(course_id)

        if file_name not in ELMoFactory.ELMo_to_status:
            thr = threading.Thread(target=ELMoFactory.__fetch_remote_model, args=(file_name,))
            thr.start()
            return ELMoFactory.__DEFAULT_WEIGHT_FILE

        if ELMoFactory.ELMo_to_status[file_name] == FileStatus.Ready and \
                (ELMoFactory.__RESOURCE_PATH / file_name).resolve().exists():
            thr = threading.Thread(target=ELMoFactory.__update_model, args=(file_name,))
            thr.start()
            return file_name

        return ELMoFactory.__DEFAULT_WEIGHT_FILE

    def get_model_for_course(self, course_id=None):
        if course_id is None:
            model_name = self.__DEFAULT_WEIGHT_FILE
        else:
            model_name = ELMoFactory.__course_id_to_file_name(course_id)

        if model_name not in ELMoFactory.ELMo_models_cache:
            weights_path = (self.__RESOURCE_PATH / model_name).resolve()
            try:
                ELMoFactory.ELMo_models_cache[model_name] = ElmoEmbedder(ELMoFactory.__OPTIONS_PATH, weights_path)
            except FileNotFoundError:
                self.__logger.error("Model not found, Using default elmo model")
                return ElmoEmbedder(ELMoFactory.__OPTIONS_PATH, self.__DEFAULT_WEIGHT_FILE)

        self.__logger.info("Using the ELMo Model {}".format(model_name))
        return ELMoFactory.ELMo_models_cache[model_name]
