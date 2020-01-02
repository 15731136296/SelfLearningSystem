import pandas as pd
import redis

# host = "39.98.180.205"
# pool = redis.ConnectionPool(host=host, port=6379, db=1, decode_responses=True)
pool = redis.ConnectionPool(host='localhost', port=6379, db=1, decode_responses=True)
red = redis.Redis(connection_pool=pool)


def get_test_df():
    # path3 = "../test_library_info/test_info_clear.csv"
    path3 = "../test_library_info/test_info_clear_test.csv"
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
    df_group_0 = test_df[
        (test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] > 1) & (
                test_df["difficulty"] == 0)]
    df_group_90 = test_df[
        (test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] > 1) & (
                test_df["difficulty"] == 90)]

    return df_0, df_90, df_group_0, df_group_90


def init_test(df_0, df_90, knowledge_ids_num):

    """
    与策略二不一样，修改。

    """

    # 1、初始化数据
    if knowledge_ids_num == 1:

        if df_0[0].shape[0] < 4:
            num = df_0.shape[0]
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
        # init_df = init_df_new
        init_df = init_df_new.reset_index(drop=True)  # 重置索引

    # 修改列名
    # init_df =init_df.rename({"ids_split": "knowledge_ids"})
    # 暂定数据格式
    init_df = init_df.reset_index()
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

    test_df = get_test_df()

    knowledge_ids = [str(i) for i in knowledge_ids]
    knowledge_ids_num = len(knowledge_ids)
    # 初始化练习题的数据范围
    df_0, df_90, df_group_0, df_group_90 = init_test_set(test_df, knowledge_ids)
    df_recall_group = df_group_0.append(df_group_90)

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
        is_true_list = eval(red_dict["is_true"])
        red_dict = red.hgetall(str(practice_id))
        is_true_list = eval(red_dict["is_true_list"])


        # 更新is_true_list,判断难度，判断题型
        is_true_list.append(is_true)
        red.hmset(str(practice_id), {"is_true_list": is_true_list})
        difficulty = judge_next_difficulty(is_true_list)

        false_knowledge_ids_list = eval(red_dict["false_knowledge_ids_list"])
        knowledge_ids_list = eval(red_dict["knowledge_ids_list"])


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



    if len(knowledge_ids_list) == 1:
        df_group_0 = df_0
        df_group_90 = df_90
        df_recall_group = df_group_0.append(df_group_90)


    # 出题
    # 错误点或者组合体
    # 返回一题
    if false_knowledge_ids_list:
        # 出错题
        false_knowledge_ids = false_knowledge_ids_list[0]
        i = knowledge_ids_list.index(false_knowledge_ids) #所在知识点的列表index
        if difficulty == 0:

            if df_0[i].shape[0] >= 1:
                df_test = df_0[i].sample(1)
            else:
                df_test = df_90[i].sample(1)
                # df_test = df_recall_group[0]#防止没有题目
        elif difficulty == 90:

            if df_90[i].shape[0] >= 1:
                df_test = df_90[i].sample(1)
            else:
                df_test = df_0[i].sample(1)
                # df_test = df_recall_group[0]#防止没有题目

        # 更改 false_knowledge_ids_list
        false_knowledge_ids_list.remove(false_knowledge_ids)
        red.hmset(str(practice_id), {"false_knowledge_ids_list": false_knowledge_ids_list})


    else:
       # 组合题
        if difficulty == 0:
            if df_group_0.shape[0] >= 1:
                df_test = df_group_0.sample(1)

            elif df_group_0.empty and df_recall_group.shape[0] >= 1:
                df_test = df_recall_group.sample(1)

            else:
                df_test = pd.DataFrame()

                # df_test = df_recall_group[0]#防止没有题目
        elif difficulty == 90:

            if df_group_90.shape[0] >= 1:
                df_test = df_group_90.sample(1)

            elif df_group_90.empty and df_recall_group.shape[0] >= 1:
                df_test = df_recall_group.sample(1)
            else:
                df_test = pd.DataFrame()
                # df_test = df_recall_group[0]

    df_test = df_test.reset_index()

    df_test.index += (last_location+1)

    init_json = df_test[["test_id", "ids_split"]].to_json(orient='index', force_ascii=False)
    json = {"status": 0, "message": "success",
            "result": {"user_id": user_id, "practice_id": practice_id, "data": eval(init_json)}}

    return json




