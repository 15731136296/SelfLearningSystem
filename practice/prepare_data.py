import pandas as pd

path1 = "../test_library_info/math_department1_test_knowledge_trees.csv"
df_knowledge_trees = pd.read_csv(path1)

def get_knowledge_ids(knowledge_ids):
    """
    拆分知识点
    """
    knowledge_ids = str(knowledge_ids)
    if len(knowledge_ids) > 0:

        knowledge_ids_list = [int(i) for i in knowledge_ids.split(",") if i is not ""]

        knowledge_ids_list.sort()
        knowledge_trees_list = df_knowledge_trees["id"].to_list()

        knowledge_ids_list = [i for i in knowledge_trees_list if
                              i in knowledge_ids_list and knowledge_trees_list]  # 过滤掉不在知识树的ID

        if knowledge_ids_list:  # 过滤empty sequence空列表

            rank_string = df_knowledge_trees[df_knowledge_trees["id"] == max(knowledge_ids_list)]["rank_string"].values[
                0]
            rank_string_list = [rank_string]
            rank_string = [int(i) for i in rank_string.split(".") if i is not ""]

            diff = list(set(knowledge_ids_list).difference(set(rank_string)))

            while len(diff) > 0:
                rank_string_new = df_knowledge_trees[df_knowledge_trees["id"] == max(diff)]["rank_string"].values[0]
                rank_string_list.append(rank_string_new)

                rank_string_new = [int(i) for i in rank_string_new.split(".") if i is not ""]
                rank_string = list(set(rank_string).union(set(rank_string_new)))
                diff = list(set(knowledge_ids_list).difference(set(rank_string)))

            return rank_string_list[::-1]
    else:
        return

# knowledge_ids_list = [i for i in knowledge_trees_list if i in knowledge_ids_list and knowledge_trees_list] #过滤掉不在知识树的ID",32772,2,32754,34306,34591,34592"


def get_ids(knowledge_ids):
    """
    拆分知识点,得到叶子节点
    """
    knowledge_ids = str(knowledge_ids)
    if len(knowledge_ids) > 0:

        knowledge_ids_list = [int(i) for i in knowledge_ids.split(",") if i is not ""]

        knowledge_ids_list.sort()
        knowledge_trees_list = df_knowledge_trees["id"].to_list()

        knowledge_ids_list = [i for i in knowledge_trees_list if
                              i in knowledge_ids_list and knowledge_trees_list]  # 过滤掉不在知识树的ID

        if knowledge_ids_list:  # 过滤empty sequence空列表

            rank_string = df_knowledge_trees[df_knowledge_trees["id"] == max(knowledge_ids_list)]["rank_string"].values[
                0]
            rank_string_list = [rank_string]
            id_list = [max(knowledge_ids_list)]
            rank_string = [int(i) for i in rank_string.split(".") if i is not ""]

            diff = list(set(knowledge_ids_list).difference(set(rank_string)))

            while len(diff) > 0:
                rank_string_new = df_knowledge_trees[df_knowledge_trees["id"] == max(diff)]["rank_string"].values[0]
                id_list.append(max(diff))
                rank_string_list.append(rank_string_new)

                rank_string_new = [int(i) for i in rank_string_new.split(".") if i is not ""]
                rank_string = list(set(rank_string).union(set(rank_string_new)))
                diff = list(set(knowledge_ids_list).difference(set(rank_string)))

            id_list.sort()
            return id_list
    else:
        return


def prepare_data(path1, path2, path3):
    """
    获得预处理数据

    :param path1:
    :param path2:
    :param path3:
    :return:
    """


    df_knowledge_trees = pd.read_csv(path1)
    df_test_info = pd.read_csv(path2)
    df_test_info_1 = df_test_info[
        ["test_id", "knowledge_ids", "knowledge_num", "empty_knowledge", "difficulty", "test_type",
         "subject_id", "department_id", "grade_ids"]]

    df_test_info_new = df_test_info_1[-df_test_info_1["knowledge_ids"].isnull()]

    df_test_info_new["knowledge_ids_split"] = df_test_info_new["knowledge_ids"].apply(get_knowledge_ids)
    df_test_info_new["ids_split"] = df_test_info_new["knowledge_ids"].apply(get_ids)
    df_test_info_clear = df_test_info_new[-df_test_info_new["knowledge_ids_split"].isnull()]

    df_test_info_clear.to_csv(path3, index=False)

    return df_test_info_clear


if __name__ == '__main__':

    path1 = "../test_library_info/math_department1_test_knowledge_trees.csv"
    path2 = "../test_library_info/test_info.csv"
    path3 = "../test_library_info/test_info_clear.csv"

    prepare_data(path1,path2,path3)