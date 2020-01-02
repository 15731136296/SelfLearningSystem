# 导入Flask类
from flask import Flask, request
import json
import sys
sys.path.append("..")
import practice
from practice.strategy_two import send_test_again
from practice.strategy_one import process_initialization


# 实例化，可视为固定格式
app = Flask(__name__)

# route()方法用于设定路由；类似spring路由配置
@app.route('/test',methods = ['POST', 'GET'])
def init_test():
    get_Data = request.get_data()  # 获取传入的参数
    receive_json = json.loads(get_Data, encoding='utf-8')  # 传入的参数为bytes类型，需要转化成json
    knowledge_ids = receive_json.get("knowledge_ids")
    knowledge_ids_num = len(knowledge_ids)

    if knowledge_ids_num <= 3:
        init_json = practice.strategy_one.process_initialization(receive_json)
        return init_json
    else:

        init_json = practice.strategy_two.process_initialization(receive_json)
    return init_json



@app.route('/practice',methods = ['POST','GET'])
def prepare_practice():

    get_Data = request.get_data()  # 获取传入的参数
    receive_json = json.loads(get_Data, encoding='utf-8')  # 传入的参数为bytes类型，需要转化成json

    result = receive_json.get("result")
    knowledge_ids = [i.get("knowledge_ids") for i in result]
    knowledge_ids_list = [i[0] for i in knowledge_ids]
    knowledge_ids_num = len(list(set(knowledge_ids_list)))

    if knowledge_ids_num <= 3:
        return "策略一"
    else:
        send_json = send_test_again(receive_json)
        return send_json


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5002)  # 测试环境
    app.run()

    # 请求地址:http://127.0.0.1:5000/test
    # 请求地址:http://127.0.0.1:5000/practice
