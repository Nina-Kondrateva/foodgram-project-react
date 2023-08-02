Проект FOODGRAM предназначен для любителей вкусно покушать)
Если вы постоянно в поисках новых рецептов и желаете поделиться своими любимыми блюдами с другими, тогда вам к нам!

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Nina-Kondrateva/foodgram-project-react.git
```


Cоздать и активировать виртуальное окружение:
```
python -m venv venv
source venv/Script/activate
```


Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```


Выполнить миграции:
```
python manage.py migrate
```


Запустить проект:
```
python manage.py runserver
```

