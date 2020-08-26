import subprocess
import typer
from enum import Enum
import csv
import configparser
import os
import time
import math
import shutil
import fileinput


app = typer.Typer()

# READ CONFIG
config = configparser.ConfigParser()
config.read('edgenet_cli.conf')

GENERAL_PRODUCTION_CONFIG_PATH = config['GENERAL']['PRODUCTION_CONFIG_PATH']
GENERAL_DEPLOY_NAME= config['GENERAL']['DEPLOY_NAME']
GENERAL_VERSION = config['GENERAL']['VERSION']
GENERAL_VERSION_CONF_FILE = config['GENERAL']['VERSION_CONF_FILE']
BACKEND_PODS_PER_BACKEND = int(config['BACKEND']['PODS_PER_BACKEND'])
BACKEND_START_BACKEND_PORT = int(config['BACKEND']['START_BACKEND_PORT'])
SLICES_NAMESPACES_NAMES = config['SLICES']['NAMESPACES_NAMES']
SLICES_DAEMONSET_START_INDEX = int(config['SLICES']['DAEMONSET_START_INDEX'])
SLICES_DAEMONSET_END_INDEX = int(config['SLICES']['DAEMONSET_END_INDEX'])

# COMPUTED CONSTANTS
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return int(i + 1)

try:
    NUMBER_OF_NODES = file_len('data/nodes_clean.csv')
    NUMBER_OF_BACKENDS = math.ceil(NUMBER_OF_NODES / BACKEND_PODS_PER_BACKEND)
except FileNotFoundError:
    pass


class createOptions(str, Enum):
    node_list = "nodes"
    config_files = "config"

class removeOptions(str, Enum):
    config_files = "config"
    data = "data"
    all_data = "all" 

class deployOptions(str, Enum):
    config = "configmaps"
    daemonsets = "daemonsets"

class deleteOptions(str, Enum):
    config = "configmaps"
    daemonsets = "daemonsets"
    pods_force = "pods-force"

class getOptions(str, Enum):
    config = "configmaps"
    daemonsets = "daemonsets"
    pods = "pods"


@app.command()
def create(option: createOptions):
    if option == createOptions.node_list:
        typer.echo(f"Creating node list file...")
        if create_node_list():
            typer.secho("Node list file created!", fg=typer.colors.GREEN, bold=False)
        else:
            typer.secho("Node list file creation failed!", fg=typer.colors.RED, bold=True)
    elif option == createOptions.config_files:
        typer.echo(f"Creating config files...")
        create_config_files()

@app.command()
def remove(option: removeOptions):
    if option == removeOptions.config_files:
        remove_config_files()
        typer.secho("All config files removed!", fg=typer.colors.GREEN, bold=False)
    elif option == removeOptions.data:
        remove_data_files()
        typer.secho("All data files removed!", fg=typer.colors.GREEN, bold=False)
    elif option == removeOptions.all_data:
        remove_config_files()
        remove_data_files()
        typer.secho("All files removed!", fg=typer.colors.GREEN, bold=False)

@app.command()
def deploy(option: deployOptions, namespace: str = typer.Option('all')):
    if option == deployOptions.config:
        if namespace == 'all':
            namespaces = SLICES_NAMESPACES_NAMES.split(',')
            deploy_config(namespaces)
        else:
            namespaces = [namespace]
            deploy_config(namespaces)
    elif option == deployOptions.daemonsets:
        if namespace == 'all':
            namespaces = SLICES_NAMESPACES_NAMES.split(',')
            deploy_daemonsets(namespaces)
        else:
            namespaces = [namespace]
            deploy_daemonsets(namespaces)

