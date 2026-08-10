<h1>Kufar Telegram Notifier</h1>
<p>
   <b>Kufar Telegram Notifier</b> — проект, состоящий из двух взаимодействующих частей:
</p>

<ul>
   <li>
      <b>C++ сервис</b> — периодически опрашивает API Kufar,
      выполняет поиск новых объявлений и отправляет найденные объявления
      в Telegram.
   </li>
   <li>
      <b>Python Telegram Bot</b> — предоставляет интерфейс для управления
      поисковыми запросами, пользователями и настройками, а также содержит
      административную панель и дополнительные инструменты управления
      программой.
   </li>
</ul>

<p>
   Python-бот использует SQLite для хранения данных пользователей и их
   ограничений. Конфигурация поисковых запросов по-прежнему хранится
   в <code>kufar-configuration.json</code>.
</p>

<p>
   Для стандартного использования проекта достаточно настроить файл
   <code>kufar-configuration.json</code> и запустить C++ сервис.
   Установка Python-компонента не является обязательной — он предназначен
   для упрощения настройки поисковых запросов через Telegram и может быть
   использован в качестве удобного графического интерфейса управления конфигурацией.
</p><br><br>
<pre>Если Вы являетесь администрацией Kufar и у Вас имеются претензии к данному проекту - обращайтесь в раздел «<i>Issues</i>» для обратной связи.</pre>
<p align="center">
   <img src="https://user-images.githubusercontent.com/83237609/180989226-ec24b7d5-63ea-4ed5-9830-dd40d27ee30d.png" width="600"/>
</p>
<h2>Требования</h2>

<ul>
   <li>C++20 совместимый компилятор</li>
   <li>CMake версии 3.5+</li>
   <li>Python 3.10+</li>
   <li>Telegram Bot Token</li>
</ul>

<h2>Python Telegram Bot</h2>

<p>
   Python-часть проекта представляет собой Telegram-бота для управления
   поисковыми запросами и настройки программы без необходимости вручную
   редактировать JSON-файлы.
</p>

<p>Бот предоставляет следующие возможности:</p>

<ul>
   <li>автоматически получать новые объявления с Kufar в Telegram боте;</li>
   <li>создавать несколько поисковых запросов;</li>
   <li>задавать различные параметры поиска для каждого запроса;</li>
   <li>хранение информации о пользователях в SQLite;</li>
   <li>обратная связь с разработчиком через Telegram;</li>
   <li>ограничивать количество запросов для пользователей Python-бота;</li>
   <li>административная панель;</li>
   <li>просмотр списка пользователей и их идентификаторов;</li>
   <li>просмотр поисковых запросов пользователей;</li>
   <li>управление индивидуальными лимитами поисковых запросов;</li>
   <li>получение текущей конфигурации программы через Telegram;</li>
   <li>просмотр и получение логов Python- и C++-частей проекта;</li>
</ul>

<h3>База данных</h3>

<p>
   Python-бот использует SQLite для хранения данных, связанных с
   пользователями и их настройками.
</p>

<p>
   База данных находится в файле
   <code>data/bot.db</code> и создаётся автоматически при первом запуске
   бота.
</p>

<p>
   В базе хранятся пользователи, их идентификаторы, имена пользователей
   и индивидуальные ограничения на количество поисковых запросов.
</p>

<h3>Обратная связь</h3>

<p>
   Пользователь может отправить сообщение разработчику через команду
   <code>/feedback</code>. Обращение передаётся в специальную telegram группу
   поддержки.
</p>

<p>
   Разработчик может ответить на обращение непосредственно через reply
   на сообщение в группе. Бот автоматически определяет пользователя,
   которому необходимо отправить ответ.
</p>

<h3>Административная панель</h3>

<p>
   Административная панель доступна только пользователю,
   указанному в конфигурации в разделе <code>"telegram"</code> по команде <code>/admin</code>.
</p>

<p>Через неё доступны:</p>

<ul>
   <li>просмотр пользователей;</li>
   <li>просмотр поисковых запросов;</li>
   <li>изменение лимитов пользователей;</li>
   <li>получение текущего файла конфигурации;</li>
   <li>просмотр логов Python- и C++-частей;</li>
   <li>получение последних логов, логов за текущий день или всех логов в виде ZIP-архива.</li>
</ul>

<h2>Структура проекта</h2>

<details>
   <summary>
      Дерево проекта
   </summary>

<pre>
.
├── cpp/            # C++ сервис поиска объявлений
├── python/         # Python Telegram Bot для управления конфигурацией
├── data/           # Файлы конфигурации и кэш в виде логов
├── build/          # Файлы сборки CMake
├── bin/            # Скомпилированные исполняемые файлы
├── README.md
├── .gitignore
└── LICENSE
</pre>

