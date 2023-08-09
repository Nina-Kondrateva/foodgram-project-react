Проект FOODGRAM предназначен для любителей вкусно покушать)
Если вы постоянно в поисках новых рецептов и желаете поделиться своими любимыми блюдами с другими, тогда вам к нам!
Здесь можно найти что-нибудь интересное для себя, подписаться на понравившихся авторов, добавлять любимые рецепты в избранное и даже распечатать все необходимые продукты для выбранных рецептов!

```
Адрес главной страницы сайта [https://mylovefood.hopto.org/](url)
```

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Nina-Kondrateva/foodgram-project-react.git
```

***На сервере установить Docker и Docker Compose***
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin;
```

***Переходим в директорию проекта***
```
cd foodgram/
```

***Создаем файл .env, в котором нужно указать данные:***
```
POSTGRES_DB=Имя базы данных
POSTGRES_USER=Имя пользователя
POSTGRES_PASSWORD=Пароль пользователя
DB_HOST=db
DB_PORT=5432
SECRET_KEY=(сгенерировать секретный ключ для Django)
ALLOWED_HOSTS=127.0.0.1, localhost, <доменное имя вашего сайта>
DEBUG=True
```

***Выполнить команды***
```
sudo docker compose -f docker-compose.production.yml up -d
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/static/. /static/
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_data
```

***Создаем суперпользователся***
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

***Устанавливаем и настраиваем NGINX***
```
sudo apt install nginx -y
sudo systemctl start nginx
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

Открываем конфигурационный файл NGINX
```
sudo nano /etc/nginx/sites-enabled/default
```
Полностью удаляем из него все и пишем новые настройки:
```
server {
    listen 80;
    server_name <доменное имя вашего сайта>;
    
    location / {
        proxy_set_header HOST $host;
        proxy_pass http://127.0.0.1:8000;

    }
}
```

Сохраняем изменения, выходим из редактора и выполняем команды
```
sudo nginx -t
sudo systemctl start nginx
```

***Настраиваем шифрование, получаем SSL-сертификат***
```
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --nginx
sudo systemctl reload nginx
```

**Примеры запросов**:
```
Зарегистироваться: https://mylovefood.hopto.org/signin
Главная страница: https://mylovefood.hopto.org/
Посмотерть конкретный рецепт: https://mylovefood.hopto.org/recipes/1
```

**Используемые технологии:**
```
Django REST
Python 3.2.3
JavaScript
Gunicorn
Nginx
PostgreSQL
Docker
```
**Автор Nina-Kondrateva**
