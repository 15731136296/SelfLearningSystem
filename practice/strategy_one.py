import pandas as pd
import redis

# host = "39.98.180.205"
# pool = redis.ConnectionPool(host=host, port=6379, db=1, decode_responses=True)
pool = redis.ConnectionPool(host='localhost', port=6379, db=1, decode_responses=True)
red = redis.Redis(connection_pool=pool)


def get_test_df():
    path3 = "../test_library_info/test_info_clear.csv"
    # path3 = "../test_library_info/test_info_clear_test.csv"
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
    content = "|".join(knowledge_ids)
    df_group_0 = test_df[
        (test_df["knowledge_ids"].str.contains(content)) & (test_df["knowledge_num"] > 1) & (
                test_df["difficulty"] == 0)]
    df_group_90 = test_df[
        (test_df["knowledge_ids"].str.contains(content)) & (test_df["knowledge_num"] > 1) & (
                test_df["difficulty"] == 90)]

    return df_0, df_90, df_group_0, df_group_90


def init_test(df_0, df_90, df_recall_group, knowledge_ids_num):

    """
    与策略二不一样，修改。
    """

    # 1、初始化数据
    if knowledge_ids_num == 1:

        if df_0[0].shape[0] < 4:
            num = df_0[0].shape[0]
            if df_90[0].shape[0] <= (4-num):
                init_df = df_0[0].append(df_90)
            else:
                init_test_2 = df_90[0].sample((4-num), replace=False)  # 要是没有的话，重复出题。
                init_df = df_0[0].append(init_test_2)
        else:
            init_df = df_0[0].sample(4, replace=False)  # 要是没有的话，重复出题。


    elif knowledge_ids_num == 2:
        # 备选集 初始化题目
        init_df_new = pd.DataFrame()
        for i in range(knowledge_ids_num):
            #2是限制参数
            if df_0[i].shape[0] < 2:
                num = df_0[i].shape[0]
                if df_90[i].shape[0] <= (2 - num):
                    init_df = df_0[i].append(df_90[i])
                else:
                    init_test_2 = df_90[i].sample((2 - num), replace=False)  # 要是没有的话，重复出题。
                    init_df = df_0[i].append(init_test_2)
            else:
                init_df = df_0[i].sample(2, replace=False)  # 要是没有的话，重复出题。
            init_df_new = init_df_new.append(init_df)
        init_df = init_df_new


    elif knowledge_ids_num == 3:

        """修改逻辑"""

        init_df_new = pd.DataFrame()
        for i in range(knowledge_ids_num):
            #2是限制参数
            if df_0[i].shape[0] < 2:
                num = df_0[i].shape[0]
                if df_90[i].shape[0] <= (2 - num):
                    init_df = df_0[i].append(df_90[i])
                else:
                    init_test_2 = df_90[i].sample((2 - num), replace=False)  # 要是没有的话，重复出题。
                    init_df = df_0[i].append(init_test_2)
            else:
                init_df = df_0[i].sample(2, replace=False)  # 要是没有的话，重复出题。
            init_df_new = init_df_new.append(init_df)
        init_df = init_df_new.reset_index(drop=True)  # 重置索引


    init_df = init_df.reset_index()
    init_df.index += 1  #索引从1开始
    df = init_df[["test_id", "test_type", "ids_split"]]
    df = df.rename(columns={"test_id": "test_id", "test_type": "test_type", "ids_split": "knowledge_ids"})
    init_json = df.to_json(orient='index', force_ascii=False)
    test_id_list = df["test_id"].to_list()
    # location_ids_num = init_df.shape[0]
    return init_json, test_id_list


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

    test_df = get_test_df()

    knowledge_ids = [str(i) for i in knowledge_ids]
    knowledge_ids_num = len(knowledge_ids)
    # 初始化练习题的数据范围
    df_0, df_90, df_group_0, df_group_90 = init_test_set(test_df, knowledge_ids)
    df_recall_group = df_group_0.append(df_group_90)

    # 第一层
    # 题量: 25
    # n道只含一个知识点的题目
    init_json, test_id_list = init_test(df_0, df_90, df_recall_group, knowledge_ids_num)
    location_ids_num = len(test_id_list)
    # location_ids_num 为实际发送题目解析返回数据

    df_0_dict = {}
    for i, j in enumerate(df_0):
        df_0_dict[str(i)] = j.to_dict()
    df_90_dict = {}
    for i, j in enumerate(df_90):
        df_90_dict[str(i)] = j.to_dict()

    knowledge_ids_num = len(knowledge_ids)


    dict_test = {"practice_id": practice_id, "knowledge_ids_num": knowledge_ids_num,"test_id_list":test_id_list,
                 "location_ids_num":location_ids_num, "time_threshold": time_threshold,
                 "df_0": df_0_dict, "df_90": df_90_dict, "df_group_0": df_group_0.to_dict(), "df_group_90": df_group_90.to_dict(),
                 "df_recall_group": df_recall_group.to_dict()}
    # dict_test["knowledge_ids"] = ",".join([str(i) for i in init_json["knowledge_ids"]])#降低redis版本后可以存列表的数据了
    red.hmset(str(practice_id), dict_test)#保存到redis

    json = {"status": 0, "message": "success", "result": {"user_id": user_id, "practice_id": practice_id, "data": eval(init_json)}}

    return json