# # "ids_split"修改成"knowledge_ids"
# if __name__ == '__main__':
#     # [13811, 13812, 13813, 13814]
#
#     init_json = {"user_id": 100, "practice_id": 100, "subject_id": 2,
#                      "department_id": 1, "grade_ids": 4, "textbook": 13796,
#                      "chapter": 13803, "knowledge_ids": [13811]}
#
#     process_initialization(init_json)
#
#     receive_json = {"user_id": 100, "practice_id": 100, "result":
#             [{"location": 1, "test_id": 2057204, "is_true": 0, "difficulty": 0, "time_consuming": 40,
#               "knowledge_ids": [13811]},
#              {"location": 2, "test_id": 2057202, "is_true": 0, "difficulty": 0, "time_consuming": 2,
#               "knowledge_ids": [13811]},
#              {"location": 3, "test_id": 2057214, "is_true": 1, "difficulty": 0, "time_consuming": 3,
#               "knowledge_ids": [13811]},
#              {"location": 4, "test_id": 2057213, "is_true": 1, "difficulty": 0, "time_consuming": 9,
#               "knowledge_ids": [13811]}]}
#
#     # 每次交互行为
#     # receive_json = {"user_id": 100, "practice_id": 100, "result": [{"location": 5, "test_id": 2057204, "is_true": 0, "difficulty": 0, "time_consuming": 40,
#     #                         "knowledge_ids": [13811]}]}
#     s = every_interaction(receive_json)
#     print(s)





    #
    #
    # init, knowledge_ids = init()
    # test_df = get_test_df()
    #
    # knowledge_ids = [str(i) for i in knowledge_ids]
    # knowledge_ids_num = len(knowledge_ids)
"""
# 知识点为1个
    if knowledge_ids_num == 1:

        #1、初始化数据
        df_recall_1_0 = test_df[(test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_1_90 = test_df[(test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]
        #2、准备4道简单题
        # init = df_recall_1_0["test_id"].sample(4, replace=True)  # 要是没有的话，重复出题。
        # test_init = init.to_list()  # 初始化4道题，type:list
        init = df_recall_1_0.sample(4, replace=True)  # 要是没有的话，重复出题。
        df_test = init[["test_id", "ids_split"]].reset_index()
        send_json = df_test.to_json() #待修改

        #3、发送四道简单题send_json
        # send_json()

        #4、接收四道题的返回数据和答题结果
        is_true_list = receive_json()
        
        

        #5、判断下一道题的难度
        difficulty = judge_next_difficulty(is_true_list)
        if difficulty == 0:
            next_test = df_recall_1_0.sample(1, replace=True)  # 要是没有的话，重复出题。
        elif difficulty == 90:
            next_test = df_recall_1_90.sample(1, replace=True)  # 要是没有的话，重复出题。
        df_next_test = next_test[["test_id", "ids_split"]].reset_index()
        send_json = df_next_test.to_json()  # 待修改


        #6、发送第5道简单题send_json
        # send_json(send_json)
        #7、接收第5道题的返回数据和答题结果
        new_is_true_list = [1]
        is_true_list.extend(new_is_true_list)
        #8、判断下一道题的难度
        difficulty = judge_next_difficulty(is_true_list)


        if difficulty == 0:

            if df_recall_1_0.empty:
                next_test = df_recall_1_90.sample(1, replace=True)  # 要是没有的话，重复出题。
            else:
                next_test = df_recall_1_0.sample(1, replace=True)  # 要是没有的话，重复出题。
        elif difficulty == 90:

            if df_recall_1_90.empty:
                next_test = df_recall_1_0.sample(1, replace=True)  # 要是没有的话，重复出题。
            else:
                next_test = df_recall_1_90.sample(1, replace=True)  # 要是没有的话，重复出题。

        df_next_test = next_test[["test_id", "ids_split"]].reset_index()
        send_json = df_next_test.to_json()  # 待修改

        for _ in range(4):
            new_is_true_list = [1]
            is_true_list.extend(new_is_true_list)
            # 8、判断下一道题的难度
            difficulty = judge_next_difficulty(is_true_list)
            if difficulty == 0:

                if df_recall_1_0.empty:
                    next_test = df_recall_1_90.sample(1, replace=True)  # 要是没有的话，重复出题。
                else:
                    next_test = df_recall_1_0.sample(1, replace=True)  # 要是没有的话，重复出题。
            elif difficulty == 90:

                if df_recall_1_90.empty:
                    next_test = df_recall_1_0.sample(1, replace=True)  # 要是没有的话，重复出题。
                else:
                    next_test = df_recall_1_90.sample(1, replace=True)  # 要是没有的话，重复出题。

            df_next_test = next_test[["test_id", "ids_split"]].reset_index()
            send_json = df_next_test.to_json()  # 待修改

        #第10题
        if df_recall_1_90.empty:
            next_test = df_recall_1_0.sample(1, replace=True)  # 要是没有的话，重复出题。
        else:
            next_test = df_recall_1_90.sample(1, replace=True)  # 要是没有的话，重复出题。

        df_next_test = next_test[["test_id", "ids_split"]].reset_index()
        send_json = df_next_test.to_json()  # 待修改




"""





