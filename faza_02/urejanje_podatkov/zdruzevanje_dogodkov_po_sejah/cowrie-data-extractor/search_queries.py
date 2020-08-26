from elasticsearch6 import Elasticsearch
import configparser
import time
import logging


config = configparser.ConfigParser()
config.read('./cowrie-data-extractor.conf')

sensor_filter_str = str(config['ELASTICSEARCH']['SENSOR_FILTER'])
sensor_filter_str = sensor_filter_str.split(',')
sensor_filter_str = [el.strip() for el in sensor_filter_str]

class ElasticsearchQueries:
    def __init__(self, ip, port):
        self.es = Elasticsearch([{'host':ip,'port':port}])

    def query_by_time(self, index_val, timestamp_gl, timestamp_lt, max_query_size=5000):
        '''
        # The from parameter defines the offset from the first result you want to fetch. 
        # The size parameter allows you to configure the maximum amount of hits to be returned.
        # Though from and size can be set as request parameters, they can also be set within the search body. from defaults to 0, and size defaults to 10.
        '''

        query_by_time = {
            "from" : 0,
            "size": max_query_size,
            "query": {
                "bool" : {
                    "must" : [
                        {"term" : { "eventid" : "cowrie.session.closed" }},
                        {
                            "range": {
                                "timestamp": {
                                    "gt": timestamp_gl,
                                    "lt": timestamp_lt
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                "timestamp": {
                    "order": "desc"
                }
                }
            ]
        }

        if sensor_filter_str == ['all']:
            query_by_time = query_by_time
        else:
            query_by_time['query']['bool']['must'].append({"terms" : { "sensor" : sensor_filter_str}})

        res = None
        while res is None:
            try:
                res = self.es.search(index=index_val, body=query_by_time)
            except:
                logging.error('query_by_time: No connection to ES!!!')
                time.sleep(15)    
        return res

    def query_by_session(self, index_val, timestamp_lt, session_id, max_query_size=5000):
        query_by_sesssion_id = {
            "from" : 0,
            "size": max_query_size,
            "query": {
                "bool" : {
                    "must" : [
                        {"term" : { "session" : session_id }},
                        {
                            "range": {
                                "timestamp": {
                                    "lt": timestamp_lt
                                }
                            }
                        }
                    ]
                }
            },
        "sort" : [
            { "timestamp" : {"order" : "asc"}}
        ]
        }

        res = None
        while res is None:
            try:
                res = self.es.search(index=index_val, body=query_by_sesssion_id)
            except:
                logging.error('query_by_session: No connection to ES!!!')
                time.sleep(15)    
        return res