@app.command()
def delete(option: deleteOptions, namespace: str = typer.Option('all')):
    if option == deleteOptions.config:
        if namespace == 'all':
            namespaces = SLICES_NAMESPACES_NAMES.split(',')
            delete_config(namespaces)
        else:
            namespaces = [namespace]
            delete_config(namespaces)
    elif option == deleteOptions.daemonsets:
        if namespace == 'all':
            namespaces = SLICES_NAMESPACES_NAMES.split(',')
            delete_daemonsets(namespaces)
        else:
            namespaces = [namespace]
            delete_daemonsets(namespaces)
    elif option == deleteOptions.pods_force:
        if namespace == 'all':
            namespaces = SLICES_NAMESPACES_NAMES.split(',')
            delete_pods(namespaces)
        else:
            namespaces = [namespace]
            delete_pods(namespaces)

@app.command()
def get(option: getOptions, namespace: str = typer.Option('all')):
    if option == getOptions.config:
        if namespace == 'all':
            namespaces = SLICES_NAMESPACES_NAMES.split(',')
            get_config(namespaces)
        else:
            namespaces = [namespace]
            get_config(namespaces)
    elif option == getOptions.daemonsets:
        if namespace == 'all':
            namespaces = SLICES_NAMESPACES_NAMES.split(',')
            get_daemonsets(namespaces)
        else:
            namespaces = [namespace]
            get_daemonsets(namespaces)
    elif option == getOptions.pods:
        if namespace == 'all':
            namespaces = SLICES_NAMESPACES_NAMES.split(',')
            get_pods(namespaces)
        else:
            namespaces = [namespace]
            get_pods(namespaces)


# CREATE FUNCTIONS
def create_node_list():
    folder = './data'
    nodes_data_file_path = f'{folder}/nodes.data'
    nodes_data_file_path_clean = f'{folder}/nodes_clean.csv'
    if not os.path.exists(folder):
        os.makedirs(folder)
    status = subprocess.run(f"kubectl get nodes -o wide > {nodes_data_file_path}", shell=True)
    if status.returncode != 0:
        return False
    parse_node_list(nodes_data_file_path, nodes_data_file_path_clean)
    return True

def create_config_files():
    daemonset_dir = f'{GENERAL_PRODUCTION_CONFIG_PATH}/daemonsets'
    if not os.path.exists(daemonset_dir):
        os.makedirs(daemonset_dir)

    typer.secho(f"Number of nodes: {NUMBER_OF_NODES}", fg=typer.colors.MAGENTA, bold=True)
    typer.secho(f"Pods per backend: {BACKEND_PODS_PER_BACKEND}", fg=typer.colors.MAGENTA, bold=True)
    typer.secho(f"Number of backends: {NUMBER_OF_BACKENDS}", fg=typer.colors.MAGENTA, bold=True)

    create_deploy_folders()

    copy_config_files()
    typer.secho("Files copied!", fg=typer.colors.GREEN, bold=False)

    edit_config_names()

    nodes_name_list = read_node_names()
    edit_daemonset_files(nodes_name_list)
    typer.secho("Config created!", fg=typer.colors.GREEN, bold=False)

# REMOVE FUNCTIONS
def remove_config_files():
    subprocess.run(f'rm -rf {GENERAL_PRODUCTION_CONFIG_PATH}', shell=True)

def remove_data_files():
    subprocess.run(f'rm -rf ./data', shell=True)

# DEPLOY FUNCTIONS
def deploy_config(namespaces):
    for namespace in namespaces:
        path = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config'

        for deploy_num in range(1, NUMBER_OF_BACKENDS + 1):
            COWRIE_CONFIG_CFG= f'cowrie-cowrie-cfg-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
            COWRIE_CONFIG_CFG_DIST= f'cowrie-cowrie-cfg-dist-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
            FILEBEAT_CONFIG= f'cowrie-filebeat1-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
            COWRIE_USERDB_EXAMPLE= f'cowrie-userdb-example-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
            COWRIE_USERDB_TXT= f'cowrie-userdb-txt-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
            deploy_config_subprocess(path, deploy_num, COWRIE_CONFIG_CFG, namespace)
            deploy_config_subprocess(path, deploy_num, COWRIE_CONFIG_CFG_DIST, namespace)
            deploy_config_subprocess(path, deploy_num, FILEBEAT_CONFIG, namespace)
            deploy_config_subprocess(path, deploy_num, COWRIE_USERDB_EXAMPLE, namespace)
            deploy_config_subprocess(path, deploy_num, COWRIE_USERDB_TXT, namespace)
            time.sleep(1)

        typer.secho(f"Config deploy for namespace {namespace} finished!", fg=typer.colors.GREEN, bold=True)