"""

# 知识点为2个

    elif knowledge_ids_num == 2:

        # 备选集
        df_recall_1_0 = test_df[(test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_1_90 = test_df[(test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]

        df_recall_2_0 = test_df[(test_df["knowledge_ids"].str.contains(knowledge_ids[1])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_2_90 = test_df[(test_df["knowledge_ids"].str.contains(knowledge_ids[1])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]

        df_group_0 = test_df[
            (test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] == 1) & (
                        test_df["difficulty"] == 0)]
        df_group_90 = test_df[
            (test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] == 1) & (
                        test_df["difficulty"] == 90)]


        # 2、准备4道简单题

        init = df_recall_1_0.sample(2, replace=True)  # 要是没有的话，重复出题。
        init_2 = df_recall_2_0.sample(2, replace=True)  # 要是没有的话，重复出题。
        init = init.append(init_2)
        # test_init = init.to_list()  # 初始化4道题，type:list
        df_test = init[["test_id", "ids_split"]].reset_index()
        send_json = df_test.to_json()  # 待修改
        # 3、发送四道简单题send_json
        # send_json()
        # 4、接收四道题的返回数据和答题结果
        is_true_list = receive_json()

        false_knowledge_ids_list = [138112, 138113]#错误的知识点


        # 5、判断下一道题的难度
        difficulty = judge_next_difficulty(is_true_list)


        if len(false_knowledge_ids_list) == 0:

            if difficulty == 0:
                next_test = df_group_0.sample(1, replace=True)  # 要是没有的话，重复出题。
            elif difficulty == 90:
                next_test = df_group_90.sample(1, replace=True)  # 要是没有的话，重复出题。
            df_next_test = next_test[["test_id", "ids_split"]].reset_index()
            send_json = df_next_test.to_json()  # 待修改



        elif len(false_knowledge_ids_list) == 1:

            if difficulty == 0:
                next_test = test_df[(test_df["knowledge_ids"].str.contains(false_knowledge_ids_list[0])) &
                                    (test_df["knowledge_num"] == 1) & (test_df["difficulty"] == 0)]

                if next_test.empty:
                    next_test = df_group_0.sample(1, replace=True)  # 要是没有的话，重复出题。
                else:
                    next_test = next_test.sample(1, replace=True)  # 要是没有的话，重复出题。

            elif difficulty == 90:
                next_test = test_df[(test_df["knowledge_ids"].str.contains(false_knowledge_ids_list[0])) &
                                    (test_df["knowledge_num"] == 1) & (test_df["difficulty"] == 90)]

                if next_test.empty:
                    next_test = df_group_90.sample(1, replace=True)  # 要是没有的话，重复出题。
                else:
                    next_test = next_test.sample(1, replace=True)  # 要是没有的话，重复出题。


            df_next_test = next_test[["test_id", "ids_split"]].reset_index()
            send_json = df_next_test.to_json()  # 待修改


        elif len(false_knowledge_ids_list) == 2:

            pass
        else:
            pass

        # 第六题
        false_knowledge_id = false_knowledge_ids_list[1]

        # 发送组合题

        # if difficulty == 0:
        #     next_test = df_recall_1_0.sample(1, replace=True)  # 要是没有的话，重复出题。
        # elif difficulty == 90:
        #     next_test = df_recall_1_90.sample(1, replace=True)  # 要是没有的话，重复出题。
        # df_next_test = next_test[["test_id", "ids_split"]].reset_index()
        # send_json = df_next_test.to_json()  # 待修改

        pass


#知识点为3个
    elif knowledge_ids_num == 3:
        pass

    else:
        pass



"""





