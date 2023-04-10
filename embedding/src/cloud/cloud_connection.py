from logging import getLogger
from owncloud import owncloud, HTTPResponseError
from .config import nextcloud_credentials, mode


class CloudConnection:
    __logger = getLogger(__name__)
    possible_modes = ["production", "test_server_1", "test_server_2", "test_server_3"]
    remote_models_path = "Athene/{}/models".format(mode)
    remote_training_data_path = "Athene/{}/training_data".format(mode)
    cloud = None

    @staticmethod
    def __establish_cloud_connection():
        if CloudConnection.cloud is None:
            CloudConnection.cloud = owncloud.Client("https://nextcloud.in.tum.de/")
            try:
                CloudConnection.cloud.login(nextcloud_credentials["login"], nextcloud_credentials["password"])
            except HTTPResponseError as e:
                CloudConnection.__logger.warning(
                    "(not critical) Connection to cloud failed. Please check your credentials.")


    @staticmethod
    def __get_course_id_from_remote_path(remote_path):
        remote_path = remote_path.replace(CloudConnection.remote_training_data_path + '/course_', "")
        remote_path = remote_path.replace("/", "")
        return remote_path

    @staticmethod
    def get_available_course_ids():
        CloudConnection.__establish_cloud_connection()
        course_paths = list(
            map(lambda file: file.path, CloudConnection.cloud.list(CloudConnection.remote_training_data_path)))
        return list(map(lambda path: CloudConnection.__get_course_id_from_remote_path(path), course_paths))

    @staticmethod
    def get_cloud_connection():
        if mode not in CloudConnection.possible_modes:
            raise Exception("mode {} is not implemented. Possible modes are {}".format(mode, CloudConnection.possible_modes))
        CloudConnection.__establish_cloud_connection()
        return CloudConnection.cloud

    @staticmethod
    def upload_file(file_name, file_data, course_id):
        try:
            CloudConnection.__establish_cloud_connection()
            course_dir_remote_path = CloudConnection.remote_training_data_path + "/" + "course_{}".format(course_id)
            if course_id not in CloudConnection.get_available_course_ids():
                CloudConnection.cloud.mkdir(course_dir_remote_path)
            new_file_remote_path = course_dir_remote_path + "/" + file_name
            CloudConnection.cloud.put_file_contents(new_file_remote_path, file_data)
            return new_file_remote_path
        except HTTPResponseError as e:
            CloudConnection.__logger.error("upload of file {} failed. Please check the connection to the cloud".format(file_name))
