import pandas as pd
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

def init():

    subject_id = 2  # 学科-数学
    department_id = 1  # 小学
    grade_ids = 4  # 年级
    textbook = 13796  # 教材
    chapter = 13803  #章
    knowledge_ids = [13811, 13812, 13813, 13814]# 章节\章节——叶子知识点
    # knowledge_ids = [13811, 13812, 13813, 13814, 13815]
    # 自己加载
    time_threshold = 15  # 初始化准备,加载学生信息。没有的话,设定一个值time_threshold = 60
    init = [subject_id, department_id, grade_ids, textbook, chapter, knowledge_ids]
    return init, knowledge_ids


def get_test_df():
    path3 = "../test_library_info/test_info_clear.csv"
    test_df = pd.read_csv(path3)
    return test_df



def receive_json():
    # 返回数据格式
    receive_results = [
        {"location": 1, "test_id": 200001, "is_true": 0, "difficulty": 0, "time_consuming": 40, "user_answer": "",
         "knowledge_ids": 13811},
        {"location": 2, "test_id": 200002, "is_true": 1, "difficulty": 0, "time_consuming": 2, "user_answer": "",
         "knowledge_ids": 13811},
        {"location": 3, "test_id": 200003, "is_true": 0, "difficulty": 0, "time_consuming": 3, "user_answer": "",
         "knowledge_ids": 13812},
        {"location": 4, "test_id": 200004, "is_true": 1, "difficulty": 0, "time_consuming": 9, "user_answer": "",
         "knowledge_ids": 13812},
        {"location": 5, "test_id": 200005, "is_true": 0, "difficulty": 0, "time_consuming": 4, "user_answer": "",
         "knowledge_ids": 13813},
        {"location": 6, "test_id": 200006, "is_true": 0, "difficulty": 0, "time_consuming": 2, "user_answer": "",
         "knowledge_ids": 13813},
        {"location": 7, "test_id": 200007, "is_true": 1, "difficulty": 0, "time_consuming": 3, "user_answer": "",
         "knowledge_ids": 13814},
        {"location": 8, "test_id": 200008, "is_true": 1, "difficulty": 0, "time_consuming": 19, "user_answer": "",
         "knowledge_ids": 13814}
    ]


    receive_json = {"status": "0", "message": "success", "data": receive_results}

    df_receive_results = pd.DataFrame(receive_json.get("data"))
    df_receive_results = df_receive_results.sort_values(["location"])

    is_true_list = df_receive_results["is_true"].to_list()
    knowledge_ids_list = df_receive_results["knowledge_ids"].to_list()

    return df_receive_results


def send_json():
    pass

def sorting_result(df_receive_results,time_threshold):

    """
    解析返回数据receive_json()
    """
    knowledge_ids_list = df_receive_results["knowledge_ids"].to_list()
    knowledge_ids_list = list(set(knowledge_ids_list))
    is_true_count = df_receive_results.groupby("knowledge_ids")["is_true"].sum().reset_index(name='count')
    is_true_count = is_true_count.sort_values("count")
    x_false_knowledge_ids_list = is_true_count[is_true_count["count"] < 2]["knowledge_ids"].to_list()
    true_knowledge_ids_list = is_true_count[is_true_count["count"] == 2]["knowledge_ids"].to_list()
    true_knowledge_ids_df = df_receive_results[
        (df_receive_results["knowledge_ids"].isin(true_knowledge_ids_list))]
    # 初始化准备,加载学生信息。没有的话,设定一个值time_threshold = 60

    if time_threshold is None:
        time_threshold = 60
    y_true_knowledge_ids_list = true_knowledge_ids_df[true_knowledge_ids_df["time_consuming"] > time_threshold][
        "knowledge_ids"].to_list()
    z_true_knowledge_ids_list = list(
        set(knowledge_ids_list) - set(x_false_knowledge_ids_list) - set(y_true_knowledge_ids_list))
    return [x_false_knowledge_ids_list, y_true_knowledge_ids_list, z_true_knowledge_ids_list]




