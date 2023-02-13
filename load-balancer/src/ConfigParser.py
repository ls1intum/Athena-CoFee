from .entities import NodeType, ComputeNode
from logging import getLogger
import os.path
import requests
import yaml

# Class to parse config file including compute node definitions
class ConfigParser:
    __logger = getLogger(__name__)
    compute_nodes = list()

    # Checks if a compute node is up and returns a boolean
    def checkComputeNode(self, url):
        try:
            requests.get(url, timeout=5)
        except Exception:
            return False
        return True

    # Adds a compute node to the compute node list, if it is up. Otherwise skip adding it
    def addComputeNode(self, compute_node):
        if self.checkComputeNode(compute_node.url):
            self.compute_nodes.append(compute_node)
            self.__logger.info("Parsed Compute Node definition - " + str(compute_node))
        else:
            self.__logger.warning("Skipping Compute Node definition because it seems to be down - " + str(compute_node))

    # Parses provided config and returns a list of available compute nodes
    def parseConfig(self, node_type):
        # Read config.yml file
        try:
            filepath = str(os.environ['LOAD_BALANCER_CONFIG_FILE_PATH']) if "LOAD_BALANCER_CONFIG_FILE_PATH" in os.environ else "src/node_config.docker.yml"
            with open(filepath, 'r') as stream:
                config = yaml.safe_load(stream)
        except Exception as e:
            self.__logger.error("Error reading config: " + str(e))
            return

        self.compute_nodes = list()
        # Parse docker nodes using traefik API
        if 'docker_nodes' in config and node_type is not NodeType.gpu:
            for node in config['docker_nodes']:
                # Check if config is valid
                required_variables = ('traefik_service_api', 'trigger_route', node_type + '_service_name')
                if not all(key in node for key in required_variables):
                    self.__logger.warning("Skipping Docker Node definition. Not all required variables set: " + str(node))
                    self.__logger.warning("Required variables are: " + str(required_variables))
                    continue

                # Create nodes
                try:
                    # Query traefik API
                    traefik_services = requests.get(node['traefik_service_api'] + node[node_type + '_service_name'], timeout=5).json()
                    for i, server in enumerate(traefik_services['loadBalancer']['servers']):
                        new_node = ComputeNode(name='traefik_' + node_type + '_' + str(i), type=node_type, url=str(server['url'])+str(node['trigger_route']))
                        self.addComputeNode(new_node)
                except Exception as e:
                    self.__logger.error("Error during config parsing (docker nodes): " + str(e))

        # Parse standalone nodes
        if 'compute_nodes' in config:
            for node in config['compute_nodes']:
                # Check if config is valid
                if node_type == NodeType.gpu:
                    required_variables = ('name', 'type', 'trigger_url', 'trigger_username', 'trigger_password')
                else:
                    required_variables = ('name', 'type', 'trigger_url')
                if not all(key in node for key in required_variables):
                    self.__logger.warning("Skipping Compute Node definition. Not all required variables set: " + str(node))
                    self.__logger.warning("Required variables are: " + str(required_variables))
                    continue

                # Create nodes
                try:
                    if node['type'] == node_type:
                        new_node = ComputeNode(name=str(node['name']), type=node['type'], url=str(node['trigger_url']))
                        if node_type == NodeType.gpu:
                            new_node.username = node['trigger_username']
                            new_node.password = node['trigger_password']
                        self.addComputeNode(new_node)
                except Exception as e:
                    self.__logger.error("Error during config parsing (standalone nodes): " + str(e))

        return self.compute_nodes
