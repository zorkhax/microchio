# Тестовое задание:

===============================================================

Написать на Python приложение, реализующее некий симбиоз чата и микроблога. 

Требования к приложению:

1. Приложение должно позволять любому зашедшему пользователю оставлять на странице сообщения.

2. Пользователь должен иметь возможность задать себе имя. Нет необходимости в регистрации и логине, можно идентифицировать пользователей по куки.

3. Сообщение должно включать в себя текст и/или аттачменты (может быть только текст, только аттачменты, или и то, и другое). В качестве аттачментов могут выступать:
 - картинки, загружаемые с компьютера пользователя;
 - простые ссылки;
 - ролики c youtube.
 Приложение должно позволять добавить по несколько аттачментов каждого типа.

4. У каждого сообщения должна быть кнопка Like и счётчик количества нажатий кнопки.

5. У каждого сообщения должно быть показано время его отправки.

6. Пользователь, создавший сообщение, должен иметь возможность его удалить.

7. Новые сообщения, созданные пользователями, должны появляться в браузерах других пользователей без необходимости нажатия Refresh. Таким же образом должны исчезать удалённые сообщения и обновляться счётчики нажатий Like.


Требования к платформе:

1. Задание должно быть реализовано на фреймворке Flask.

2. В качестве СУБД приложение может использовать любую БД.

3. Требуемая версия Python - 2.7.x

4. Можно использовать jquery, mootools и т.п.


Цель задания - дать вам возможность продемонстрировать, что вы умеете и как вы мыслите, а не только лишь получить продукт, удовлетворяющий приведённым требованиям. Поэтому требования намеренно описаны не очень подробно, и мы ожидаем от вас проявления творческой фантазии. Также, если вы хотите обратить наше внимание на какие-либо особые навыки, мы будем рады, если вы продемонстрируете их. Будут анализироваться следующие аспекты вашей работы: 
- Качество реализации функциональности;
- Логичность и понятность пользовательского интерфейса;
- Качество, структурированность, объектно-ориентированность и читаемость кода;
- Общая архитектура приложения, разумное использование паттернов проектирования и других принципов "хорошего тона" в программировании;
- Знание интересных и необычных техник.

===============================================================


#Инструкция по развёртыванию.

Рекомендации буду давать относительно системы Ubuntu 13.10.


1. Для начала необходимо установить Python версии 2.6.5 или выше и python-dev
  * sudo apt-get install -y python2.7 python-dev

2. Установить pip
  * sudo apt-get install -y python-pip

3. Создать и активировать окружение
  * Удобно использовать virtualenvwrapper
  * pip install virtualenvwrapper
  * export WORKON_HOME=~/Envs
  * mkdir -p $WORKON_HOME
  * source /usr/local/bin/virtualenvwrapper.sh
  * mkvirtualenv microchio
  * workon microchio

4. Установить необходимые библиотеки
  * pip install -r requirements.txt

5. Создать и обновить базу данных
  * ./db_create.py
  * ./db_upgrade.py

6. Запустить сервер
  * ./run.py

Приложение будет доступно из браузера, на http://localhost:5000/

Microchio основан на первой половине The Flask Mega-Tutorial от Miguel Grinberg: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