if __name__ == '__main__':

    time_threshold = 15
    init, knowledge_ids = init()
    test_df = get_test_df()

    knowledge_ids = [str(i) for i in knowledge_ids]
    knowledge_ids_num = len(knowledge_ids)

    # 第一层
    # 题量: 25
    # n道只含一个知识点的题目


    # 备选集 初始化题目
    init = pd.DataFrame()

    T = []
    for i in range(knowledge_ids_num):
        df_recall_0 = test_df[(test_df["knowledge_ids"].str.contains(knowledge_ids[i])) & (test_df["knowledge_num"] == 1) & (
                    test_df["difficulty"] == 0)]

        # if df_recall_0.empty:
        #     init_test = df_recall_90.sample(2, replace=True)  # 要是没有的话，重复出题。
        # else:
        #     init_test = df_recall_0.sample(2, replace=True)  # 要是没有的话，重复出题。

        print("第" + str(i) + "个", knowledge_ids[i])
        print(df_recall_0)
        T.append(df_recall_0)
    print(T)
    print(T[0])
        # df_recall_90 = test_df[(test_df["knowledge_ids"].str.contains(knowledge_ids[i])) & (test_df["knowledge_num"] == 1) & (
        #             test_df["difficulty"] == 90)]




    #     if df_recall_0.empty:
    #         init_test = df_recall_90.sample(2, replace=True)  # 要是没有的话，重复出题。
    #     else:
    #         init_test = df_recall_0.sample(2, replace=True)  # 要是没有的话，重复出题。
    #     init.append(init_test)
    # df_test = init[["test_id", "ids_split"]].reset_index()
    # send_json = df_test.to_json()  # 待修改
    #
    # df_recall_group_0 = test_df[
    #     (test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] > 1) & (
    #                 test_df["difficulty"] == 0)]
    # df_recall_group_90 = test_df[
    #     (test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] > 1) & (
    #                 test_df["difficulty"] == 90)]






"""

#     #4、接收2n道题的返回数据和答题结果
    # receive_json()
    df_receive_results = receive_json()
    xyz_list = sorting_result(df_receive_results, time_threshold)
    x_false_knowledge_ids_list = xyz_list[0]
    y_true_knowledge_ids_list = xyz_list[1]
    z_true_knowledge_ids_list = xyz_list[2]
    x = len(x_false_knowledge_ids_list)
    y = len(y_true_knowledge_ids_list)
    z = len(z_true_knowledge_ids_list)

    print(x, y, z)
    print("test")

    if x > 0:
        if (25-2*knowledge_ids_num)/x < 2:

            print(x, y, z)
            print("出题策略为 1x_1y_1z_组合")

            for i in x_false_knowledge_ids_list:

                df_recall_x = test_df[(test_df["knowledge_ids"].str.contains(i)) & (test_df["knowledge_num"] == 1) & (test_df["difficulty"] == 0)].sample(1)
            for i in y_true_knowledge_ids_list:
                df_recall_y = test_df[(test_df["knowledge_ids"].str.contains(i)) & (test_df["knowledge_num"] == 1) & (test_df["difficulty"] == 0)].sample(1)

            for i in z_true_knowledge_ids_list:
                df_recall_z = test_df[(test_df["knowledge_ids"].str.contains(i)) & (test_df["knowledge_num"] == 1) & (test_df["difficulty"] == 90)].sample(1)

            new_test_df = pd.concat([df_recall_x, df_recall_y, df_recall_z], axis=0, ignore_index=True)

            group_num = 25 - new_test_df.shape[0]
            df_recall_group = test_df[(test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (test_df["knowledge_num"] > 1)].sample(group_num)


        elif (25 - 2 * knowledge_ids_num) / x > 2:
            print(x, y, z)
            print("出题策略为 2x_1y_1z_组合")

            for i in x_false_knowledge_ids_list:
                df_recall_x = test_df[
                    (test_df["knowledge_ids"].str.contains(i)) & (test_df["knowledge_num"] == 1) & (
                                test_df["difficulty"] == 0)].sample(2)
            for i in y_true_knowledge_ids_list:
                df_recall_y = test_df[
                    (test_df["knowledge_ids"].str.contains(i)) & (test_df["knowledge_num"] == 1) & (
                                test_df["difficulty"] == 0)].sample(1)

            for i in z_true_knowledge_ids_list:
                df_recall_z = test_df[
                    (test_df["knowledge_ids"].str.contains(i)) & (test_df["knowledge_num"] == 1) & (
                                test_df["difficulty"] == 90)].sample(1)

            new_test_df = pd.concat([df_recall_x, df_recall_y, df_recall_z], axis=0, ignore_index=True)

            group_num = 25 - new_test_df.shape[0]
            df_recall_group = test_df[(test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (
                        test_df["knowledge_num"] > 1)].sample(group_num)


    else:

        print(x, y, z)
        print("出题策略为 1y_1z_组合")
        for i in y_true_knowledge_ids_list:
            df_recall_y = test_df[
                (test_df["knowledge_ids"].str.contains(i)) & (test_df["knowledge_num"] == 1) & (
                        test_df["difficulty"] == 0)].sample(1)

        for i in z_true_knowledge_ids_list:
            df_recall_z = test_df[
                (test_df["knowledge_ids"].str.contains(i)) & (test_df["knowledge_num"] == 1) & (
                        test_df["difficulty"] == 90)].sample(1)

        new_test_df = pd.concat([df_recall_y, df_recall_z], axis=0, ignore_index=True)

        group_num = 25 - new_test_df.shape[0]
        df_recall_group = test_df[(test_df["knowledge_ids"].str.contains("13811|138112|138113")) & (
                test_df["knowledge_num"] > 1)].sample(group_num)


    # 发送排序题目

"""


#难点
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

