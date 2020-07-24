from logging import getLogger
import yaml
import os.path
import requests
from .entities import ComputeNode

class ConfigParser:
    __logger = getLogger(__name__)
    compute_nodes = list()

    def checkComputeNode(self, url):
        try:
            requests.post(url, timeout=5)
        except Exception as e:
            #self.__logger.warning("Compute node did not respond: {}".format(str(e)))
            return False
        return True

    def addComputeNode(self, compute_node):
        if self.checkComputeNode(compute_node.url):
            self.compute_nodes.append(compute_node)
            self.__logger.info("Parsed Compute Node definition - " + str(compute_node))
        else:
            self.__logger.warning("Skipping Compute Node definition because it seems to be down - " + str(compute_node))

    def parseConfig(self):
        # Read config.yml file
        try:
            filepath = str(os.environ['CONFIG_FILE_PATH']) if "CONFIG_FILE_PATH" in os.environ else "src/config.yml"
            with open(filepath, 'r') as stream:
                config = yaml.safe_load(stream)
        except Exception as e:
            self.__logger.error("Error reading config: " + str(e))
            return

        self.compute_nodes = list()
        # Parse docker nodes
        if 'docker_nodes' in config:
            for node in config['docker_nodes']:
                required_variables = ('traefik_service_api', 'embedding_route', 'chunk_size', 'compute_power', 'communication_cost')
                if not all(key in node for key in required_variables):
                    self.__logger.warning("Skipping Docker Node definition. Not all required variables set: " + str(node))
                    self.__logger.warning("Required variables are: " + str(required_variables))
                    continue
                try:
                    # Query traefik API
                    traefik_services = requests.get(node['traefik_service_api'], timeout=5).json()
                    for i, server in enumerate(traefik_services['loadBalancer']['servers']):
                        new_node = ComputeNode(name='traefik_'+str(i), url=str(server['url'])+str(node['embedding_route']),
                                               chunk_size=int(node['chunk_size']),
                                               compute_power=int(node['compute_power']),
                                               communication_cost=int(node['communication_cost']))
                        self.addComputeNode(new_node)
                except Exception as e:
                    self.__logger.error("Error during config parsing: " + str(e))

        # Parse standalone nodes
        if 'compute_nodes' in config:
            for node in config['compute_nodes']:
                required_variables = ('name', 'url', 'chunk_size', 'compute_power', 'communication_cost')
                if not all(key in node for key in required_variables):
                    self.__logger.warning("Skipping Compute Node definition. Not all required variables set: " + str(node))
                    self.__logger.warning("Required variables are: " + str(required_variables))
                    continue
                try:
                    new_node = ComputeNode(name=str(node['name']), url=str(node['url']), chunk_size=int(node['chunk_size']),
                                           compute_power=int(node['compute_power']),
                                           communication_cost=int(node['communication_cost']))
                    self.addComputeNode(new_node)
                except Exception as e:
                    self.__logger.error("Error during config parsing: " + str(e))

        return self.compute_nodes