def deploy_daemonsets(namespaces):
    if len(namespaces) > 1:
        number_of_namespaces = len(namespaces) 
        nodes = list(range(1, NUMBER_OF_NODES + 1))
        nodes_splited = chunk_it(nodes, number_of_namespaces)
        for index, chunk in enumerate(nodes_splited):
            for node_id in chunk:
                deploy_daemonset_subproces(node_id, namespaces[index])
    else:
        namespace = namespaces[0]
        for node_id in range(SLICES_DAEMONSET_START_INDEX, SLICES_DAEMONSET_END_INDEX + 1):
            deploy_daemonset_subproces(node_id, namespace)

# DELETE FUNCTIONS
def delete_config(namespaces):
    for namespace in namespaces:
        typer.secho(f"--- Namespace: {namespace}", bold=True)
        configmaps = get_configmaps_for_namespace(namespace)
        for configmap in configmaps:
            delete_config_subprocess(configmap, namespace)
    typer.secho(f"All configmaps deleted!", fg=typer.colors.GREEN, bold=True)

def delete_daemonsets(namespaces):
    for namespace in namespaces:
        typer.secho(f"--- Namespace: {namespace}", bold=True)
        daemonsets = get_daemonset_for_namespace(namespace)
        for daemonset in daemonsets:
            delete_daemonset_subprocess(daemonset, namespace)
    typer.secho(f"All daemonsets deleted!", fg=typer.colors.GREEN, bold=True)

def delete_pods(namespaces):
    for namespace in namespaces:
        typer.secho(f"--- Namespace: {namespace}", bold=True)
        pods = get_pods_for_namespace(namespace)
        for pod in pods:
            delete_pods_subprocess(pod, namespace)
    typer.secho(f"All pods deleted (by force)!", fg=typer.colors.GREEN, bold=True)

# GET FUNCTIONS
def get_config(namespaces):
    for namespace in namespaces:
        typer.secho(f"--- Configmpas for namespace: {namespace}", bold=True)
        configmaps = get_configmaps_for_namespace(namespace)
        for configmap in configmaps:
            typer.secho(f"{configmap}", bold=False)

def get_daemonsets(namespaces):
    for namespace in namespaces:
        typer.secho(f"--- Daemonsets for namespace: {namespace}", bold=True)
        daemonsets = get_daemonset_for_namespace(namespace)
        for daemonset in daemonsets:
            typer.secho(f"{daemonset}", bold=False)

def get_pods(namespaces):
    for namespace in namespaces:
        typer.secho(f"--- Pods for namespace: {namespace}", bold=True)
        pods = get_pods_for_namespace(namespace)
        for pod in pods:
            typer.secho(f"{pod}", bold=False)

# HELPER FUNCTIONS
def parse_node_list(file_path, clean_file_path):
    # read the file to list
    with open(file_path, 'r') as f:
        nodes_file_raw = f.readlines()

    # transform lines to csv format
    with open(clean_file_path, 'w') as csvFile:
        for line in nodes_file_raw:
            clean_lines = line.split()
            if clean_lines[1] == 'Ready':
                if not clean_lines[5].startswith('2001:'):
                    writer = csv.writer(csvFile)
                    row = [clean_lines[0], clean_lines[5]]
                    writer.writerow(row)

def create_deploy_folders():
    for deploy_num in range(1, NUMBER_OF_BACKENDS + 1):
        path = f"/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config/conf-0{str(deploy_num)}-{GENERAL_DEPLOY_NAME}"
        try:
            os.mkdir(path)
        except OSError:
            typer.secho(f"Creation of the directory {path} failed", fg=typer.colors.RED, bold=True)

