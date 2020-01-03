import pandas as pd
import redis
# host = "39.98.180.205"
# pool = redis.ConnectionPool(host=host, port=6379, db=1, decode_responses=True)
pool = redis.ConnectionPool(host='localhost', port=6379, db=1, decode_responses=True)
red = redis.Redis(connection_pool=pool)

"""
 策略二
        条件:知识点个数n大于3
        题量:25道

        第一层
        题量: 2n道只含一个知识点的题目

        第二层:
        排序策略:
            根据第一层的答题结果和答题时长进行排序.
            优先级:答错、答对（用时长）、答对（用时短）

            1、排序
            错-知识点错的次数
            对-停留时间过长
            对-停留时间正常
            （相同时按照出题顺序排序）

            2、知识点个数统计
            类型                  知识点个数统计
            1错题                      x
            2对题-停留时间过长           y
            3对题-停留时间正常           z
            (x+y+z=n)

        出题策略:
            当（25-2n）/x >2时,出题策略为 2x_1y_1z_组合
            当（25-2n）/x <2时,出题策略为 1x_1y_1z_组合
            当x=0时，出题策略为 1y_1z_组合
            注意: n的范围是 3<n<14，不存在25-2n）/x =2的情况，因为25为奇数

        难度策略:
        1）2x_1y_1z_组合
        2）1x_1y_1z_组合
        3）1y_1z_组合
        y:简单
        z:难
        x:简单和难分情况
            1）2x_1y_1z_组合，其中 x: 2错——2简; 1对1错——1简1难
            2）1x_1y_1z_组合，其中 x: 1错——1简。
"""

def get_test_df():

    """
    获得清洗后的题库
    :return:  type：dataframe
    """
    path3 = "../test_library_info/test_info_clear.csv"
    # path3 = "../test_library_info/test_info_clear_test.csv"#完美测试集
    test_df = pd.read_csv(path3)
    return test_df


def init_test_set(test_df, knowledge_ids):

    """
    备选集 初始化题目
    :param test_df:
    :param knowledge_ids:
    :return:
    """

    df_0 = []
    df_90 = []
    knowledge_ids_num = len(knowledge_ids)

    for i in range(knowledge_ids_num):
        df_recall_0 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[i])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_90 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[i])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]
        df_0.append(df_recall_0)
        df_90.append(df_recall_90)

        # 组合题
    df_recall_group_0 = test_df[
        (test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] > 1) & (
                test_df["difficulty"] == 0)]
    df_recall_group_90 = test_df[
        (test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] > 1) & (
                test_df["difficulty"] == 90)]

    return df_0, df_90, df_recall_group_0, df_recall_group_90


def init_test(df_0, df_90, knowledge_ids_num):
    # 备选集 初始化题目
    init_df = pd.DataFrame()
    for i in range(knowledge_ids_num):
        df_recall_0 = df_0[i]
        df_recall_90 = df_90[i]
        if df_recall_0.empty and df_recall_90.shape[0] > 1:
            init_test = df_recall_90.sample(2, replace=False)  # 要是没有的话，重复出题。
        elif df_recall_0.shape[0] > 1:
            init_test = df_recall_0.sample(2, replace=False)  # 要是没有的话，重复出题。

        init_df = init_df.append(init_test)
    init_df = init_df.reset_index(drop=True)  # 重置索引
    # 修改列名
    # init_df =init_df.rename({"ids_split": "knowledge_ids"})
    # 暂定数据格式
    init_df.index += 1  #索引从1开始
    init_json = init_df[["test_id", "ids_split"]].to_json(orient='index', force_ascii=False)
    location_ids_num = init_df.shape[0]
    return init_json, location_ids_num


