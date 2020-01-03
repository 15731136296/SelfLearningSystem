import redis


# pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
# redis 取出的结果默认是字节，我们可以设定 decode_responses=True 改成字符串

host = "39.98.180.205"
pool = redis.ConnectionPool(host=host, port=6379, db=1, decode_responses=True)
# pool = redis.ConnectionPool(host='localhost', port=6379, db=1, decode_responses=True)
red = redis.Redis(connection_pool=pool)


dict_1 = {"user_id": 1, "practice_id": 999 , "subject_id":2,
  "department_id":1, "grade_ids": 2, "textbook": 13796,
  "chapter":13803, "knowledge_ids": [13811, 13812, 13813]}

# dict_1["knowledge_ids"] = ",".join([str(i) for i in dict_1["knowledge_ids"]])
# red.expire("name_test", 86400) #设置60*60*24秒后释放,即24小时后释放
red.hmset("name_test", dict_1)


# dict_2 = {"test1": 1000, "test2": 2000}
# red.hmset("name_test", dict_2)
print(red.hgetall("name_test"))
# print(red.hmget("name_test", "user_id", "practice_id"))#输出:['aa', 'bb']
# print(red.exists("name_test"))
# print(red.hdel("name_test", "user_id"))#输出：












# 3.Hash类型：一个name对应一个dic字典来存储。
#在name对应的hash中批量获取键所对应的值
dic = {"key1": 111, "key2": 222}
# red.hmset("name_2", dic)

#释放
red.expire('name_2', 10)

# print(red.hget("name", "key2"))#输出:bb
# print(red.hmget("name", "key1", "key2"))#输出:['aa', 'bb']


# print(red.hget("name_1", "key2"))#输出:bb
# print(red.hmget("name_1", "key1", "key2"))#输出:['aa', 'bb']

# print(red.hget("name_2", "key2"))#输出:bb
#
# print(red.exists("name_2"))
# print(red.hdel("name_2", "key2"))#输出：1
# print(red.hdel("name_2", "key2"))#输出：1


# exists(self, name)
#
# #检查reis的name是否存在
#
# expire(self,name ,time)
#
# #为某个name的设置过期时间

#删除指定name对应的key所在的键值对，删除成功返回1，失败返回0
# print(red.hdel("name", "key1"))#输出：1







