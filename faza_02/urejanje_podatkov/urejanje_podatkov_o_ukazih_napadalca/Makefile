run:
	@echo "Running cowrie-command-data-analysis.py..."
	python3 ./cowrie-command-data-analysis/cowrie-command-data-analysis.py

clean:
	rm -rf ./output_data/*

table:
	@echo "Creating table..."
	python3 ./cowrie-command-data-analysis/create_tables.py
	@echo "Table created."

run-d:
	@echo "Running cowrie-command-data-analysis in background..."
	nohup ./cowrie-command-data-analysis/cowrie-command-data-analysis.py > output_data/output.log &
