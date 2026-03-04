# Hotel 项目 Docker 部署完整流程

## 一、环境准备

### 1.1 服务器要求
- 云服务器（阿里云/腾讯云等）
- 已安装 Docker
- MySQL 数据库（可本地或远程）

### 1.2 安装 Docker（如果未安装）
```bash
# Ubuntu
curl -fsSL https://get.docker.com | sh
sudo systemctl start docker
sudo systemctl enable docker

# CentOS
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
```

---

## 二、项目配置

### 2.1 目录结构
```
hotel/
├── app/
│   ├── api/
│   │   ├── model.py
│   │   ├── util.py
│   │   └── __init__.py
│   ├── route/
│   │   ├── user.py
│   │   ├── admin.py
│   │   └── __init__.py
│   └── static/
│       └── codes/          # 验证码图片目录
├── config.ini
├── Dockerfile
├── requirements.txt
├── run.py
└── hotel.sql               # 数据库初始化脚本
```

### 2.2 配置文件说明

**config.ini**（可选，代码中已有默认值）
```ini
[database]
host = 127.0.0.1
user = root
password = 123456
name = hotel
```

**requirements.txt**
```
Flask==2.0.3
Flask-SQLAlchemy==2.5.1
Flask-Login==0.6.2
Flask-Admin==1.5.8
PyMySQL==1.0.2
cryptography==41.0.7
requests==2.28.1
Werkzeug==2.0.3
```

### 2.3 Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
```

---

## 三、数据库配置

### 3.1 方式一：使用宿主机 MySQL

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE hotel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 导入数据
mysql -u root -p hotel < hotel.sql
```

### 3.2 方式二：使用 Docker MySQL

```bash
# 启动 MySQL 容器
docker run -d \
  --name mysql-hotel \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=hotel \
  -v mysql-data:/var/lib/mysql \
  -p 3306:3306 \
  mysql:8.0

# 等待 MySQL 启动后导入数据
docker exec -i mysql-hotel mysql -uroot -p123456 hotel < hotel.sql
```

---

## 四、构建与运行

### 4.1 构建镜像
```bash
cd hotel项目目录
docker build -t hotel-app .
```

### 4.2 运行容器

**方式一：使用宿主机 MySQL**
```bash
docker run -d \
  --name hotel \
  -p 5001:5000 \
  -e DB_HOST=127.0.0.1 \
  -e DB_USER=root \
  -e DB_PASSWORD=123456 \
  -e DB_NAME=hotel \
  --link mysql-hotel:mysql \
  hotel-app
```

**方式二：使用 Docker MySQL（推荐）**
```bash
docker run -d \
  --name hotel \
  -p 5001:5000 \
  -e DB_HOST=172.17.0.1 \
  -e DB_USER=root \
  -e DB_PASSWORD=123456 \
  -e DB_NAME=hotel \
  --link mysql-hotel:mysql \
  hotel-app
```

> 注意：`172.17.0.1` 是 Docker 默认网桥的网关 IP

### 4.3 Docker Compose 方式（推荐）

**docker-compose.yml**
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: hotel-mysql
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: hotel
    volumes:
      - mysql-data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  hotel:
    build: .
    container_name: hotel-app
    ports:
      - "5001:5000"
    environment:
      DB_HOST: mysql
      DB_USER: root
      DB_PASSWORD: 123456
      DB_NAME: hotel
    depends_on:
      mysql:
        condition: service_healthy
    volumes:
      - ./app/static/codes:/app/app/static/codes

volumes:
  mysql-data:
```

**启动**
```bash
docker-compose up -d
```

---

## 五、安全组/防火墙配置

### 5.1 云服务器安全组
在云控制台添加入站规则：
| 协议 | 端口 | 来源 |
|------|------|------|
| TCP | 5001 | 0.0.0.0/0 |
| TCP | 3306 | 你的IP（可选）|

### 5.2 服务器防火墙
```bash
# CentOS/RHEL
sudo firewall-cmd --add-port=5001/tcp --permanent
sudo firewall-cmd --reload

# Ubuntu
sudo ufw allow 5001/tcp
```

---

## 六、验证部署

### 6.1 检查容器状态
```bash
docker ps
docker logs hotel-app
```

### 6.2 测试访问
```bash
# 本地测试
curl http://127.0.0.1:5001

# 远程测试
curl http://162.14.107.126:5001
```

### 6.3 首次登录
- 访问：`http://你的IP:5001/user/login`
- 管理后台：`http://你的IP:5001/admin`
- 管理员账号：`admin` / `admin`（需在数据库中创建）

---

## 七、常用命令

```bash
# 查看日志
docker logs -f hotel-app

# 重启容器
docker restart hotel-app

# 停止容器
docker stop hotel-app

# 更新部署
docker-compose build
docker-compose up -d

# 进入容器调试
docker exec -it hotel-app /bin/bash
```

---

## 八、注意事项

1. **数据库连接**：确保 MySQL 允许远程连接或使用 Docker 网络
2. **端口映射**：`5001:5000` 表示宿主机 5001 映射到容器 5000
3. **数据持久化**：生产环境建议挂载 volumes 保留数据
4. **HTTPS**：生产环境建议使用 Nginx 反向代理 + HTTPS
