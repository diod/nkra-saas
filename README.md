### Описание работы корпуса

Каждый корпус -- это коллекция документов с текстами на каком-то языке (иногда более чем на одном, например, в параллельном корпусе). Цель проекта ruscorpora.ru -- предоставить поиск по документам (и атрибутам документов/отдельных слов в этих документах). Для того, чтобы искать по документам, их нужно *предобработать* и *проиндексировать*. Предобработка -- это то, чем занимается saas (этот проект), индексация происходит на стороне Яндекс.Сервера. Мы с Яндекс.Сервером взаимодействуем только двумя способами: отправляем документы на индексацию и удаляем уже проиндексированные документы (через HTTP API).

Исходные документы лежат в отдельном SVN-репозитории и представлены в формате XML, например:

```
<?xml version="1.0" encoding="UTF-8"?>
<html>
   <head>
      <meta content="drama" name="fname" />
      <meta content="А.П. Чехов" name="author" />
      <meta content="муж|жен" name="sex" />
      <meta content="1860" name="birthday" />
      <meta content="Драма" name="title" />
      <meta content="1887" name="date" />
      <meta content="художественная" name="sphere" />
      <meta content="художественное чтение" name="type" />
      <meta content="Россия / XIX в." name="chronotop" />
      <meta content="нейтральный" name="style" />
      <meta content="н-возраст" name="audience_age" />
      <meta content="н-уровень" name="audience_level" />
      <meta content="большая" name="audience_size" />
      <meta content="Старое радио" name="source" />
      <meta content="электронный текст" name="medium" />
      <meta content="хорошее" name="quality" />
      <meta content="ПК устной речи" name="subcorpus" />
      <meta content="Осокина Я.|Савчук С.О." name="responsible" />
   </head>
   <body>
      <speach role="Лука" actor="Ростислав Плятт" sex="муж">
         Па́вел
         <distinct form="Васи́лич">Васи́льевич</distinct>
         / та́м кака́я-то да́ма пришла́ / ва́с спра́шивает. Уж це́лый ча́с дожида́ется.
      </speach>
      <speach role="Павел Васильевич" actor="Осип Абдулов" sex="муж">Ну́ её к чёрту́! Скажи́ / что я́ за́нят.</speach>
      <speach role="Лука" actor="Ростислав Плятт" sex="муж">
         Ведь она́ / Па́вел
         <distinct form="Васи́лич">Васи́льевич</distinct>
         / уж пя́ть ра́з приходи́ла. Говори́т / что о́чень ну́жно ва́с ви́деть. Чу́ть не пла́чет.
      </speach>
      <speach role="Павел Васильевич" actor="Осип Абдулов" sex="муж">Хм... Ну ла́дно / проси́ её в кабине́т.</speach>
   </body>
</html>
```

