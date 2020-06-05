from owncloud import owncloud


class CloudConnection:
    remote_models_path = "Athene/models"
    remote_training_data_path = "Athene/training_data"
    cloud = None

    @staticmethod
    def __establish_cloud_connection():
        if CloudConnection.cloud is None:
            CloudConnection.cloud = owncloud.Client("https://nextcloud.in.tum.de/")
            CloudConnection.cloud.login('khachnao@in.tum.de', 'JaZP6-oN8sG-xyTxk-w6NGT-7MxC3')

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
        CloudConnection.__establish_cloud_connection()
        return CloudConnection.cloud

    @staticmethod
    def upload_file(file_name, file_data, course_id):
        CloudConnection.__establish_cloud_connection()
        course_dir_remote_path = CloudConnection.remote_training_data_path + "/" + "course_{}".format(course_id)
        if course_id not in CloudConnection.get_available_course_ids():
            CloudConnection.cloud.mkdir(course_dir_remote_path)
        new_file_remote_path = course_dir_remote_path + "/" + file_name
        CloudConnection.cloud.put_file_contents(new_file_remote_path, file_data)
        return new_file_remote_path
