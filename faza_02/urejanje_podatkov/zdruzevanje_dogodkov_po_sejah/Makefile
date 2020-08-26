run:
	@echo "Running cowrie-data-extractor.py..."
	python3 ./cowrie-data-extractor/cowrie-data-extractor.py

run-d:
	@echo "Running cowrie-data-extractor.py in background..."
	nohup ./cowrie-data-extractor/cowrie-data-extractor.py > data/output.log &

init:
	sudo apt install python3-pip -y
	sudo apt install sqlite3 -y
	pip3 install -r ./requirements.txt
	pip3 install requests --upgrade

clean:
	rm -f cowrie_data.db
	rm -f ./data/unique_sessions.txt
	rm -f ./data/skipped_sessions.txt

table:
	@echo "Creating table..."
	python3 ./cowrie-data-extractor/create_database_table.py
	@echo "Table created."
