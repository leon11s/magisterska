import base64



def _analize(command, session, id):
    counter_cat = 0
    counter_cd = 0
    counter_echo = 0
    counter_uname = 0
    counter_lscpu = 0
    counter_top = 0
    counter_w = 0
    counter_crontab = 0
    counter_which = 0
    counter_ls = 0
    counter_free = 0
    counter_rm = 0
    
    # COMMAND: cat * - reads data from files, and outputs their contents
    if command.startswith('cat'):
        counter_cat += 1
        
        '''
        >>> PATTERN - gettin the status of all mounted file systems
        - cat /proc/mounts
        '''
        mounted_files_patterns = ['cat /proc/mounts']
        if command in mounted_files_patterns:
            print('Command recognized: gettin the status of all mounted file systems')
            return ('SYSTEM INFORMATION', 'get_mounted_file_system')

        '''
        >>> PATTERN - getting number of CPU cores 
        - cat /proc/cpuinfo | grep name | wc -l
        - cat /proc/cpuinfo | grep model | grep name | wc -l
        '''
        number_of_cores_patterns = ['cat /proc/cpuinfo | grep name | wc -l',
                                    'cat /proc/cpuinfo | grep model | grep name | wc -l']
        if command in number_of_cores_patterns:
            print('Command recognized: getting number of CPU cores')
            return ('HARDWARE_INFORMATION', 'get_number_of_cpu_cores')
        
        '''
        >>> PATTERN - getting CPU name
        - cat /proc/cpuinfo | grep name | head -n 1 | awk '{print $4,$5,$6,$7,$8,$9;}'
        - cat /proc/cpuinfo | grep name | head -n 1
        '''
        cpu_names_patterns = ["cat /proc/cpuinfo | grep name | head -n 1 | awk '{print $4,$5,$6,$7,$8,$9;}'",
                                'cat /proc/cpuinfo | grep name | head -n 1']
        if command in cpu_names_patterns:
            print('Command recognized: getting name of CPU')
            return ('HARDWARE_INFORMATION', 'get_name_of_cpu')    
        
        '''
        >>> PATTERN - get file content
        - cat /var[FILE_PATH] | head [OPTIONS]
        '''
        command_splited = command.split(' ')
        if command_splited[2] == '|' and command_splited[3] == 'head' and command_splited[1].startswith('/var'):
            print('Command recognized: getting content of file', command_splited[1])
            return ('FILE_AND_DIRECTORY_COMMANDS', 'get_file_content')
        else:
            print(command) 
            return (0, 'not_found_cat') 

    # COMMAND: cd * - change directory
    if command.startswith('cd'):
        counter_cd += 1
        '''
        >>> PATTERN - change directory to /var/tmp - directory is made available for programs 
        that require temporary files or directories that are preserved between system reboots
        - cd /var/tmp
        '''
        change_directory_var_tmp = ['cd /var/tmp']
        if command in change_directory_var_tmp:
            print('Command recognized: change directory to /var/tmp')
            return ('DIRECTORY_NAVIGATION', 'change_directory_var_tmp')

        '''
        >>> PATTERN - change directory to [PATH]
        - cd /[PATH]
        '''
        command_splited = command.split(' ')
        if len(command_splited) == 2 and command_splited[1].startswith('/'):
            print('Command recognized: change directory to:', command_splited[1])
            return ('DIRECTORY_NAVIGATION', 'change_directory')    
        else:
            print(command) 
            return (0, 'not_found_cd')

    # COMMAND: free * - Display free and used memory
    if command.startswith('free'):
        counter_free += 1
        '''
        >>> PATTERN - Display free and used memory
        - free -m | grep Mem | awk '{print $2 ,$3, $4, $5, $6, $7}'
        - free -m
        '''
        free_mem = ["free -m | grep Mem | awk '{print $2 ,$3, $4, $5, $6, $7}'",
                    'free -m']
        if command in free_mem:
            print('Command recognized: Display free and used memory')
            return ('PERFORMANCE_MONITORING_AND_STATISTICS', 'get_free_used_memory')
        else:
            print(command) 
            return (0, 'not_found_free')        

    # COMMAND: lscpu * - displays information about the CPU architecture
    if command.startswith('lscpu'):
        counter_lscpu += 1
        '''
        >>> PATTERN - getting model of CPU
        - lscpu | grep Model
        '''
        lscpu_model = ['lscpu | grep Model']
        if command in lscpu_model:
            print('Command recognized: getting model of CPU')
            return ('HARDWARE_INFORMATION', 'get_model_of_cpu')
        else:
            print(command) 
            return (0, 'not_found_lscpu') 

    # COMMAND: top * - Display and manage the top processes
    if command.startswith('top'):
        counter_top += 1
        '''
        >>> PATTERN -  show the Linux processes
        - top
        '''
        top = ['top']
        if command in top:
            print('Command recognized: show the Linux processes')
            return ('PERFORMANCE_MONITORING_AND_STATISTICS', 'show_linux_processes')
        else:
            print(command) 
            return (0, 'not_found_top') 

    # COMMAND: which * - Find command location
    if command.startswith('which'):
        counter_which += 1
        '''
        >>> PATTERN - Location of the input command
        - which [command-name]
        '''
        command_splited = command.split(' ')
        if not command_splited[1].startswith('-'):
            print('Command recognized: Get location of ' +  command_splited[1] + ' command.')
            which_command_str = 'get_location_of_command_' + command_splited[1]
            return ('SYSTEM INFORMATION', which_command_str)
        else:
            print(command) 
            return (0, 'not_found_which')

    # COMMAND: ls * - lists files and directories
    if command.startswith('ls'):
        counter_ls += 1
        '''
        >>> PATTERN -  List files in a long listing (detailed) format
        - ls -lh
        - ls -la
        '''
        command_splited = command.split(' ', 2)
        ls_options = ['-lh', '-la']
        if command_splited[1].strip() in ls_options:
            print('Command recognized: List files in directory ' + command_splited[2])
            ls_command_string = 'list_files_in_' + command_splited[2]
            return ('FILE_AND_DIRECTORY_COMMANDS', ls_command_string)
        else:
            print(command) 
            return (0, 'not_found_ls')     

    # COMMAND: w * - Show who is logged in and what they are doing.
    if command.startswith('w'):
        counter_w += 1
        '''
        >>> PATTERN -  Show who is logged in and what they are doing.
        - w
        '''
        w = ['w']
        if command in w:
            print('Command recognized: show who is logged in and what they are doing')
            return ('USER_INFORMATION_AND_MANAGEMENT', 'show_logged_users_and_processes')
        else:
            print(command) 
            return (0, 'not_found_w')   

    # COMMAND: crontab * - Manage cron table
    if command.startswith('crontab'):
        counter_crontab += 1
        '''
        >>> PATTERN -  Display the current crontab.
        - crontab -l
        '''
        crontab_l = ['crontab -l']
        if command in crontab_l:
            print('Command recognized: Display the current crontab.')
            return ('CRONTAB_MANAGEMENT', 'show_current_crontab')
        else:
            print(command) 
            return (0, 'not_found_crontab')    

    # COMMAND: rm * - Remove (delete) file
    if command.startswith('rm'):
        counter_rm += 1
        '''
        >>> PATTERN - Forcefully remove directory recursively
        - rm -rf /[PATH]
        '''
        rm_rf= ['rm -rf']
        if command.split('/')[0].strip() in rm_rf:
            print('Command recognized: Forcefully remove directory /' + command.split('/',1)[1].strip())
            return ('FILE_AND_DIRECTORY_COMMANDS', 'forcefully_remove_directory_file')
        else:
            print(command) 
            return (0, 'not_found_rm')         

    # COMMAND: echo * - display line of text/string that are passed as an argument
    if command.startswith('echo'):
        counter_echo += 1
        '''
        >>> PATTERN - decode a base64 command and run with bash
        - echo "base64_encoded_command" | base64 --decode | bash
        '''
        command_splited = command.split('"')
        if command_splited[2].strip() == '| base64 --decode | bash':
            base64_encoded_command = command_splited[1]
            base64_decoded_command = base64.b64decode(base64_encoded_command).decode("utf-8")
            file_name = 'output_data/echo_script_' + session + '_' + str(id)
            with open(file_name, 'w') as f:
                f.write(base64_decoded_command)
            print('Command recognized: run a base64 encoded bash script')
            return ('SCRIPT_EXECUTION', 'run_a_base4_encoded_bash_script')

        '''
        >>> PATTERN -  create a file with the shell 
        - echo [TEXT_INPUT] > /[PATH]
        '''
        command_splited = command.split(' ')
        if len(command_splited) > 3:
            if command_splited[2] == '>' and command_splited[3].startswith('/'):
                print('Command recognized: Create file in ' + command_splited[3])
                return ('FILE_AND_DIRECTORY_COMMANDS', 'Creating file with shell')    

        '''
        >>> PATTERN - change user password
        - echo "[USR:PASS]"|chpasswd|bash
        '''
        if 'chpasswd' in command:
            command_splited = command.split('|')
            username = command_splited[0].split('"')
            username = username[1].split(':')[0]
            if command_splited[1] == 'chpasswd' and command_splited[2] == 'bash':
                print('Command recognized: Password cahange for ' + username)
                return ('USER_INFORMATION_AND_MANAGEMENT', 'Pawssword changed for ' + username) 

        else:
            print(command) 
            return (0, 'not_found_echo')

    # COMMAND: uname * - print system information
    if command.startswith('uname'):
        counter_uname += 1
        '''
        >>> PATTERN - Display the machine hardware name
        - uname -m
        '''
        uname_m = ['uname -m']
        if command in uname_m:
            print('Command recognized: Display the machine hardware name')
            return ('SYSTEM_INFORMATION', 'get_machine_hardware_name')
        
        '''
        >>> PATTERN - Display Linux system information
        - uname -a
        '''
        uname_m = ['uname -a']
        if command in uname_m:
            print('Command recognized: Display Linux system information')
            return ('SYSTEM_INFORMATION', 'get_Linux_system_information')

        '''
        >>> PATTERN - Display the machine hardware name
        - uname -s
        - uname
        '''
        uname_m = ['uname -s', 'uname']
        if command in uname_m:
            print('Command recognized: Display the kernel name')
            return ('SYSTEM_INFORMATION', 'get_kernel_name')    
        else:
            print(command) 
            return (0, 'not_found_uname')    



    else:
        print(command)     
        return 'not_found'   
        
       
   
def parse_command(commands, session, id):
    command_list = commands.split('; ')
    if len(command_list) == 1:
        command = command_list[0]
        return _analize(command,session, id)

    else:
        command_parsed = []
        for command in command_list:
            command_parsed_ = _analize(command, session, id)
            command_parsed.append(command_parsed_)
        
        return command_parsed
            
