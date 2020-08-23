# Vzpostavitev visoko interaktivnega sistema za opazovanje obnaˇsanja napadalcev

Repozitorji za gradiva magistrske naloge.

## Povzetek

Trenutno smo v obdobju velikega zanimanja za kibernetsko varnost, saj je napadov na povezane naprave vedno več. 
Ena izmed možnosti kako lahko pomagamo k boljši varnosti je tudi uporaba pasti za napadalce (angl. honeypots).
To je koncept elektronskih pasti, ki ga postavimo na omrežje, da ga je mogoče napasti in ogroziti. Med tem pa
pasti za napadalce zbirajo podatke o napadih. Večina pasti ne podpira visoke interaktivnosti, kar pripomore 
k hitrejšemu odkritju, da gre za lažno napravo. Da bi naredili pasti čim bolj zanimive za napadalca želimo 
simulirati realen sistem s poljubnim operacijskim sistemom in storitvami. Ker so zbrani podatki
na različnih lokacijah želimo postavili sistem za centralno beleženje in analizo podatkov. Izziv pri 
nameščanju pasti je tudi vzpostavitev skalabilne in fleksibilne infrastrukture. Ta problem je viden tako pri 
nameščanju velikega števila pasti, kot tudi pri vzpostavitvi sistema za shranjevanje in analizo podatkov.

V magistrskem delu smo smo najprej predstavili tehnologijo pasti in izbrali najprimernejšo past za našo 
nalogo. Nato smo predstavili tehnologije, ki smo jih uporabili v našem sistemu za opazovanje napadalcev. 
Opisali smo delovanje Docker kontejnerjev, orkestracijskega orodja Kubernetes in sistema za centralno 
beleženje podatkov. V nadaljevanju smo opisali posamezne faze vzpostavitve visoko interaktivnega 
kontejneriziranega sistema pasti z oddaljenim dostopom preko ukazne lupine ter težave in rešitve, ki so se 
pri tem pojavile. Poglobili smo se tudi v varnost kontejnerjev in na načine urejanja in shranjevanja 
podatkov. Na koncu smo vzpostavili delujoč sistem in predstavili še njegove možne izboljšave.