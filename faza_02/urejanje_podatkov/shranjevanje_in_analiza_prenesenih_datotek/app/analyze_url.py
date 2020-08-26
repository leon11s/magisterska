import logging

from data_outputs import insert_sql_data
from urls_ops import unique_url_parser, find_file_ulrs
from files_ops import (file_downloader, 
                        file_information, 
                        file_hashing, 
                        file_base64_converter, 
                        file_virus_total_check,
                        file_saver,
                        file_remover)
from helpers.printer import print_debug

logger = logging.getLogger('cyberlab_files_analysis.analyze_url')

# # TODO: preimenuj povsod general file folder v tmp path in porpavi
# TODO: insert data to riak
# TODO: omeji Rekurzijo
# TODO: dodaj več api kljuučev za virus total

def analyze_url(url, parent_id=None):
    if parent_id == None: print('\n\n\n\n')
    print_debug(f'****************************************Analysing URL: {url}*********************************************')


    file_name = file_information.get_file_name(url)
    is_downloaded = file_downloader.download_file(url, file_name, timeout=3)
    if is_downloaded:
        # calculate file hash
        file_md5_hash = file_hashing.get_file_hash_md5(file_name)
        
        # check if file hash exists in the database
        if not insert_sql_data.hash_exists(file_md5_hash):
            print_debug(f"File with hash {file_md5_hash} doesn't exist in DB.")

            # get file info
            file_sha256_hash = file_hashing.get_file_hash_sha256(file_name)
            file_sha1_hash = file_hashing.get_file_hash_sha1(file_name)
            file_size = file_information.get_file_size(file_name, unit='KB')
            is_text_file = file_information.is_textfile(file_name)
            file_type = file_information.get_file_type(file_name)
            virus_total_infections_count, virus_total_report, virus_total_tokens = file_virus_total_check.get_report(file_md5_hash)
            payload_b64 = file_base64_converter.encode_file(file_name)
            file_path = file_saver.save_file(file_md5_hash, payload_b64)

            # preglej zip file -> TODO
            
            
            
            # print_debug(f'---> Filename: {file_name}, \
            #                     Size: {file_size}, \
            #                     Textfile: {is_text_file}, \
            #                     Filetype: {file_type},\
            #                     MD5 hash: {file_md5_hash},\
            #                     SHA256 hash: {file_sha256_hash}')

            file_data = {'md5_hash': [file_md5_hash],
                        'file_name': [file_name],
                        'parent_id': [parent_id],
                        'file_size_kb': [file_size],
                        'file_type': [file_type],
                        'sha256_hash': [file_sha256_hash],
                        'sha1_hash': [file_sha1_hash],
                        'is_text_file': [is_text_file],
                        'virus_total_infections_count': [virus_total_infections_count],
                        'virus_total_report': [virus_total_report],
                        'virus_total_tokens': [virus_total_tokens],
                        'file_path': [file_path],}

            insert_sql_data.insert_data(file_data, 
                                index='md5_hash', 
                                mode='append') 

            # rekruzivno preveri še za ostale urlje
            if is_text_file:  
                print('||||||||||||||||||||||||||||||||||||RECURSIVE||||||||||||||||||||||||||||||||||')
                urls = find_file_ulrs.get_urls(file_name) # TODO: popravi branje regexa 
                if urls:
                    url_id = insert_sql_data.get_file_id(file_md5_hash)
                    for url in urls:
                        analyze_url(url, parent_id=url_id)
                print('|||||||||||||||||||||||||||||||||RECURSIVE END||||||||||||||||||||||||||||||||||||||')
 

    # odstrani file iz mape files
    file_remover.remove_temp_files()

    
    print_debug('---------------')