def process_initialization(init_json):

    """
    发送初始化题目
    :param init_json: 前段发送数据
    :return: type:json
    """

    user_id = init_json.get("user_id")
    practice_id = init_json.get("practice_id")
    subject_id = init_json.get("subject_id")  # 学科-数学
    department_id = init_json.get("department_id")  # 小学
    grade_ids = init_json.get("grade_ids")  # 年级
    textbook = init_json.get("textbook")  # 教材
    chapter = init_json.get("chapter")  # 章
    knowledge_ids = init_json.get("knowledge_ids")  # 章节\章节——叶子知识点
    # 自己加载,根据用户id获取
    time_threshold = 30  # 初始化准备,加载学生信息。没有的话,设定一个值time_threshold = 60
    # init = [user_id, practice_id, subject_id, department_id, grade_ids, textbook, chapter]

    test_df = get_test_df()

    knowledge_ids = [str(i) for i in knowledge_ids]
    knowledge_ids_num = len(knowledge_ids)
    # 初始化练习题的数据范围
    df_0, df_90, df_recall_group_0, df_recall_group_90 = init_test_set(test_df, knowledge_ids)
    df_recall_group = df_recall_group_0.append(df_recall_group_90)

    # 第一层
    # 题量: 25
    # n道只含一个知识点的题目
    init_json, location_ids_num = init_test(df_0, df_90, knowledge_ids_num)
    # location_ids_num 为实际发送题目解析返回数据

    df_0_dict = {}
    for i, j in enumerate(df_0):
        df_0_dict[str(i)] = j.to_dict()
    df_90_dict = {}
    for i, j in enumerate(df_90):
        df_90_dict[str(i)] = j.to_dict()
    knowledge_ids_num = len(knowledge_ids)

    dict_test = {"practice_id": practice_id, "knowledge_ids_num": knowledge_ids_num,
                 "location_ids_num":location_ids_num, "time_threshold": time_threshold,
                 "df_0": df_0_dict,"df_90": df_90_dict, "df_recall_group": df_recall_group.to_dict()}
    # dict_test["knowledge_ids"] = ",".join([str(i) for i in init_json["knowledge_ids"]])#降低redis版本后可以存列表的数据了
    red.hmset(str(practice_id), dict_test)#保存到redis
    #返回数据
    json = {"status": 0, "message": "success", "result": {"user_id": user_id, "practice_id": practice_id, "data": eval(init_json)}}
    return json


def sorting_result(df_receive_results, time_threshold):

    """
    解析返回数据receive_json()
    """

    knowledge_ids_list = df_receive_results["knowledge_ids"].to_list()
    knowledge_ids_list = list(set(knowledge_ids_list))

    is_true_count = df_receive_results.groupby("knowledge_ids")["is_true"].sum().reset_index(name='count')
    is_true_count = is_true_count.sort_values("count")

    x_false_knowledge_ids_list = is_true_count[is_true_count["count"] < 2]["knowledge_ids"].to_list()
    true_knowledge_ids_list = is_true_count[is_true_count["count"] == 2]["knowledge_ids"].to_list()
    true_knowledge_ids_df = df_receive_results[(df_receive_results["knowledge_ids"].isin(true_knowledge_ids_list))]
    # 初始化准备,加载学生信息。没有的话,设定一个值time_threshold = 60

    if time_threshold is None:
        time_threshold = 60
    y_true_knowledge_ids_list = true_knowledge_ids_df[true_knowledge_ids_df["time_consuming"] > time_threshold][
        "knowledge_ids"].to_list()
    z_true_knowledge_ids_list = list(
        set(knowledge_ids_list) - set(x_false_knowledge_ids_list) - set(y_true_knowledge_ids_list))
    return [x_false_knowledge_ids_list, y_true_knowledge_ids_list, z_true_knowledge_ids_list]



def xyz_test(x_false_knowledge_ids_list,y_true_knowledge_ids_list,z_true_knowledge_ids_list, knowledge_ids,df_0,df_90,df_recall_group,location_ids_num,n=None, m=1, k=1):
    if x_false_knowledge_ids_list:
        for i in x_false_knowledge_ids_list:

            index = knowledge_ids.index(i)

            if df_0[index].shape[0] > 1:
                df_recall_x = df_0[index].sample(n)
    else:
        df_recall_x = pd.DataFrame()

    if y_true_knowledge_ids_list:
        for i in y_true_knowledge_ids_list:

            index = knowledge_ids.index(i)
            if df_0[index].shape[0] > 0:
                df_recall_y = df_0[index].sample(m)
    else:
        df_recall_y = pd.DataFrame()

    if z_true_knowledge_ids_list:
        for i in z_true_knowledge_ids_list:
            index = knowledge_ids.index(i)
            if df_90[index].shape[0] > 0:
                df_recall_z = df_90[index].sample(k)
    else:
        df_recall_z = pd.DataFrame()

    new_test_df = pd.concat([df_recall_x, df_recall_y, df_recall_z], axis=0, ignore_index=True)

    group_num = 25 - location_ids_num - new_test_df.shape[0]


    # 修改判断个数

    df_recall_group = df_recall_group.sample(group_num, replace=True)  # 随机选择,
    new_test_df = new_test_df.append(df_recall_group)


    new_test_df = new_test_df.reset_index(drop=True)
    new_json = new_test_df[["test_id", "ids_split"]]

    return new_json