def judge_next_difficulty(is_true_list):

    """
    判断出题难度
    :param is_true_list:
    :return:
    """

    if sum(is_true_list[-2:]) == 0:

        difficulty = 0
        return difficulty
    elif sum(is_true_list[-4:]) == 4:

        difficulty = 90
        return difficulty
    else:
        difficulty = 0

        return difficulty


def every_interaction(receive_json):

    """
    多次交互
    :param receive_json: 前端返回数据
    :return: type : json
    """

    practice_id = receive_json.get("practice_id")
    user_id = receive_json.get("user_id")
    result = receive_json.get("result")

    location_ids_num = len(result)
    last_location = max([i.get("location")for i in result])



    # 第一次接收数据，并且记录返回的4道题的结果
    if location_ids_num > 1:
        is_true_list = [i.get("is_true") for i in result]

        knowledge_ids = [i.get("knowledge_ids") for i in result]
        knowledge_ids_list = [i[0] for i in knowledge_ids]
        knowledge_ids_num = len(list(set(knowledge_ids_list)))

        false_knowledge_ids_list = [knowledge_ids[i][0] for i, j in enumerate(is_true_list) if j == 0]  # 错误的知识点
        false_knowledge_ids_list = list(set(false_knowledge_ids_list))



        # redis记录答题结果即可、是否正确。
        dict_test = {"user_id": user_id, "practice_id": practice_id, "knowledge_ids_num": knowledge_ids_num,
                     "knowledge_ids_list": knowledge_ids_list,
                     "location_ids_num": location_ids_num, "is_true_list": is_true_list,
                     "false_knowledge_ids_list": false_knowledge_ids_list}
        red.hmset(str(practice_id), dict_test)

        difficulty = judge_next_difficulty(is_true_list)



    #4道题后，一道一道题的返回答题结果
    elif location_ids_num == 1:

        result = receive_json.get("result")[0]#每次返回一次答题结果
        is_true = result.get("is_true")
        location = result.get("location")

        # 获取redis数据
        red_dict = red.hgetall(str(practice_id))
        is_true_list = eval(red_dict["is_true_list"])


        # 更新is_true_list,判断难度，判断题型
        is_true_list.append(is_true)
        red.hmset(str(practice_id), {"is_true_list": is_true_list})
        difficulty = judge_next_difficulty(is_true_list)

        false_knowledge_ids_list = eval(red_dict["false_knowledge_ids_list"])
        knowledge_ids_list = eval(red_dict["knowledge_ids_list"])
        knowledge_ids_num = len(list(set(knowledge_ids_list)))
        red_dict = red.hgetall(str(practice_id))
        test_id_list = eval(red_dict["test_id_list"])


    # 解析redis数据中的字典
    red_dict = red.hgetall(str(practice_id))
    df_0 = []
    for values in eval(red_dict["df_0"]).values():  # 神奇的eval函数
        df = pd.DataFrame(values)
        df_0.append(df)


    df_90 = []
    for values in eval(red_dict["df_90"]).values():  # 神奇的eval函数
        df = pd.DataFrame(values)
        df_90.append(df)


    df_group_0 = pd.DataFrame(eval(red_dict["df_group_0"]))  # 神奇的eval函数
    df_group_90 = pd.DataFrame(eval(red_dict["df_group_90"]))  # 神奇的eval函数
    df_recall_group = pd.DataFrame(eval(red_dict["df_recall_group"]))  #

    #过滤已经出过的题目
    test_id_list = eval(red_dict["test_id_list"])
    df_group_0_filter = df_group_0[- df_group_0["test_id"].isin(test_id_list)]
    df_group_90_filter = df_group_90[- df_group_90["test_id"].isin(test_id_list)]
    df_recall_group_filter = df_recall_group[- df_recall_group["test_id"].isin(test_id_list)]


    if knowledge_ids_num == 1:

        df_group_0_filter = df_0[0][- df_0[0]["test_id"].isin(test_id_list)]
        df_group_90_filter = df_90[0][- df_90[0]["test_id"].isin(test_id_list)]
        df_recall_group_filter = df_group_0_filter.append(df_group_90_filter)


    # 出题
    # 错误点或者组合体
    # 返回一题
    if false_knowledge_ids_list:
        # 出错题
        false_knowledge_ids = false_knowledge_ids_list[0]
        i = knowledge_ids_list.index(false_knowledge_ids) #所在知识点的列表index
        df_0_filter = df_0[i][- df_0[i]["test_id"].isin(test_id_list)]
        df_90_filter = df_90[i][- df_90[i]["test_id"].isin(test_id_list)]

        if difficulty == 0:

            if df_0_filter.shape[0] >= 1:
                df_test = df_0_filter.sample(1)
            else:
                if df_90_filter.shape[0] > 0:
                    df_test = df_90_filter.sample(1)
                else:
                    df_test = pd.DataFrame(columns=["test_id", "test_type", "ids_split"])
                    # df_test = df_recall_group[0]#防止没有题目
        elif difficulty == 90:

            if df_90_filter .shape[0] >= 1:
                df_test = df_90_filter.sample(1)
            else:
                if df_0_filter.shape[0] > 0:
                    df_test = df_90_filter.sample(1)
                else:
                    df_test = pd.DataFrame(columns=["test_id", "test_type", "ids_split"])
                    # df_test = df_recall_group[0]#防止没有题目
                # df_test = df_recall_group[0]#防止没有题目

        # 更新 false_knowledge_ids_list
        false_knowledge_ids_list.remove(false_knowledge_ids)
        red.hmset(str(practice_id), {"false_knowledge_ids_list": false_knowledge_ids_list})


    else:
       # 组合题
        if difficulty == 0:
            if df_group_0_filter.shape[0] >= 1:
                df_test = df_group_0_filter.sample(1)

            elif df_group_0_filter.empty and df_recall_group_filter.shape[0] >= 1:
                df_test = df_recall_group_filter.sample(1)

            else:
                df_test = pd.DataFrame(columns=["test_id", "test_type", "ids_split"])

                # df_test = df_recall_group[0]#防止没有题目
        elif difficulty == 90:

            if df_group_90_filter.shape[0] >= 1:
                df_test = df_group_90_filter.sample(1)

            elif df_group_90_filter.empty and df_recall_group_filter.shape[0] >= 1:
                df_test = df_recall_group_filter.sample(1)
            else:
                df_test = pd.DataFrame(columns=["test_id", "test_type", "ids_split"])
                # df_test = df_recall_group[0]

    df_test = df_test.reset_index()
    df_test.index += (last_location+1)

    df_test_1 = df_test[["test_id", "test_type", "ids_split"]]
    df_test_1 = df_test_1.rename(columns={"test_id": "test_id", "test_type": "test_type", "ids_split": "knowledge_ids"})
    init_json = df_test_1.to_json(orient='index', force_ascii=False)
    json = {"status": 0, "message": "success",
            "result": {"user_id": user_id, "practice_id": practice_id, "data": eval(init_json)}}

    #保存题目ID列表到redis
    next_test_id = df_test_1["test_id"].to_list()
    test_id_list = eval(red_dict["test_id_list"])
    test_id_list.extend(next_test_id)
    red.hmset(str(practice_id), {"test_id_list": test_id_list})

    return json



