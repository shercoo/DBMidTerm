# DBMidTerm
数据库期中项目

## 本地运行步骤：

1.  安装mysql

2. 修改`MidTerm/settings.py`中`DATABASE`字段：

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'btForum',
            'USER': '${你的用户名}',
            'PASSWORD': '${你的密码}',
            "ATOMIC_REQUESTS": True,
        }
    }
    DATABASE_OPTIONS = { 'charset': 'utf8', }
    ```

3.  删除`btForum/migrations`目录下除`__init__.py`外所有文件


4. 在根目录下运行，完成数据库初始化：

    ```shell
   python manage.py makemigrations
   python manage.py migrate
    ```


5. 上一步必定会报错，因为django不支持创建视图，需要进入MySQL，或其它数据库编辑工具，在btForum数据库中手动创建视图：

```mysql
use btForum;
create view ratestats as
select `stats`.`torrent_id` AS `torrent_id`,
       `stats`.`min(score)` AS `minimum`,
       `stats`.`max(score)` AS `maximum`,
       `stats`.`avg(score)` AS `average`,
       `stats7`.`min7`      AS `min7`,
       `stats7`.`max7`      AS `max7`,
       `stats7`.`avg7`      AS `avg7`
from (((select `btforum`.`btforum_rate`.`torrent_id` AS `torrent_id`,
               min(`btforum`.`btforum_rate`.`score`) AS `min(score)`,
               max(`btforum`.`btforum_rate`.`score`) AS `max(score)`,
               avg(`btforum`.`btforum_rate`.`score`) AS `avg(score)`
        from `btforum`.`btforum_rate`
        group by `btforum`.`btforum_rate`.`torrent_id`)) `stats`
         left join ((select `btforum`.`btforum_rate`.`torrent_id` AS `torrent_id`,
                            min(`btforum`.`btforum_rate`.`score`) AS `min7`,
                            max(`btforum`.`btforum_rate`.`score`) AS `max7`,
                            avg(`btforum`.`btforum_rate`.`score`) AS `avg7`
                     from `btforum`.`btforum_rate`
                     where (`btforum`.`btforum_rate`.`time` >= (now() - 7000000))
                     group by `btforum`.`btforum_rate`.`torrent_id`)) `stats7`
                   on ((`stats`.`torrent_id` = `stats7`.`torrent_id`)));
```


6. 启动服务器
    ```shell
   python manage.py runserver
    ```


## 前端

*   地址 ：https://github.com/Leeson63/DBMidTermFrontend