def init(init_json):

    user_id = init_json.get("user_id")
    practice_id = init_json.get("practice_id")
    subject_id = init_json.get("subject_id")  # 学科-数学
    department_id = init_json.get("department_id")  # 小学
    grade_ids = init_json.get("grade_ids")  # 年级
    textbook = init_json.get("textbook")  # 教材
    chapter = init_json.get("chapter")  #章
    knowledge_ids = init_json.get("knowledge_ids")# 章节\章节——叶子知识点

    # 自己加载,根据用户id获取
    time_threshold = 15  # 初始化准备,加载学生信息。没有的话,设定一个值time_threshold = 60
    init = [user_id, practice_id, subject_id, department_id, grade_ids, textbook, chapter]
    return init, knowledge_ids, time_threshold



def send_test_again(receive_json):

# # 一、保存的数据
#     init_json = {"user_id": 1, "practice_id": 1, "subject_id": 2,
#                  "department_id": 1, "grade_ids": 4, "textbook": 13796,
#                  "chapter": 13803, "knowledge_ids": [13811, 13812, 13813, 13814]}
#
#
#     init_data, knowledge_ids, time_threshold = init(init_json)
#
#     test_df = get_test_df()
#     knowledge_ids = [str(i) for i in knowledge_ids]
#     # # 初始化练习题的数据范围
#     df_0, df_90, df_recall_group_0, df_recall_group_90 = init_test_set(test_df, knowledge_ids)
#     df_recall_group = df_recall_group_0.append(df_recall_group_90)
#
#     df_0_dict = {}
#     for i, j in enumerate(df_0):
#         df_0_dict[str(i)] = j.to_dict()
#     df_90_dict = {}
#     for i, j in enumerate(df_90):
#         df_90_dict[str(i)] = j.to_dict()
#
#     practice_id = init_json["practice_id"]
#     knowledge_ids = init_json["knowledge_ids"]
#     knowledge_ids_num = len(knowledge_ids)
#     time_threshold = 30
#     location_ids = [0, 1, 2, 3, 4, 5, 6, 7]
#     location_ids_num = len(location_ids)# 实际发送题目解析返回数据
#
#     dict_test = {"practice_id": practice_id, "knowledge_ids_num": knowledge_ids_num,
#                  "location_ids_num":location_ids_num, "time_threshold": time_threshold,
#                  "df_0": df_0_dict,"df_90": df_90_dict, "df_recall_group": df_recall_group.to_dict()}
#
#
#     dict_test["knowledge_ids"] = ",".join([str(i) for i in init_json["knowledge_ids"]])
#     red.hmset(str(practice_id), dict_test)