# if __name__ == '__main__':

    # [c, 13917, 13918, 13919]

    # init_json = {"user_id": 100, "practice_id": 100, "subject_id": 2,
    #                  "department_id": 1, "grade_ids": 4, "textbook": 13796,
    #                  "chapter": 13910, "knowledge_ids": [13919]}
    #
    # s = process_initialization(init_json)
    # print(s)

    # receive_json = {"user_id": 100, "practice_id": 100, "result":
    #         [{"location": 1, "test_id": 2248832, "is_true": 0, "difficulty": 0, "time_consuming": 40,
    #           "knowledge_ids": [13916]},
    #          {"location": 2, "test_id": 2253021, "is_true": 0, "difficulty": 0, "time_consuming": 200,
    #           "knowledge_ids": [13916]},
    #          {"location": 3, "test_id": 2242066, "is_true": 0, "difficulty": 0, "time_consuming": 3,
    #           "knowledge_ids": [13916]},
    #          {"location": 4, "test_id": 2242050, "is_true": 0, "difficulty": 0, "time_consuming": 9,
    #           "knowledge_ids": [13916]}]}
    # #
    # # # 每次交互行为
    # # receive_json = {"user_id": 100, "practice_id": 100, "result": [{"location": 9, "test_id": 2057207, "is_true": 0, "difficulty": 0, "time_consuming": 40,
    # #                         "knowledge_ids": [13811]}]}
    # s = every_interaction(receive_json)
    # print(s)
    #
