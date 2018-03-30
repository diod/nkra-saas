# OLD_RUS +

```
cd /place/ruscorpora/corpora/slav/old_rus/
svn up
cd /place/ruscorpora/processing/
sh old_rus.sh > old_rus.log 2>&1
cd /home/zavgorodny/saas/
rm -f old_rus* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/old_rus/ --kps 10000 --corpus_type old_rus --subcorpus old_rus --nodisk > old_rus.log 2>&1
```

# MID_RUS +
```
cd /place/ruscorpora/corpora/slav/mid_rus/
svn up
cd /place/ruscorpora/processing/
sh mid_rus.sh > mid_rus.log 2>&1
cd /home/zavgorodny/saas/
rm -f mid_rus* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/mid_rus/ --kps 10010 --corpus_type mid_rus --subcorpus mid_rus --nodisk > mid_rus.log 2>&1
```

# BIRCHBARK +
```
cd /place/ruscorpora/corpora/slav/birchbark/
svn up
cd /place/ruscorpora/processing/
sh birchbark.sh > birchbark.log 2>&1
cd /home/zavgorodny/saas/
rm -f birchbark* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/birchbark/ --kps 10020 --corpus_type birchbark --subcorpus birchbark --nodisk > birchbark.log 2>&1
```

# ORTHLIB +
```
cd /place/ruscorpora/corpora/slav/orthlib/
svn up
cd /place/ruscorpora/processing/
sh orthlib.sh > orthlib.log 2>&1
cd /home/zavgorodny/saas/
rm -f orthlib* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/orthlib/ --kps 10030 --corpus_type orthlib --subcorpus orthlib --nodisk > orthlib.log 2>&1
```

# MULTIPARC +
```
cd /place/ruscorpora/corpora/multiparc/eng-rus/
svn up
cd /place/ruscorpora/processing/
sh multiparc_eng-rus.sh > multiparc_eng-rus.log 2>&1
cd /home/zavgorodny/saas/
rm -f *multiparc_rus* && clear && python index.py --index --paired="eng|rus" --dir /place/ruscorpora/texts/finalized/multiparc_eng-rus/ --kps 10040 --subcorpus multiparc --corpus_type multiparc --nodisk > multiparc_eng-rus.log 2>&1
```

# MULTIPARC_RUS +
```
cd /place/ruscorpora/corpora/multiparc/multiparc_rus/
svn up
cd /place/ruscorpora/processing/
sh multiparc_rus.sh > multiparc_rus.log 2>&1
cd /home/zavgorodny/saas/
rm -f multiparc_rus* && clear && python index.py --index --paired=".*(?=[0-9]{4}.xml)" --dir /place/ruscorpora/texts/finalized/multiparc_rus/ --kps 10050 --subcorpus multiparc_rus --corpus_type multiparc_rus --nodisk > multiparc_rus.log 2>&1
```

# MULTILANG +
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

# PARA +
```
cd /place/ruscorpora/corpora/para/
svn up
cd /place/ruscorpora/processing/
sh para.sh > para.log 2>&1
cd /home/zavgorodny/saas/
rm -f para* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/para/ --kps 10101 --corpus_type para --subcorpus para --nodisk > para.log 2>&1
```

# DIALECT +
```
cd /place/ruscorpora/corpora/dialect/
svn up
cd /place/ruscorpora/processing/
sh dialect.sh > dialect.log 2>&1
cd /home/zavgorodny/saas/
rm -f dialect* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/dialect/ --kps 10110 --corpus_type dialect --subcorpus dialect --nodisk > dialect.log 2>&1
```

# POETIC +
```
cd /place/ruscorpora/corpora/poetic/
svn up
cd /place/ruscorpora/processing/
sh poetic.sh > poetic.log 2>&1
cd /home/zavgorodny/saas/
rm -f poetic* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/poetic/ --kps 10120 --corpus_type poetic --subcorpus poetic --nodisk > poetic.log 2>&1
```

# ACCENT +
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

# SPOKEN +
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

# MURCO +
```
cd /place/ruscorpora/corpora/murco/
svn up
cd /place/ruscorpora/processing/
sh murco.sh > murco.log 2>&1
cd /home/zavgorodny/saas/
rm -f murco* && clear && python index.py --index --dir /place/ruscorpora/texts/finalized/murco/ --kps 10150 --corpus_type murco --subcorpus murco --nodisk > murco.log 2>&1
```