</details>
<h2>Конфигурация программы</h2>
<details>
   <summary>
      Настройка kufar-configuration.json
   </summary>
   <details>
      <summary>
         Telegram
      </summary>
      <b>bot-token</b> - токен вашего бота, который будет отправлять сообщения.<br>
      <b>chat-id</b> - идентификатор чата, в который будут отправляться сообщения.<br>
      <b>support-chat-id</b> - идентификатор группы, в которую будут отправляться сообщения обратной связи.(Перед запуском требуется добавить бота в группу)
   </details>
   <details>
      <summary>
         Queries <sup>(все поля - опциональны)</sup>
      </summary>
      <b>tag</b> - поисковой запрос. <sup>(text)</sup><br>
      <b>only-title-search</b> - осуществление поиска только в заголовках. <sup>(true/false)</sup>
      <details>
         <summary>
            Price
         </summary>
         <b>min</b> - минимальная цена (целочисленное значение в BYN).<br>
         <b>max</b> - максимальная цена (целочисленное значение в BYN).<br>
         <b>Пример:</b> "price": {"min": 0, "max": 800}         
      </details>
      <b>language</b> - язык. <sup>(text)</sup><br>
      <b>limit</b> - ограничение на количество получаемых объявлений за один запрос. <sup>(int)</sup><br>
      <b>currency</b> - валюта <sup>(text: BYR)</sup><br>
      <b>condition</b> - <a href="https://github.com/TechUnRestricted/Kufar-Telegram-Notifier/blob/4e5eb51e3664c5e4e96812a5e146e41087787484/include/kufar.hpp#L515">состояние</a> (новое / б/y = 1 / 2).<br>
      <b>seller-type</b> - <a href="https://github.com/TechUnRestricted/Kufar-Telegram-Notifier/blob/4e5eb51e3664c5e4e96812a5e146e41087787484/include/kufar.hpp#L520">тип продавца</a> (частное лицо / компания = 0 / 1).<br>
      <b>kufar-delivery-required</b> - только с Kufar Доставкой. <sup>(true/false)</sup><br>
      <b>kufar-payment-required</b> - только с Kufar Оплатой. <sup>(true/false)</sup><br>
      <b>kufar-halva-required</b> - только с Kufar Рассрочкой (Халва). <sup>(true/false)</sup><br>
      <b>only-with-photos</b> - только с фото. <sup>(true/false)</sup><br>
      <b>only-with-videos</b> - только с видео. <sup>(true/false)</sup><br>
      <b>only-with-exchange-available</b> - только с возможностью обмена. <sup>(true/false)</sup><br>
      <b>sort-type</b> - <a href="https://github.com/TechUnRestricted/Kufar-Telegram-Notifier/blob/4e5eb51e3664c5e4e96812a5e146e41087787484/include/kufar.hpp#L525">тип сортировки</a>. (убывание / возрастание = 1 / 2)<br>
      <b>category</b> - <a href="https://github.com/TechUnRestricted/Kufar-Telegram-Notifier/blob/4e5eb51e3664c5e4e96812a5e146e41087787484/include/kufar.hpp#L193">категория</a>. <sup>(int)</sup><br>
      <b>sub-category</b> - <a href="https://github.com/TechUnRestricted/Kufar-Telegram-Notifier/blob/4e5eb51e3664c5e4e96812a5e146e41087787484/include/kufar.hpp#L217">подкатегория</a>. <sup>(int)</sup><br>
      <b>region</b> - <a href="https://github.com/TechUnRestricted/Kufar-Telegram-Notifier/blob/4e5eb51e3664c5e4e96812a5e146e41087787484/include/kufar.hpp#L17">номер региона</a> для поиска объявлений. <sup>(int)</sup><br>
      <b>areas</b> - <a href="https://github.com/TechUnRestricted/Kufar-Telegram-Notifier/blob/4e5eb51e3664c5e4e96812a5e146e41087787484/include/kufar.hpp#L27">номера областей</a> для поиска объявлений. Пример: "areas": [1, 38, 4]<sup>(int)</sup><br>
      <b>start-time</b> - время(Unix timestamp), раньше которого объявления будут игнорироваться <sup>(int)</sup><br>
      <b>chat-id</b> - чат, в который будет отправлено сообщение. В случае пропуска этого поля будет использован чат, который объявлен глобально <sup>(text)</sup><br>
   </details>
   <details>
      <summary>
         Delays
      </summary>
      <b>query</b> - задержка (в секундах) перед переходом к следующему поисковому запросу.<br>
      <b>loop</b> - задержка (в секундах) перед повторением поиска по очереди с начала.<br>
   </details>
</details>
<details>
     <summary>
         Настройка cached-data.json
     </summary>
Настраивать данный файл не нужно.<br>
Достаточно убедиться в том, что он представляет из себя валидный JSON файл со структурой <code>[]</code> (массив).<br>
Предназначение: хранит в себе идентификаторы отправленных объявлений для предотвращения повторной отправки при перезапуске программы.
</details>

<h2>Сборка проекта</h2>

<h3>C++ часть</h3>

<p>Для сборки C++ части проекта выполните из корневой директории:</p>
<pre>
   <<code>cmake -S cpp -B build</code><br>
   <code>cmake --build build</code>
</pre>
<p>После успешной сборки исполняемый файл будет находиться в директории <code>bin/</code>.</p>

<h3>Python часть</h3>

<p>Перейдите в директорию <code>python/</code> и создайте виртуальное окружение:</p>
<pre><code>cd python python3 -m venv venv</code></pre>

<p>Активируйте виртуальное окружение:</p>
<pre><code>source venv/bin/activate</code></pre>

<p>Установите зависимости из <code>requirements.txt</code>:</p>
<pre><code>pip install -r requirements.txt</code></pre>


<h2>Запуск проекта</h2>

<h3>C++ часть</h3>
<p>После сборки C++ программу можно запустить из корневой директории проекта:</p>
<pre>
   <code>bin/Kufar-Telegram-Notifier</code>
</pre>

<h3>Python часть</h3>
<p>Сначала перейдите в директорию <code>python/</code> и активируйте виртуальное окружение:</p>
<pre>
   <code>cd [путь-к-проекту]/python source venv/bin/activate</code>
</pre>
<p>После этого запустите Telegram-бота:</p>
<pre>
   <code>python3 main.py</code>
</pre>
<p>Таким образом, проект состоит из двух частей: C++-программа выполняет основную работу с поиском объявлений, а Python-бот предоставляет удобный интерфейс для настройки запросов через Telegram.</p>

<p align="center">
   <img src="https://user-images.githubusercontent.com/83237609/181288185-7f9c23b0-32bf-4a1a-a3fd-168ed38255e1.png"/>
</p>
