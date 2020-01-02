"""
策略一草稿
"""
import pandas as pd
import redis

pool = redis.ConnectionPool(host='localhost', port=6379, db=1, decode_responses=True)
red = redis.Redis(connection_pool=pool)


def init():
    subject_id = 2  # 学科-数学
    department_id = 1  # 小学
    grade_ids = 4  # 年级
    textbook = 13796  # 教材
    chapter = 13803  # 章
    knowledge_ids = [13811, 13812, 13813]
    knowledge_ids = [13811, 13812]
    # knowledge_ids = [13811]# 章节\章节——叶子知识点
    init = [subject_id, department_id, grade_ids, textbook, chapter, knowledge_ids]
    return init, knowledge_ids


def get_test_df():
    # path3 = "../test_library_info/test_info_clear.csv"
    path3 = "../test_library_info/test_info_clear_test.csv"
    test_df = pd.read_csv(path3)
    return test_df


def get_recall_dateset(test_df, knowledge_ids):
    """
    根据知识点获得题目的备选集

    """

    knowledge_ids = [str(i) for i in knowledge_ids]
    knowledge_ids_num = len(knowledge_ids)

    if knowledge_ids_num == 1:

        df_recall_1_0 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_1_90 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]

        return df_recall_1_0, df_recall_1_90

    elif knowledge_ids_num == 2:
        # 备选集
        df_recall_1_0 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_1_90 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]

        df_recall_2_0 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[1])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_2_90 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[1])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]

        df_recall_group_0 = test_df[
            (test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_group_90 = test_df[
            (test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]

        return df_recall_1_0, df_recall_1_90, df_recall_2_0, df_recall_2_90, df_recall_group_0, df_recall_group_90

    elif knowledge_ids_num == 3:

        pass


def send_json_init(init_json):
    # 发送数据格式
    # 一、
    send_results = [{"location": 1, "test_id": 200001, "knowledge_ids": 2020},
                    {"location": 2, "test_id": 200002, "knowledge_ids": 2021},
                    {"location": 3, "test_id": 200003, "knowledge_ids": 2023},
                    {"location": 4, "test_id": 200001, "knowledge_ids": 2023}]

    send_json = {"status": "0", "message": "success", "data": send_results}
    # 二
    # test_post_results = {"1": {"test_id": 200001, "difficulty": 0, "test_type": "题目类型", "test_content": "题目内容",
    #                            "test_options": "试题选项", "test_answer": "正确答案", "test_analytic": "试题解析", "url": "试题图片url"}}

    df_send_results = pd.DataFrame(send_json.get("data"))
    df_send_results = df_send_results.sort_values(["location"])


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
    """
    与策略二不一样，修改。

    """

    # 1、初始化数据
    if knowledge_ids_num == 1:
        df_recall_1_0 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_1_90 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]
        # 2、准备4道简单题
        # init = df_recall_1_0["test_id"].sample(4, replace=True)  # 要是没有的话，重复出题。
        # test_init = init.to_list()  # 初始化4道题，type:list

        # df_0[i].sample(4, replace=True)
        init = df_recall_1_0.sample(4, replace=True)  # 要是没有的话，重复出题。
        df_test = init[["test_id", "ids_split"]].reset_index()
        send_json = df_test.to_json()  # 待修改

        if df_0.empty and df_90.shape[0] > 1:
            init_test = df_90.sample(2, replace=False)  # 要是没有的话，重复出题。
        elif df_0.shape[0] > 1:
            init_test = df_0.sample(2, replace=False)  # 要是没有的话，重复出题。

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
    init_df.index += 1  # 索引从1开始
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
                 "location_ids_num": location_ids_num, "time_threshold": time_threshold,
                 "df_0": df_0_dict, "df_90": df_90_dict, "df_recall_group": df_recall_group.to_dict()}
    # dict_test["knowledge_ids"] = ",".join([str(i) for i in init_json["knowledge_ids"]])#降低redis版本后可以存列表的数据了
    red.hmset(str(practice_id), dict_test)  # 保存到redis
    # 返回数据
    json = {"status": 0, "message": "success",
            "result": {"user_id": user_id, "practice_id": practice_id, "data": eval(init_json)}}
    return json


def receive_json():
    # 返回数据格式

    receive_results = [
        {"location": 1, "test_id": 200002, "is_true": 0, "difficulty": 0, "time_consuming": 4, "user_answer": "",
         "knowledge_ids": 2020},
        {"location": 2, "test_id": 200001, "is_true": 1, "difficulty": 0, "time_consuming": 2, "user_answer": "",
         "knowledge_ids": 2021},
        {"location": 3, "test_id": 200009, "is_true": 1, "difficulty": 0, "time_consuming": 3, "user_answer": "",
         "knowledge_ids": 2022},
        {"location": 4, "test_id": 200010, "is_true": 1, "difficulty": 0, "time_consuming": 9, "user_answer": "",
         "knowledge_ids": 2023}]

    receive_json = {"status": "0", "message": "success", "data": receive_results}

    df_receive_results = pd.DataFrame(receive_json.get("data"))
    df_receive_results = df_receive_results.sort_values(["location"])
    is_true_list = df_receive_results["is_true"].to_list()

    return is_true_list


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


def send_json():
    pass


def receive_json():
    pass


if __name__ == '__main__':

    init, knowledge_ids = init()
    test_df = get_test_df()

    knowledge_ids = [str(i) for i in knowledge_ids]
    knowledge_ids_num = len(knowledge_ids)

    # 知识点为1个
    if knowledge_ids_num == 1:

        # 1、初始化数据
        df_recall_1_0 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_1_90 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]
        # 2、准备4道简单题
        # init = df_recall_1_0["test_id"].sample(4, replace=True)  # 要是没有的话，重复出题。
        # test_init = init.to_list()  # 初始化4道题，type:list
        init = df_recall_1_0.sample(4, replace=True)  # 要是没有的话，重复出题。
        df_test = init[["test_id", "ids_split"]].reset_index()
        send_json = df_test.to_json()  # 待修改

        # 3、发送四道简单题send_json
        # send_json()

        # 4、接收四道题的返回数据和答题结果
        is_true_list = receive_json()

        # 5、判断下一道题的难度
        difficulty = judge_next_difficulty(is_true_list)
        if difficulty == 0:
            next_test = df_recall_1_0.sample(1, replace=True)  # 要是没有的话，重复出题。
        elif difficulty == 90:
            next_test = df_recall_1_90.sample(1, replace=True)  # 要是没有的话，重复出题。
        df_next_test = next_test[["test_id", "ids_split"]].reset_index()
        send_json = df_next_test.to_json()  # 待修改

        # 6、发送第5道简单题send_json
        # send_json(send_json)
        # 7、接收第5道题的返回数据和答题结果
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

        # 第10题
        if df_recall_1_90.empty:
            next_test = df_recall_1_0.sample(1, replace=True)  # 要是没有的话，重复出题。
        else:
            next_test = df_recall_1_90.sample(1, replace=True)  # 要是没有的话，重复出题。

        df_next_test = next_test[["test_id", "ids_split"]].reset_index()
        send_json = df_next_test.to_json()  # 待修改


    # 知识点为2个

    elif knowledge_ids_num == 2:

        # 备选集
        df_recall_1_0 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_1_90 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[0])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]

        df_recall_2_0 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[1])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_2_90 = test_df[
            (test_df["knowledge_ids"].str.contains(knowledge_ids[1])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 90)]

        df_recall_group_0 = test_df[
            (test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]
        df_recall_group_90 = test_df[
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

        false_knowledge_ids_list = [138112, 138113]  # 错误的知识点

        # 5、判断下一道题的难度
        difficulty = judge_next_difficulty(is_true_list)

        if len(false_knowledge_ids_list) == 0:

            if difficulty == 0:
                next_test = df_recall_group_0.sample(1, replace=True)  # 要是没有的话，重复出题。
            elif difficulty == 90:
                next_test = df_recall_group_90.sample(1, replace=True)  # 要是没有的话，重复出题。
            df_next_test = next_test[["test_id", "ids_split"]].reset_index()
            send_json = df_next_test.to_json()  # 待修改



        elif len(false_knowledge_ids_list) == 1:

            if difficulty == 0:
                next_test = test_df[(test_df["knowledge_ids"].str.contains(false_knowledge_ids_list[0])) &
                                    (test_df["knowledge_num"] == 1) & (test_df["difficulty"] == 0)]

                if next_test.empty:
                    next_test = df_recall_group_0.sample(1, replace=True)  # 要是没有的话，重复出题。
                else:
                    next_test = next_test.sample(1, replace=True)  # 要是没有的话，重复出题。

            elif difficulty == 90:
                next_test = test_df[(test_df["knowledge_ids"].str.contains(false_knowledge_ids_list[0])) &
                                    (test_df["knowledge_num"] == 1) & (test_df["difficulty"] == 90)]

                if next_test.empty:
                    next_test = df_recall_group_90.sample(1, replace=True)  # 要是没有的话，重复出题。
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


    # 知识点为3个
    elif knowledge_ids_num == 3:
        pass

    else:
        pass









