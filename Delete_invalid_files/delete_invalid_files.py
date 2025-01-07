from time import sleep
import requests

# 配置区域

# API 端点
list_url = "https://www.example.com/api/v3/admin/file/list"
delete_url = "https://www.example.com/api/v3/admin/file/delete"

# 每次请求的列表数量
page_size = 1000

# 每次请求的间歇时间
sleep_time = 1

# 高级自定义区域

# 配置User-Agent与请求类型
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "content-type": "application/json;charset=UTF-8",
}

# 请求次数
request_count = {
    "count": 0,
    "error": 0
}

# 删除次数
delete_count = {
    "count": 0,
    "error": 0
}

def confirmation():
    while True:
        user_input = input("您确定要继续吗？ (YES/NO): ").strip().upper()
        if user_input == "YES":
            print("Starting...")
            print("----------------")
            return True
        elif user_input == "NO":
            print("----------------")
            print("stopped")
            exit()
        else:
            print("无效输入，请输入 'YES' 或 'NO'.")

# 启动时打印信息
def start_info() :
    print("Cloudreve 失效文件清理工具")
    print("----------------")
    print("请确保已经登录并且已经将Cookie保存到 Cookie.txt 文件")
    print("请确定已经完成测试，否则请不要运行此脚本")
    print("----------------")
    confirmation()



# 读取cookie
cookies = {}
with open('cookie.txt', 'r') as f:
    for line in f:
        # 分割每一行，并处理键值对
        for cookie in line.split(';'):
            # 去除首尾空格
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)  # 分割键和值
                cookies[key] = value


# 获取文件列表
def get_file_list(page):
    data = {
        "page": page,
        "page_size": page_size,
        "order_by": "id desc",
        "conditions": {},
        "searches": {}
    }
    response = requests.post(list_url, json=data, headers=headers, cookies=cookies)
    request_count["count"] + 1
    if response.status_code == 200:
        print(f"请求数据成功，数据数量: {len(response.json()['data']['items'])}")
        return response.json()
    else:
        print(f"获取文件列表失败，状态码：{response.status_code}")
        request_count["error"] + 1
        return None


# 判断用户是否失效
def is_invalid_user(user):
    return (user["ID"] == 0 and
            user["CreatedAt"] == "0001-01-01T00:00:00Z" and
            user["UpdatedAt"] == "0001-01-01T00:00:00Z" and
            not user["Email"])


# 删除文件
def delete_files(file_ids):
    data = {
        "id": file_ids,
        "force": False,
        "unlink": False
    }
    response = requests.post(delete_url, json=data, headers=headers, cookies=cookies)
    delete_count["count"] + 1
    if response.status_code == 200:
        result = response.json()
        print("请求删除成功")
        if result["code"] == 0:
            print(f"成功删除文件ID: {file_ids}")
        else:
            print(f"删除文件失败: {result['msg']}")
            delete_count["error"] + 1
    else:
        print(f"删除文件请求失败，状态码：{response.status_code}")
        delete_count["error"] + 1


# 主程序
def main():
    page = 1
    first_run = True
    first_total = 0

    # 启动时打印信息
    start_info()

    while True:
        # 限制请求频率
        sleep(sleep_time)
        file_data = get_file_list(page)
        if file_data is None:
            break

        total_files = file_data["data"]["total"]
        users = file_data["data"]["users"]
        file_ids_to_delete = []

        if first_run:
            print(f"处理前，共{total_files}个文件")
            first_total = total_files
            first_run = False

        for file in file_data["data"]["items"]:
            user_id = file["UserID"]
            #print(f"检查文件 {file['Name']}，用户 ID: {user_id}")
            if str(user_id) in users and is_invalid_user(users[str(user_id)]):
                print(f"找到了一个失效的用户文件，用户名: {user_id}")
                file_ids_to_delete.append(file["ID"])
            # else:
            #     print(f"用户有效{user_id}")

        if file_ids_to_delete:
            print(file_ids_to_delete)
            print(f"本次删除文件总数{len(file_ids_to_delete)}")
            # 页码会出现变动，所以先减一
            if(page <= 3):
                page = 1
            else:
                page - 2
            delete_files(file_ids_to_delete)

        # 判断是否继续分页
        if page * page_size >= total_files:
            print("----------------")
            print("已经到最后一页，结束程序")
            print(f"处理前，共{first_total}个文件\n处理后，共{total_files}个文件")
            print("----------------")
            print(f"总列表成功请求数: {request_count["count"]}")
            print(f"总列表失败请求数: {request_count["error"]}")
            print("----------------")
            print(f"总删除成功请求数: {delete_count["count"]}")
            print(f"总删除失败请求数: {delete_count["error"]}")
            print("----------------")
            break
        page += 1


if __name__ == "__main__":
    main()
