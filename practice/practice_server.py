# 导入Flask类
from flask import Flask, request
import json
import sys
sys.path.append("..")
import practice
from practice.strategy_two import send_test_again
from practice.strategy_one import process_initialization
from practice.strategy_one import every_interaction

# 实例化，可视为固定格式
app = Flask(__name__)

# route()方法用于设定路由；类似spring路由配置
@app.route('/test',methods = ['POST'])
def init_test():
    get_Data = request.get_data()  # 获取传入的参数
    receive_json = json.loads(get_Data, encoding='utf-8')  # 传入的参数为bytes类型，需要转化成json
    knowledge_ids = receive_json.get("knowledge_ids")
    knowledge_ids_num = len(knowledge_ids)

    if knowledge_ids_num <= 3:
        # "策略一"
        init_json = practice.strategy_one.process_initialization(receive_json)
        return init_json
    else:
        # "策略二"
        init_json = practice.strategy_two.process_initialization(receive_json)
        return init_json




@app.route('/practice',methods = ['POST'])
def prepare_practice():

    get_Data = request.get_data()  # 获取传入的参数
    receive_json = json.loads(get_Data, encoding='utf-8')  # 传入的参数为bytes类型，需要转化成json

    result = receive_json.get("result")
    knowledge_ids = [i.get("knowledge_ids") for i in result]
    knowledge_ids_list = [i[0] for i in knowledge_ids]
    knowledge_ids_num = len(list(set(knowledge_ids_list)))

    if knowledge_ids_num <= 3:
        # "策略一"
        send_json = every_interaction(receive_json)
        return send_json
    else:
        # "策略二"
        send_json = send_test_again(receive_json)
        return send_json


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)  # 测试环境
    # 请求地址:http://39.98.180.205:5002/test
    # 请求地址:http://39.98.180.205:5002/practice


    # app.run(host="10.29.49.95")
    # 请求地址:http://127.0.0.1:500/test
    # 请求地址:http://127.0.0.1:5000/practice