# 一、保存的数据


    #获得用户的练习id
    practice_id = receive_json.get("practice_id")
    user_id = receive_json.get("user_id")
    # practice_id = 1 #测试数据
    red_dict = red.hgetall(str(practice_id))
    # 解析redis数据
    df_0 = []
    for values in eval(red_dict["df_0"]).values():# 神奇的eval函数
        df = pd.DataFrame(values)
        df_0.append(df)

    df_90 = []
    for values in eval(red_dict["df_90"]).values():# 神奇的eval函数
        df = pd.DataFrame(values)
        df_90.append(df)
    df_recall_group = pd.DataFrame(eval(red_dict["df_recall_group"]))  # 神奇的eval函数

    time_threshold = eval(red_dict["time_threshold"])
    knowledge_ids_num = eval(red_dict["knowledge_ids_num"])
    location_ids_num = eval(red_dict["location_ids_num"])





    df_receive_results = pd.DataFrame(receive_json.get("result"))
    df_receive_results = df_receive_results.sort_values(["location"])
    df_receive_results["knowledge_ids"] = df_receive_results["knowledge_ids"].apply(lambda x: x[0])

    # 实际的返回知识点
    knowledge_ids_list = df_receive_results["knowledge_ids"].to_list()
    knowledge_ids = list(set(knowledge_ids_list))

    xyz_list = sorting_result(df_receive_results, time_threshold)
    x_false_knowledge_ids_list = xyz_list[0]
    y_true_knowledge_ids_list = xyz_list[1]
    z_true_knowledge_ids_list = xyz_list[2]
    x = len(x_false_knowledge_ids_list)
    y = len(y_true_knowledge_ids_list)
    z = len(z_true_knowledge_ids_list)


    if x > 0:

        if (25 - 2 * knowledge_ids_num) / x < 2:

            # print(x, y, z)
            # print("出题策略为 1x_1y_1z_组合")

            new_json = xyz_test(x_false_knowledge_ids_list, y_true_knowledge_ids_list, z_true_knowledge_ids_list, knowledge_ids, df_0, df_90,df_recall_group, location_ids_num, n=1)
            new_json.index += (location_ids_num + 1)  # 重置索引位置
            next_json = new_json.to_json(orient='index', force_ascii=False)
            json = {"status": 0, "message": "success", "result": {"user_id": user_id, "practice_id": practice_id, "data": eval(next_json)}}

            return json

        elif (25 - 2 * knowledge_ids_num) / x > 2:
            # print(x, y, z)
            # print("出题策略为 2x_1y_1z_组合")
            new_json = xyz_test(x_false_knowledge_ids_list, y_true_knowledge_ids_list, z_true_knowledge_ids_list, knowledge_ids, df_0, df_90, df_recall_group, location_ids_num, n=2)
            new_json.index += (location_ids_num+1) #重置索引位置
            next_json = new_json.to_json(orient='index', force_ascii=False)
            json = {"status": 0, "message": "success",
                    "result": {"user_id": user_id, "practice_id": practice_id, "data": eval(next_json)}}

            return json
    else:
        # print(x, y, z)
        # print("出题策略为 1y_1z_组合")
        new_json = xyz_test(x_false_knowledge_ids_list, y_true_knowledge_ids_list, z_true_knowledge_ids_list, knowledge_ids, df_0, df_90,df_recall_group, location_ids_num)
        new_json.index += (location_ids_num + 1)  # 重置索引位置
        next_json = new_json.to_json(orient='index', force_ascii=False)
        json = {"status": 0, "message": "success",
                "result": {"user_id": user_id, "practice_id": practice_id, "data": eval(next_json)}}

        return json

    # 发送排序题目


# 难点
"""
        难度策略:
        1）2x_1y_1z_组合
        2）1x_1y_1z_组合
        3）1y_1z_组合
        y:简单
        z:难
        x:简单和难分情况
            1）2x_1y_1z_组合，其中 x: 2错——2简; 1对1错——1简1难
            2）1x_1y_1z_组合，其中 x: 1错——1简。
"""


# if __name__ == '__main__':
#
#
#     init_json = {"user_id": 1, "practice_id": 1, "subject_id": 2,
#                  "department_id": 1, "grade_ids": 2, "textbook": 13796,
#                  "chapter": 13803, "knowledge_ids": [13811, 13812, 13813, 13814]}
#
#     process_initialization(init_json)
#     receive_json = {"user_id": 1000001, "practice_id": 1, "result":
#         [{"location": 1, "test_id": 2057204, "is_true": 0, "difficulty": 0, "time_consuming": 40,
#           "knowledge_ids": [13811]},
#          {"location": 2, "test_id": 2057202, "is_true": 0, "difficulty": 0, "time_consuming": 2,
#           "knowledge_ids": [13811]},
#          {"location": 3, "test_id": 2057214, "is_true": 1, "difficulty": 0, "time_consuming": 3,
#           "knowledge_ids": [13812]},
#          {"location": 4, "test_id": 2057213, "is_true": 1, "difficulty": 0, "time_consuming": 9,
#           "knowledge_ids": [13812]},
#          {"location": 5, "test_id": 2057225, "is_true": 1, "difficulty": 0, "time_consuming": 4,
#           "knowledge_ids": [13813]},
#          {"location": 6, "test_id": 2057222, "is_true": 0, "difficulty": 0, "time_consuming": 2,
#           "knowledge_ids": [13813]},
#          {"location": 7, "test_id": 2057234, "is_true": 1, "difficulty": 0, "time_consuming": 3,
#           "knowledge_ids": [13814]},
#          {"location": 8, "test_id": 2057236, "is_true": 0, "difficulty": 0, "time_consuming": 19,
#           "knowledge_ids": [13814]}]}
#     send_test_again(receive_json)