В сыром виде документы проиндексировать невозможно. Сначала их нужно прогнать через пайплайн [предобработки](https://github.com/oopcode/nkra-processing) (очень много плохо читаемого legacy кода). Этот пайплайн проверяет входные документы, токенизирует их, делает семантический разбор, etc.; для каждого типа корпуса существует свой sh-скрипт обработки; например, вот скрипт для основного корпуса:

```
#!/bin/sh

set -e

CORPUS=source
ROOT=/place/ruscorpora/corpora
SOURCE=$ROOT/main/$CORPUS
COMMON=$ROOT/tables
CLEAN=$SOURCE/texts
TABLES=$SOURCE/tables
TEXTS=/place/ruscorpora/texts
PREAUG=$TEXTS/pre-augmented/$CORPUS
AUG=$TEXTS/augmented/$CORPUS
FILTERED=$TEXTS/filtered/$CORPUS
FINAL=$TEXTS/finalized/$CORPUS
LOGS=logs
USERNAME=`whoami`

mkdir -p $LOGS
rm -rf $AUG
mkdir -p $AUG
rm -rf $FILTERED
mkdir -p $FILTERED
rm -rf $FINAL
mkdir -p $FINAL

python validate_xml.py $CLEAN
python ./meta.py $TABLES/$CORPUS.csv $CLEAN -check -utf
python ./meta.py $TABLES/$CORPUS.csv $TABLES/$CORPUS.tmp -convert -utf

python ruscorpora_tagging/annotate_texts.py --input $CLEAN --output $AUG --semdict tables/semantic.csv --add tables/add.cfg --del tables/del.cfg --jobs 4
python validate_xml.py $AUG

cd filters
./do.sh $CORPUS
cd -

rm -rf $AUG
python ./finalize-corpus_parallel.py $TABLES/$CORPUS.tmp $FILTERED $FINAL -utf
rm -rf $FILTERED
```

В результате предобработки мы получаем обогащенный XML-документ:

```
<?xml version="1.0" encoding="UTF-8"?>
<html>
   <head>
      <title>Title</title>
      <meta content="А.П. Чехов" name="grauthor" />
      <meta content="А.П. Чехов" name="author" />
      <meta content="муж | жен" name="grsex" />
      <meta content="муж" name="sex" />
      <meta content="жен" name="sex" />
      <meta content="1860" name="birthday" />
      <meta content="Драма (исп. О.Н. Абдулов, Р.Я. Плятт)" name="header" />
      <meta content="1950" name="created" />
      <meta content="1950" name="grcreated" />
      <meta content="театральная речь | нехудожественная" name="grsphere" />
      <meta content="театральная речь" name="sphere" />
      <meta content="нехудожественная" name="sphere" />
      <meta content="радиопостановка" name="grtype" />
      <meta content="радиопостановка" name="type" />
      <meta content="Россия: XIX в." name="chronotop" />
      <meta content="нейтральный" name="style" />
      <meta content="н-возраст" name="audience_age" />
      <meta content="н-уровень" name="audience_level" />
      <meta content="большая" name="audience_size" />
      <meta content="Аудио" name="subcorpus" />
      <meta content="1950" name="date-ex" />
      <meta content="«Старое радио»" name="company" />
      <meta content="Москва" name="not_place" />
      <meta content="«Старое радио» http://www.staroeradio.ru/" name="source" />
      <meta content="8uxcci9ex5.4703" name="video_id" />
      <meta content="208318" name="num" />
      <meta content="44" name="words" />
      <meta content="9" name="sentences" />
   </head>
   <body>
      <speach actor="Ростислав Плятт" age="42" birth="1908" role="Лука" sex="муж">
         <p>
            <se>
               <w accent="а1,а-2" after="е1" before="" number="2" orpho="АВ,ВЕ,ЕЛ_В,ЕЛ,ПА,АВЕ,ВЕЛ,_ПАВ,_ПА,ПАВ,Л_В,Л_ВА,ЕЛ_">
                  <ana disamb="yes" gr="S,anim,m,nom,norm,persn,sg" lex="павел" sem="t:hum r:propn t:persn" />
                  Па́вел
               </w>
               <distinct form="Васи́лич">
                  <w accent="и2,и-3" after="е1,и2" before="а1" number="4" orpho="ЬЕ,ИЛЬ,ЕВИ,Ч_Т,ВА,ИЧ_Т,ВИ,ВИЧ,СИ,_ВА,ЛЬ,Ч_ТА,ВАС,ИЧ_,_ВАС,ЛЬЕ,ЬЕВ,ИЛ,АСИ,СИЛ,ИЧ,ЕВ,АС">
                     <ana disamb="yes" gr="S,anim,m,nom,norm,patrn,sg" lex="васильевич" sem="t:hum t:patrn r:propn der:s" />
                     Васи́льевич
                  </w>
               </distinct>
               /
               <w accent="а1,а-1" after="" before="" number="1" orpho="М_КА,АМ,АМ_К,АМ_,ТА,_ТА,М_К,ТАМ,_ТАМ">
                  <ana disamb="yes" gr="ADVPRO,norm" lex="там" sem="t:place r:dem" />
                  та́м
               </w>
               <w accent="а2,а-3" after="я1,о2" before="а1" number="4" orpho="Я-Т,Я-,КАК,О_ДА,_КА,-Т,АК,АКА,_КАК,-ТО,АЯ-,ТО_,ТО_Д,КАЯ,О_Д,ТО,КА,АЯ">
                  <ana disamb="yes" gr="APRO,f,nom,norm,sg" lex="какой-то" sem="r:indet" />
                  кака́я-то
               </w>
               <w accent="а1,а-2" after="а1" before="" number="2" orpho="МА_П,МА,_ДА,АМ,МА_,А_П,А_ПР,ДА,АМА,_ДАМ,ДАМ">
                  <ana disamb="yes" gr="S,anim,f,nom,norm,sg" lex="дама" sem="t:hum r:concr" sem2="t:hum r:concr" />
                  да́ма
               </w>
               <w accent="а2,а-1" after="" before="и1" number="2" orpho="ШЛ,ИШ,ЛА,_ПР,А_ВА,ПРИ,ЛА_В,_ПРИ,РИШ,ИШЛ,РИ,ЛА_,А_В,ШЛА,ПР">
                  <ana disamb="yes" gr="V,act,f,indic,intr,norm,pf,praet,sg" lex="прийти" sem="der:v ca:noncaus t:move d:pref" sem2="der:v ca:noncaus d:pref" />
                  пришла́
               </w>
               /
               <w accent="а1,а-1" after="" before="" number="1" orpho="АС_С,ВА,АС_,ВАС,_ВАС,АС,С_С,С_СП,_ВА">
                  <ana disamb="yes" gr="SPRO,2p,loc,norm,pl" lex="вы" sem="r:pers" />
                  <ana disamb="yes" gr="SPRO,2p,acc,norm,pl" lex="вы" sem="r:pers" />
                  <ana disamb="yes" gr="SPRO,2p,gen,norm,pl" lex="вы" sem="r:pers" />
                  ва́с
               </w>
               <w accent="а1,а-4" after="и1,а2,е3" before="" number="4" orpho="ШИ,РАШ,ВА,_СПР,АЕ,_СП,ЕТ_,АЕТ,ШИВ,РА,АШИ,ВАЕ,СПР,ИВ,ПРА,АШ,ЕТ,ИВА,СП,ПР">
                  <ana disamb="yes" gr="V,3p,act,indic,ipf,norm,praes,sg,tran" lex="спрашивать" sem="t:speech ca:noncaus der:v d:pref d:impf" />
                  спра́шивает
               </w>
               .
            </se>
         </p>
      </speach>
      
      <...>
      
      <speach actor="Осип Абдулов" age="50" birth="1900" role="Павел Васильевич" sex="муж">
         <p>
            <se>
               <w accent="" after="" before="" number="0" orpho="ХМ,ХМ_,_ХМ">
                  <ana disamb="yes" gr="INTJ,norm" lex="хм" />
                  Хм
               </w>
               ...
            </se>
            <se>
               <w accent="" after="" before="у1" number="1" orpho="_НУ,НУ_,НУ,НУ_Л,У_Л,У_ЛА">
                  <ana disamb="yes" gr="PART,norm" lex="ну" />
                  Ну
               </w>
               <w accent="а1,а-2" after="о1" before="" number="2" orpho="НО_П,_ЛА,ЛА,АД,НО_,НО,АДН,ДН,ЛАД,_ЛАД,О_П,О_ПР,ДНО">
                  <ana disamb="yes" gr="PART,norm" lex="ладно" />
                  ла́дно
               </w>
               /
               <w accent="и2,и-1" after="" before="о1" number="2" orpho="_ПР,_ПРО,ПРО,СИ_,И_Е,И_ЕЁ,СИ,РОС,ОС,СИ_Е,РО,ОСИ,ПР">
                  <ana disamb="yes" gr="V,2p,act,imper,ipf,norm,sg,tran" lex="просить" sem="t:speech ca:caus d:root" sem2="d:root" />
                  проси́
               </w>
               <w accent="ё2,ё-1" after="" before="е1" number="2" orpho="ЕЁ_В,_ЕЁ,ЕЁ,Ё_В,ЕЁ_">
                  <ana disamb="yes" gr="SPRO,3p,acc,f,norm,sg" lex="она" sem="r:pers" />
                  <ana disamb="yes" gr="SPRO,3p,f,gen,norm,sg" lex="она" sem="r:pers" />
                  её
               </w>
               <w accent="" after="" before="" number="0" orpho="В_К,В_КА">
                  <ana disamb="yes" gr="PR,norm" lex="в" />
                  в
               </w>
               <w accent="е3,е-1" after="" before="и1,а2" number="3" orpho="НЕ,АБ,ИНЕ,_КА,НЕТ,КАБ,БИ,ЕТ_,ИН,АБИ,_КАБ,БИН,КА,ЕТ">
                  <ana disamb="yes" gr="S,acc,inan,m,norm,sg" lex="кабинет" sem="top:contain pc:constr:build t:room pt:part pc:room:appart r:concr" sem2="t:group sc:tool:furn top:contain pc:constr:build t:room pt:set sc:hum pt:part pc:room:appart r:concr" />
                  <ana disamb="yes" gr="S,inan,m,nom,norm,sg" lex="кабинет" sem="top:contain pc:constr:build t:room pt:part pc:room:appart r:concr" sem2="t:group sc:tool:furn top:contain pc:constr:build t:room pt:set sc:hum pt:part pc:room:appart r:concr" />
                  кабине́т
               </w>
               .
            </se>
         </p>
      </speach>
   </body>
</html>
```

Каждый документ разбит на предложения и слова, при каждом слове указаны грамматические и (не для всех корпусов) семантические признаки. Поиск можно вести по атрибутам документа целиком и атрибутам слов. **Важно:** в документе также остается *структура*, которая **сообщает нам, как его нужно отображать в выдаче** . Подробнее об этом будет ниже.

Когда предобработка закончена, мы можем отправить документы из корпуса на индексацию, например:

```
rm -f main* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/main/ --kps 10090 --subcorpus main --corpus_type main --nodisk > main.log 2>&1
```

Эта команда удаляет все служебные файлы, которые могли остаться с предыдущего запуска, затем запускает индексацию корпуса, лежащего в `--dir`.

* `--kps` говорит Яндекс.Серверу, что мы хотим, чтобы проиндексированные документы были ассоциированы с ID 10090 (любой uint, этот ID используется, чтобы изолировать документы одного корпуса от другого);
* `--subcorpus` и `--copus_type` указывают тип корпуса. Этих аргументов два, и схлопнуть в один их просто так нельзя, к сожалению (см. процедуру индексирования акцентолонического корпуса внизу этого документа).
* `--nodisk` заставляет скрипт сразу же отправлять документы на Яндекс.Сервер не оставлять промежуточных файлов на диске (см. ниже).

Скрипт `index.py` делает много вещей. Он обходит директорию с корпусом и:

1. Парсит каждый из документов в нем;
2. Формирует файл с сортировками и сохраняет их на диск (о сортировках -- ниже);
3. Каждый файл, если он большой, дробит на **части**;
4. Из каждой части *извлекается ее структура*. Структура древовидна и содержит информацию типа "У корня части есть два потомка типа `speach`. Первый потомок имеет такие-то атрибуты, покрывает предложения с 0-го по 3-е и имеет 3 потомка типа `se`." И так далее.
5. Для каждой части порождает еще более обогащенный XML **и** JSON-файл. XML выглядит почти так же, как в примерах выше, однако не содержит в себе информации о структуре документа: только набор предложений (`<se> ... </se>`) и слов (`<w> ... </w>`). JSON содержит иноформацию о структуре документа и о его атрибутах.
6. Если указан аргумент `--nodisk`, пара (XML, JSON) сразу же отправляется на идексацию (по HTTP API), если нет, то пара сохраняется на диск рядом с документом. Один документ может быть разбит на очень много частей, использовать `index.py` без аргумента `--nodisk` можно **только в отладочных целях**.

В процессе индексации создаются файлы `<corpus_type>.upload` и `<corpus_type>.upload.err`. Первый файл содержит путь к последнему обработанному документу (что позволяет продолжать загрузку с выбранного момента, а не каджый раз заново), второй -- пути документов, которые обработать не удалось (из-за каких-то ошибок).

Процедуры индексации разных типов корпусов перечислены внизу этого документа.

### APPENDIX: Поисковые атрибуты

Классификация документных атрибутов по назначению. Это немного лишняя информация, но пусть будет:

1. Поисковые (по ним можно задавать запросы). Могут быть как документными, так и зонными.
2. Группировочные (по ним можно группировать найденные документы или сортировать, могут быть только целочисленными). Только документные.
3. Свойства (просто выдаются по требованию вместе с найденным документом). Только документные.


Описание метаатрибутов в управляющем JSON'е.
Выглядит примерно так: "s_url": {"value": url, "type": "#hl"}.
Коды типов атрибутов (type):
#i - поисковый целочисленный атрибут
#l - поисковый литеральный атрибут
#g - группировочный целочисленный атрибут
#h - группировочный литеральный атрибут (вместо исходного значения в реальности будет содержать ui64-хеш от него)
#p - свойство (можно комбинировать с i и l)

Описание зонных атрибутов в индексируемом XML-документе.
Тут действует простое соглашение: если имя атрибута начинается с префикса "sz_", то это - литеральный атрибут.
Если с "iz_" - целочисленный (но такие зонные атрибуты у нас вроде бы не встречаются).

См. `index/index.py:370`:

```
obj = {
        'prefix': kps,
        'action': 'modify',
        'docs': [{
            'options': {
                'mime_type': 'text/xml',
                'charset': 'utf8',
                'language': 'ru',
                'realtime': 'false'
            },
            'url': {'value': url + '#%04d' % i},
            # For some corpora (paper) this value is intended to be used as a
            # list of dicts. Everything crashes if it's just a dict. Don't know
            # why it happens only sometimes.
            's_url': [{'value': url, 'type': '#hl'}],
            'p_url': [{'value': url, 'type': '#p'}],
            's_subindex': {'value': i, 'type': '#g'},
            'p_serp_part': {'value': p_serp_part, 'type': '#p'},
            'body': {'value': 'body_xml'},
        }],
    }
```

### APPENDIX: Запуск индексации для всех типов корпусов

# OLD_RUS

```
cd /place/ruscorpora/corpora/slav/old_rus/
svn up
cd /place/ruscorpora/processing/
sh old_rus.sh > old_rus.log 2>&1
cd /home/zavgorodny/saas/
rm -f old_rus* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/old_rus/ --kps 10000 --corpus_type old_rus --subcorpus old_rus --nodisk > old_rus.log 2>&1
```

# MID_RUS
```
cd /place/ruscorpora/corpora/slav/mid_rus/
svn up
cd /place/ruscorpora/processing/
sh mid_rus.sh > mid_rus.log 2>&1
cd /home/zavgorodny/saas/
rm -f mid_rus* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/mid_rus/ --kps 10010 --corpus_type mid_rus --subcorpus mid_rus --nodisk > mid_rus.log 2>&1
```

# BIRCHBARK
```
cd /place/ruscorpora/corpora/slav/birchbark/
svn up
cd /place/ruscorpora/processing/
sh birchbark.sh > birchbark.log 2>&1
cd /home/zavgorodny/saas/
rm -f birchbark* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/birchbark/ --kps 10020 --corpus_type birchbark --subcorpus birchbark --nodisk > birchbark.log 2>&1
```

# ORTHLIB
```
cd /place/ruscorpora/corpora/slav/orthlib/
svn up
cd /place/ruscorpora/processing/
sh orthlib.sh > orthlib.log 2>&1
cd /home/zavgorodny/saas/
rm -f orthlib* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/orthlib/ --kps 10030 --corpus_type orthlib --subcorpus orthlib --nodisk > orthlib.log 2>&1
```

# MULTIPARC
```
cd /place/ruscorpora/corpora/multiparc/eng-rus/
svn up
cd /place/ruscorpora/processing/
sh multiparc_eng-rus.sh > multiparc_eng-rus.log 2>&1
cd /home/zavgorodny/saas/
rm -f *multiparc_rus* && clear && python index.py --index --paired="eng|rus" --dir /place/ruscorpora/texts/finalized/multiparc_eng-rus/ --kps 10040 --subcorpus multiparc --corpus_type multiparc --nodisk > multiparc_eng-rus.log 2>&1
```

# MULTIPARC_RUS
```
cd /place/ruscorpora/corpora/multiparc/multiparc_rus/
svn up
cd /place/ruscorpora/processing/
sh multiparc_rus.sh > multiparc_rus.log 2>&1
cd /home/zavgorodny/saas/
rm -f multiparc_rus* && clear && python index.py --index --paired=".*(?=[0-9]{4}.xml)" --dir /place/ruscorpora/texts/finalized/multiparc_rus/ --kps 10050 --subcorpus multiparc_rus --corpus_type multiparc_rus --nodisk > multiparc_rus.log 2>&1
```

# MULTILANG
```
cd /place/ruscorpora/corpora/multi/
svn up
cd /place/ruscorpora/processing/
sh multi.sh > multi.log 2>&1
cd /home/zavgorodny/saas/
rm -f multilang* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/multi/ --kps 10060 --subcorpus multilang --corpus_type multilang --nodisk > multilang.log 2>&1
```

# PAPER
```
cd /place/ruscorpora/corpora/paper/
svn up
cd /place/ruscorpora/processing/
sh paper.sh > paper.log 2>&1
cd /home/zavgorodny/saas/
rm -f paper* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/paper/ --kps 10070 --subcorpus paper --corpus_type paper --nodisk > paper.log 2>&1
```

# MAIN
```
cd /place/ruscorpora/corpora/main/
svn up
cd /place/ruscorpora/processing/
sh source.sh > source.log 2>&1
sh standard.sh > standard.log 2>&1
rm -rf /place/ruscorpora/texts/finalized/main/
mkdir -p /place/ruscorpora/texts/finalized/main/standard
mkdir -p /place/ruscorpora/texts/finalized/main/source
lndir /place/ruscorpora/texts/finalized/standard /place/ruscorpora/texts/finalized/main/standard
lndir /place/ruscorpora/texts/finalized/source /place/ruscorpora/texts/finalized/main/source
cd /home/zavgorodny/saas/
rm -f main* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/main/ --kps 10090 --subcorpus main --corpus_type main --nodisk > main.log 2>&1
```

# PARA
```
cd /place/ruscorpora/corpora/para/
svn up
cd /place/ruscorpora/processing/
sh para.sh > para.log 2>&1
cd /home/zavgorodny/saas/
rm -f para* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/para/ --kps 10101 --corpus_type para --subcorpus para --nodisk > para.log 2>&1
```

# DIALECT
```
cd /place/ruscorpora/corpora/dialect/
svn up
cd /place/ruscorpora/processing/
sh dialect.sh > dialect.log 2>&1
cd /home/zavgorodny/saas/
rm -f dialect* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/dialect/ --kps 10110 --corpus_type dialect --subcorpus dialect --nodisk > dialect.log 2>&1
```

# POETIC
```
cd /place/ruscorpora/corpora/poetic/
svn up
cd /place/ruscorpora/processing/
sh poetic.sh > poetic.log 2>&1
cd /home/zavgorodny/saas/
rm -f poetic* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/poetic/ --kps 10120 --corpus_type poetic --subcorpus poetic --nodisk > poetic.log 2>&1
```

# ACCENT
```
cd /place/ruscorpora/corpora/accent/
svn up
cd /place/ruscorpora/processing/
sh accent.sh > accent.log 2>&1
cd /place/ruscorpora/texts/finalized/
mkdir -p accent/accent_main
mkdir -p accent/accent_stihi
mkdir -p accent/accent_poetic
lndir /place/ruscorpora/texts/finalized/accent_main /place/ruscorpora/texts/finalized/accent/accent_main
lndir /place/ruscorpora/texts/finalized/accent_stihi /place/ruscorpora/texts/finalized/accent/accent_stihi
lndir /place/ruscorpora/texts/finalized/poetic /place/ruscorpora/texts/finalized/accent/accent_poetic
cd /home/zavgorodny/saas/
rm -f accent* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/accent/ --kps 10130 --corpus_type accent --subcorpus accent --meta > accent.log 2>&1
cp accent.sortings accent_stihi.sortings
cp accent.sortings accent_poetic.sortings
clear && python index.py --index --dir /place/ruscorpora/texts/finalized/accent/accent_main/ --kps 10130 --corpus_type accent --subcorpus accent --nodisk > poetic.log 2>&1
clear && python index.py --index --dir /place/ruscorpora/texts/finalized/accent/accent_stihi/ --kps 10130 --corpus_type accent_stihi --subcorpus poetic --nodisk > poetic.log 2>&1
clear && python index.py --index --dir /place/ruscorpora/texts/finalized/accent/accent_poetic/ --kps 10130 --corpus_type accent_poetic --subcorpus poetic --nodisk > poetic.log 2>&1
```

# SPOKEN
```
cd /place/ruscorpora/corpora/spoken/
svn up
cd /place/ruscorpora/processing/
sh spoken.sh > spoken.log 2>&1
cd /place/ruscorpora/texts/finalized/
rm -rf /place/ruscorpora/texts/finalized/spoken_spoken
mv /place/ruscorpora/texts/finalized/spoken /place/ruscorpora/texts/finalized/spoken_spoken
mkdir /place/ruscorpora/texts/finalized/spoken
mv /place/ruscorpora/texts/finalized/spoken_spoken /place/ruscorpora/texts/finalized/spoken/spoken
mkdir /place/ruscorpora/texts/finalized/spoken/accent_main/
lndir /place/ruscorpora/texts/finalized/accent_main /place/ruscorpora/texts/finalized/spoken/accent_main
cd /home/zavgorodny/saas/
rm -f spoken* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/spoken/ --kps 10140 --corpus_type spoken_spoken --subcorpus spoken --meta > spoken.log 2>&1
cp spoken_spoken.sortings spoken_accent.sortings
clear && python index.py --index --dir /place/ruscorpora/texts/finalized/spoken/spoken/ --kps 10140 --corpus_type spoken_spoken --subcorpus spoken --nodisk > spoken_spoken.log 2>&1
clear && python index.py --index --dir /place/ruscorpora/texts/finalized/spoken/accent_main/ --kps 10140 --corpus_type spoken_accent --subcorpus accent --nodisk > spoken_accent.log 2>&1
```

# MURCO
```
cd /place/ruscorpora/corpora/murco/
svn up
cd /place/ruscorpora/processing/
sh murco.sh > murco.log 2>&1
cd /home/zavgorodny/saas/
rm -f murco* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/murco/ --kps 10150 --corpus_type murco --subcorpus murco --nodisk > murco.log 2>&1
```