def copy_config_files():
    for deploy_num in range(1, NUMBER_OF_BACKENDS + 1):
        path_src = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/general_config'
        path_dst = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config'
        shutil.copy2(f'{path_src}/cowrie-cowrie-cfg-dist-config-version-num.yaml', f'{path_dst}/conf-0{deploy_num}-{GENERAL_DEPLOY_NAME}/cowrie-cowrie-cfg-dist-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}.yaml')
        shutil.copy2(f'{path_src}/cowrie-cowrie-cfg-config-version-num.yaml', f'{path_dst}/conf-0{deploy_num}-{GENERAL_DEPLOY_NAME}/cowrie-cowrie-cfg-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}.yaml')
        shutil.copy2(f'{path_src}/cowrie-filebeat1-config-version-num.yaml', f'{path_dst}/conf-0{deploy_num}-{GENERAL_DEPLOY_NAME}/cowrie-filebeat1-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}.yaml')
        shutil.copy2(f'{path_src}/cowrie-userdb-example-config-version-num.yaml', f'{path_dst}/conf-0{deploy_num}-{GENERAL_DEPLOY_NAME}/cowrie-userdb-example-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}.yaml')
        shutil.copy2(f'{path_src}/cowrie-userdb-txt-config-version-num.yaml', f'{path_dst}/conf-0{deploy_num}-{GENERAL_DEPLOY_NAME}/cowrie-userdb-txt-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}.yaml')

def read_node_names():
    nodes_list = []
    with open('data/nodes_clean.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            nodes_list.append(row[0].strip())

    return nodes_list   

def edit_config_names():
    port = BACKEND_START_BACKEND_PORT
    for deploy_num in range(1, NUMBER_OF_BACKENDS + 1):
        typer.secho(f"Edited config files: Deploy number: {deploy_num} |  Port number: {port}", fg=typer.colors.YELLOW, bold=False)
        edit_cowrie_cfg_file(deploy_num, port)
        edit_cowrie_cowrie_cfg_dist_config(deploy_num)
        edit_cowrie_userdb_example_config(deploy_num)
        edit_cowrie_userdb_txt_config(deploy_num)
        edit_cowrie_filebeat1_config(deploy_num)
        port = port + 1

def edit_cowrie_cfg_file(deploy_num, port):
    path = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config'
    filename = f'{path}/conf-0{deploy_num}-{GENERAL_DEPLOY_NAME}/cowrie-cowrie-cfg-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}.yaml'
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'backend_ssh_port = XXXXX'
        replacement_text = f'backend_ssh_port = {port}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

    # name: cowrie-cowrie-cfg-config-vXX-XX
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'name: cowrie-cowrie-cfg-config-vXX-XX'
        replacement_text = f'name: cowrie-cowrie-cfg-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

def edit_cowrie_cowrie_cfg_dist_config(deploy_num):
    path = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config'
    filename = f'{path}/conf-0{deploy_num}-{GENERAL_DEPLOY_NAME}/cowrie-cowrie-cfg-dist-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}.yaml'

    # name: cowrie-cowrie-cfg-dist-config-vXX-XX
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'name: cowrie-cowrie-cfg-dist-config-vXX-XX'
        replacement_text = f'name: cowrie-cowrie-cfg-dist-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

def edit_cowrie_userdb_example_config(deploy_num):
    path = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config'
    filename = f'{path}/conf-0{deploy_num}-{GENERAL_DEPLOY_NAME}/cowrie-userdb-example-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}.yaml'

    # name: cowrie-userdb-example-config-vXX-XX
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'name: cowrie-userdb-example-config-vXX-XX'
        replacement_text = f'name: cowrie-userdb-example-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

def edit_cowrie_userdb_txt_config(deploy_num):
    path = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config'
    filename = f'{path}/conf-0{deploy_num}-{GENERAL_DEPLOY_NAME}/cowrie-userdb-txt-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}.yaml'

    # name: cowrie-userdb-txt-config-vXX-XX
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'name: cowrie-userdb-txt-config-vXX-XX'
        replacement_text = f'name: cowrie-userdb-txt-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

def edit_cowrie_filebeat1_config(deploy_num):
    path = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config'
    filename = f'{path}/conf-0{deploy_num}-{GENERAL_DEPLOY_NAME}/cowrie-filebeat1-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}.yaml'

    # name: cowrie-filebeat1-config-vXX-XX
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'name: cowrie-filebeat1-config-vXX-XX'
        replacement_text = f'name: cowrie-filebeat1-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='') 

def copy_deamonset_file(deamonset_num):
    path_src = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/general_config'
    path_dst = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config/daemonsets'
    shutil.copy2(f'{path_src}/daemonset-deploy.yaml', f'{path_dst}/daemonset-deploy-v{GENERAL_VERSION_CONF_FILE}-0{str(deamonset_num)}.yaml')

def edit_demonset_deploy_file(deamonset_num, node):
    path = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config/daemonsets'
    filename = f'{path}/daemonset-deploy-v{GENERAL_VERSION_CONF_FILE}-0{str(deamonset_num)}.yaml'

    # replace name deamonset values
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'name: cowrie-deamonset-vXX-XX-XX'
        replacement_text = f'name: cowrie-deamonset-v{GENERAL_VERSION_CONF_FILE}-0{deamonset_num}-{GENERAL_DEPLOY_NAME}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')


    # replace nodes names
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'kubernetes.io/hostname: node_name'
        
        replace_str ='kubernetes.io/hostname: ' + node
        replacement_text = replace_str
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

