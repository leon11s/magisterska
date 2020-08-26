# Združevanje dogodkov po sejah (cowrie-data-aggregator)

Vsak dogodek v sistemu ElasticSearch je shranjen kot samostojen JSON objekt,
ki vsebuje polje z identifikatorjem seje. S pomočjo tega polja združimo vse
dogodke in agregiramo informacije za določeno sejo. Za to uporabimo skripto
cowrie-data-aggregator, ki pridobi podatke iz sistema ElasticSearch in ustvari
3 tabele (tabela z vsemi podatki za posamezno sejo, tabela z podatki o prijavah
v sistem, tabela z podatki o vnesenih ukazih). Pred združevanjem vedno
preverimo ali ima seja začetni cowrie.session.connect in končni dogodek
cowrie.session.closed. S tem zagotovimo, da shranimo le tiste seje, ki so bile
v celoti uspešno zaznane.


## Using make file
- In case make is not install on the system:
	- `sudo apt install make`

### Run a script
1) Edit the config file for your needs:
	- `nano cowrie-data-extractor.conf`

2) If you are running the script for the first time on the host, run the package installation:
	- `make init`

3) If you dont have a table in your database you can use the following command to create it:
	- `make table`

4) Run the script with:
	- `make run`
	- `make run-d` -> runs the script in background 

5) Clean the output data with:
	- `make clean`
