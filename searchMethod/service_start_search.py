import os
import shutil
import uuid

import pandas as pd
import requests
from flask import Flask, request

from myInputCli import index_cli
from ucSearchBase import run_local_search

app = Flask(__name__)

environment_name = os.getenv("ENVIRONMENT", "production")

print(environment_name)

configurations = {
    "production": {
        "config_root_dir": "/rag-prod",
        "output_root_dir": "/rag-prod/output/"
    },
    "development": {
        "config_root_dir": "../ragtest",
        "output_root_dir": "../ragtest/output/"
    }
}

OUTPUT_ROOT_DIR = configurations[environment_name]["output_root_dir"]
CONFIG_ROOT_DIR = configurations[environment_name]["config_root_dir"]

print(environment_name)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    # 提供模型切换的参数
    libraryId = data.get('libraryId', OUTPUT_ROOT_DIR)
    # root_dir = data.get('root_dir', '/default/root/dir')
    communityLevel = data.get('communityLevel', 1)
    # response_type = data.get('response_type', 'json')
    query = data.get('query', '')

    res = run_local_search(
        data_dir=OUTPUT_ROOT_DIR + libraryId + "/artifacts",
        root_dir=CONFIG_ROOT_DIR,
        community_level=communityLevel,
        response_type="json",
        query=query
    )
    return res, 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/search', methods=['POST'])
def search():
    data = request.json
    # 提供模型切换的参数
    roleId = data.get('roleId', '')
    sessionId = data.get('sessionId', '')
    communityLevel = data.get('communityLevel', 2)
    query = data.get('query', '')
    callBackFlag = data.get('callBackFlag', 'false')
    tools = data.get('tools', '')
    role_dir_path = OUTPUT_ROOT_DIR + roleId + sessionId
    if not os.path.exists(role_dir_path):
        sessionId = ''
    res = run_local_search(
        data_dir=OUTPUT_ROOT_DIR + roleId + sessionId + "/artifacts",
        root_dir=CONFIG_ROOT_DIR,
        community_level=communityLevel,
        response_type="json",
        call_ball=callBackFlag,
        tools=tools,
        query=query
    )
    resultData = {"sessionId": sessionId,
                  "data": res}
    return resultData, 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/inputData', methods=['POST'])
def inputData():
    data = request.json
    # 提供模型切换的参数
    roleId = data.get('roleId', OUTPUT_ROOT_DIR)
    inputData = data.get('inputData', '')
    knowledge_file_url = data.get('knowledgeFileUrl', '')
    sessionId = data.get('sessionId', '')
    print("inputDataRoleId:" + roleId + "_" + sessionId)

    role_path = roleId + sessionId
    role_path_temp = role_path + "temp"

    # 下载文件
    if knowledge_file_url is not None and knowledge_file_url != '':
        inputData += _download_file(knowledge_file_url)

    data = {
        'text': [inputData],
        'id': [uuid.uuid4().__str__()],
        'title': [uuid.uuid4().__str__()]
    }

    dataset = pd.DataFrame(data)
    print(dataset)
    # dataset = dataset if dataset is not None else await _create_input(config.input)

    res = index_cli(
        root=CONFIG_ROOT_DIR,
        verbose=False,
        resume=role_path_temp,
        memprofile=False,
        nocache=False,
        reporter='none',
        config=None,
        emit=None,
        dryrun=False,
        init=False,
        dataset=dataset,
        overlay_defaults=False
    )

    if res == 'success':
        role_dir_path = OUTPUT_ROOT_DIR + role_path
        role_dir_path_temp = OUTPUT_ROOT_DIR + role_path_temp
        # 检查目标目录是否存在
        if os.path.exists(role_dir_path):
            shutil.rmtree(role_dir_path)
        shutil.copytree(OUTPUT_ROOT_DIR + role_path_temp, OUTPUT_ROOT_DIR + role_path)
        if os.path.exists(role_dir_path_temp):
            shutil.rmtree(role_dir_path_temp)

    return res, 200, {'Content-Type': 'application/json; charset=utf-8'}


'''传入 file_url 下载该文件'''
def _download_file(
        file_url: str
) -> str:
    txt = requests.get(file_url, 'charset=utf-8')
    txt.encoding = 'uft-8'
    if txt.status_code == 200:
        return txt.text
    else:
        print("download oss file error")
        raise requests.exceptions.RequestException("文件下载发生异常")


if __name__ == '__main__':
    print("服务启动成功")
    app.run(host='0.0.0.0')