def edit_demonset_deploy_file_volumes(filename, deploy_num):
    # name: cowrie-cowrie-cfg-config-vXX-XX
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'name: cowrie-cowrie-cfg-config-vXX-XX'
        replacement_text = f'name: cowrie-cowrie-cfg-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

    # name: cowrie-cowrie-cfg-dist-config-vXX-XX
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'name: cowrie-cowrie-cfg-dist-config-vXX-XX'
        replacement_text = f'name: cowrie-cowrie-cfg-dist-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

    # name: cowrie-userdb-example-config-vXX-XX
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'name: cowrie-userdb-example-config-vXX-XX'
        replacement_text = f'name: cowrie-userdb-example-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

    # name: cowrie-userdb-txt-config-vXX-XX
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'name: cowrie-userdb-txt-config-vXX-XX'
        replacement_text = f'name: cowrie-userdb-txt-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

    # name: cowrie-filebeat1-config-vXX-XX
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        text_to_search = 'name: cowrie-filebeat1-config-vXX-XX'
        replacement_text = f'name: cowrie-filebeat1-config-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

def edit_daemonset_files(nodes_list):
    # create config_numbered_list
    config_numbered_list = []
    for i in range(1, NUMBER_OF_BACKENDS + 1):
        for j in range(BACKEND_PODS_PER_BACKEND):
            config_numbered_list.append(i)

    config_numbered_list_clean = config_numbered_list[0:NUMBER_OF_NODES].copy()

    for deamonset_num, node in enumerate(nodes_list):
        deamonset_num = deamonset_num + 1 
        copy_deamonset_file(deamonset_num)
        edit_demonset_deploy_file(deamonset_num, node)

        path = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config/daemonsets'
        filename = f'{path}/daemonset-deploy-v{GENERAL_VERSION_CONF_FILE}-0{str(deamonset_num)}.yaml'
        edit_demonset_deploy_file_volumes(filename, config_numbered_list_clean[deamonset_num-1])
        typer.secho(f"Edited daemonset file: Deploy number: {deamonset_num} | Node: {node}", fg=typer.colors.YELLOW, bold=False)

def deploy_config_subprocess(path, deploy_num, config_name, namespace):
    config_path = f'{path}/conf-0{str(deploy_num)}-{GENERAL_DEPLOY_NAME}/{config_name}.yaml'
    KUBECTL_COMMAND = f'kubectl create -f {config_path} --namespace="{namespace}"'
    output = subprocess.run(KUBECTL_COMMAND, shell=True, stdout=subprocess.PIPE)
    if output.returncode == 0:
        typer.secho(f"Config file deployed: {config_name}!", fg=typer.colors.GREEN, bold=False)
    else:
        typer.secho(f"Config file deploy failed! {config_name}!", fg=typer.colors.RED, bold=True)

