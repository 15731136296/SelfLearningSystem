import pandas as pd



class Strategy():

    """
    策略介绍
    """

    def __init__(self, subject_id, department_id, grade_ids, textbook, chapter, leaves_chapters, practice_id):

        self.subject_id = subject_id
        self.department_id = department_id
        self.grade_ids = grade_ids
        self.textbook = textbook
        self.chapter = chapter
        self.leaves_chapters = leaves_chapters
        self.practice_id = practice_id
        self.knowledge_num = len(self.leaves_chapters)


    def choice_strategy(self, answer_list,time_consuming_list):

        if self.knowledge_num <= 3:
            print("使用策略一:10道题")
            return self.strategy_one(answer_list)

        else:
            print("使用策略二:25道题")
            return self.strategy_two(answer_list, time_consuming_list)

    def strategy_one(self, answer_list):
        """
        策略一
        条件: 知识点个数n小于等于3
        题量:10道
        难度策略:(1）连续答对4道题，题目难度上升一级；(2）连续答错2道题，题目难度降低一级。
        出题策略:
         |1|2|3|4|            ｜5————9｜                 |10|
        初始化4道简单题        [ 策略规则计算 ]          最后一道题为难题

        初始化4道题目，只含一个知识点的题目4道,最后一道是难题。
        中间5道题为错题同类型推荐和知识点组合题。
        推荐错题数量为: 错的知识点个数。
        推荐组合题型为: 知识点组合题型。
        """


        # 根据知识点和知识点个数匹配题目
        # self.leaves_chapters, self.knowledge_num
        # 初始化4道简单的题
        test_id = ["01", "02", "03", "04"]
        # post前台

        # 等待1234做题结果, 得到做题结果
        answer_list = [1, 1, 1, 1]




        #判断计算推送题目
        #等待5题结果
        # 判断计算推送题目
        # 等待6题结果
        # 判断计算推送题目
        # 等待7题结果
        # 判断计算推送题目
        # 等待8题结果
        # 判断计算 推送题目
        # 等待9题结果
        # 判断计算 推送题目







        answer = answer_list
        print(answer, time_consuming_list)

        if answer_list:
            pass

        pass

        # return answer

        pass
    def strategy_two(self):

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

    # 第一层
        # 题量: 2n道只含一个知识点的题目
        # post前台
        # 等待2n做题结果, 得到做题结果

    # 第二层

        # 排序策略

        # 根据第一层的答题结果和答题时长进行排序.
        # 优先级: 答错、答对（用时长）、答对（用时短）




        # # self.leaves_chapters, self.knowledge_num
        #
        # answer_list = answer_list
        # time_consuming_list = time_consuming_list
        #
        #
        # # return answer_list
        pass




def get_data():
    path3 = "../test_library_info/test_info_clear.csv"
    df = pd.read_csv(path3)
    return df





if __name__ == '__main__':

    #配置参数
    subject_id = 2  # 学科-数学
    department_id = 1  # 小学
    grade_ids = 4  # 年级
    textbook = 13796  # 教材
    chapter = 1000  # 章
    leaves_chapters = [10001, 100002, 10003]  # 章节\章节——叶子知识点
    # leaves_chapters = [10001, 100002, 10003, 10004]   # 章节\章节——叶子知识点
    practice_id = "100000"#用户练习记录ID



    # 调用类、方法
    strategy = Strategy(subject_id, department_id, grade_ids, textbook, chapter, leaves_chapters, practice_id)

    strategy.choice_strategy()
    # answer_list, time_consuming_list

    # 获得交互数据
    answer_list = [1, 1, 1, 1]
    time_consuming_list = [1.2, 1.2, 2.0, 3.0]

    answer_list.append(1)
    time_consuming_list.append(2.9)
    # print(answer_list, time_consuming_list)








    # df = get_data()
    # df_choice = df[(df["subject_id"] == subject_id) & (df["department_id"] == department_id) & (df["grade_ids"] == grade_ids)]