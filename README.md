# DRRR CHATROOM    
---
这是一个学习Python框架Django和JS框架Vue时用来练手的项目，前端页面从头写，发现很多CSS的基础都忘了，Vue是从0开始。  
后端的话框架是Django，之前有接触并写过简单的CURD，核心的websocket聊天功能是用channels-redis实现，数据存储这块因为有不少的统计所以用了Mysql。  
代码还是比较面条式，会不断抽时间修改。  

## 功能介绍
登录:只需要输入昵称和选择头像即可生成用户登录，用户数据保存至Mysql方便统计。  
房间:一旦有房间新增或关闭会通过websocket推送给列表页所有用户让其拉取最新列表，创建房间后信息也是保存至Mysql。  
聊天:所有聊天信息后端仅做传递，不作任何保存，刷新页面后所有聊天记录将丢失。
## 环境要求
*  Python 3.6+ (建议用virtualenv)
*  Mysql 5.6+
*  Redis
## 安装 
1.到Mysql新建数据库，字符集utf8mb4

2.克隆、进入目录、安装组件:
```shell script
git clone https://github.com/straightedge4life/drrr-chatroom.git
cd drrr-chatroom/backend/drrr/webchat/
pip install -r requirements.txt
```
3.复制配置文件:
```shell script
cp config.py.example config.py
```
4.修改config.py文件:  
一般只需要修改 DATABASES、CHANNEL_LAYERS和ALLOWED_HOSTS即可，其中ALLOWED_HOSTS一般设置为['127.0.0.1',]  
  
5.启动后端
```shell script
python manage.py runserver 127.0.0.1:8828
```
6.Nginx配置  
假设：  
项目根目录在/var/www  
域名为www.my-drrr-chatroom.com  
  

```
# 前端
server {
    listen       80;
    server_name www.my-drrr-chatroom.com;
    index       index.html index.html index.php;
    charset     utf-8;
    root /var/www/drrr-chatroom/frontend/drrr/dist;

    access_log  /var/log/nginx/my-drrr-chatroom-fronend.access.log;
    error_log  /var/log/nginx/my-drrr-chatroom-fronend.error.log;

    location /{
    }
}

# 后端
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}


server {
    listen       8880;
    server_name www.my-drrr-chatroom.com;
    index       index.html index.html index.php;
    charset     utf-8;

    access_log  /var/log/nginx/my-drrr-chatroom-backend.access.log;
    error_log  /var/log/nginx/my-drrr-chatroom-backend.error.log;


    location /{
        proxy_redirect off;
        proxy_pass http://127.0.0.1:8828;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        #proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }

}
```
7.设置定时任务(每小时清除24小时前的数据)
```
*/60 * * * * python manage.py ClearData
```
## 一些待修复的问题
*  各前端页面的错误提示
*  列表页统计人数应该取Redis公共频道数据而非Mysql
*  因为允许断线重连(前端带上token)，所以需要增加定时任务清理断线后不再重连的Mysql用户数据。