def get_configmaps_for_namespace(namespace):
    result = subprocess.run(f'kubectl get configmaps --namespace="{namespace}"', stdout=subprocess.PIPE, shell=True)
    result = result.stdout.decode('utf-8')
    results = [config.split()[0] for config in result.split('\n')[1:-1]]
    return results

def delete_config_subprocess(configmap_name, namespace):
    KUBECTL_COMMAND = f'kubectl delete configmap {configmap_name.strip()} --namespace="{namespace.strip()}"'
    output = subprocess.run(KUBECTL_COMMAND, shell=True, stdout=subprocess.PIPE)
    if output.returncode == 0:
        typer.secho(f"Configmap deleted: {configmap_name}!", fg=typer.colors.GREEN, bold=False)
    else:
        typer.secho(f"Configmap delete failed! {configmap_name}!", fg=typer.colors.RED, bold=True)
    time.sleep(0.5)

def get_daemonset_for_namespace(namespace):
    result = subprocess.run(f'kubectl get daemonsets --namespace="{namespace}"', stdout=subprocess.PIPE, shell=True)
    result = result.stdout.decode('utf-8')
    results = [daemonset.split()[0] for daemonset in result.split('\n')[1:-1]]
    return results

def get_pods_for_namespace(namespace):
    result = subprocess.run(f'kubectl get pods --namespace="{namespace}"', stdout=subprocess.PIPE, shell=True)
    result = result.stdout.decode('utf-8')
    results = [pod.split()[0] for pod in result.split('\n')[1:-1]]
    return results

def delete_daemonset_subprocess(daemonset_name, namespace):
    KUBECTL_COMMAND = f'kubectl delete daemonset {daemonset_name.strip()} --namespace="{namespace.strip()}"'
    output = subprocess.run(KUBECTL_COMMAND, shell=True, stdout=subprocess.PIPE)
    if output.returncode == 0:
        typer.secho(f"Daemonset deleted: {daemonset_name}!", fg=typer.colors.GREEN, bold=False)
    else:
        typer.secho(f"Daemonset delete failed! {daemonset_name}!", fg=typer.colors.RED, bold=True)
    time.sleep(0.5)

def delete_pods_subprocess(pod_name, namespace):
    KUBECTL_COMMAND = f'kubectl delete pods {pod_name.strip()} --grace-period=0 --force --namespace="{namespace.strip()}"'
    output = subprocess.run(KUBECTL_COMMAND, shell=True, stdout=subprocess.PIPE)
    if output.returncode == 0:
        typer.secho(f"Pod deleted: {pod_name}!", fg=typer.colors.GREEN, bold=False)
    else:
        typer.secho(f"Pod delete failed! {pod_name}!", fg=typer.colors.RED, bold=True)
    time.sleep(0.5)

def chunk_it(a, n):
    k, m = divmod(len(a), n)
    return list((a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)))

def deploy_daemonset_subproces(deploy_num, namespace):
    path = f'/home/administrator/cowrie-k8s-deploy-edgenet/cowrie_deployment_v{GENERAL_VERSION}/prod_config/daemonsets'
    DAEMONSET_FILE= f'daemonset-deploy-v{GENERAL_VERSION_CONF_FILE}-0{str(deploy_num)}'
    FROM_FILE = f'{path}/{DAEMONSET_FILE}.yaml'
    KUBECTL_COMMAND = f'kubectl apply -f {FROM_FILE} --namespace="{namespace}"'
    print(KUBECTL_COMMAND)
    output = subprocess.run(KUBECTL_COMMAND, shell=True, stdout=subprocess.PIPE)
    if output.returncode == 0:
        typer.secho(f"Daemonset file deployed: {DAEMONSET_FILE}!", fg=typer.colors.GREEN, bold=False)
    else:
        typer.secho(f"Daemonset file deploy failed! {DAEMONSET_FILE}!", fg=typer.colors.RED, bold=True)


if __name__ == "__main__":
    app()



