#### 武大校园网终端认证

个人用登录武大校园网终端小工具(已经懒的开浏览器了....)

##### 安装

```bash
	$ sudo pip install net-access-whu
```

##### 使用

* 直接登录

```bash
	$ net-access-whu -u 2020301260064 -p hellflame
```

* 配置文件登录

```bash
	$ net-access-whu -c login.json
```

`login.json` 文件格式
```
{
	"username": 2020301260064,
	"password": "hellflame"
}
```

之后就等着查看返回消息就好了

