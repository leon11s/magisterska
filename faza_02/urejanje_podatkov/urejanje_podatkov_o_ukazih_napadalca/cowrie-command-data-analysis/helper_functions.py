import datetime

def append_session_id_to_file(session_id, file_name='output_data/inserted_sessions_commands'):
    with open(file_name, 'a') as file:
        file.write(session_id+'\n') 

def get_inserted_sessions_from_file(file_name='output_data/inserted_sessions_commands'):
    with open(file_name, 'r') as file:
        data = file.readlines()
        data = [line.strip() for line in data]
        return data

def remove_inserted_sessions(sessions):
    session_in = get_inserted_sessions_from_file()
    res = [i for i in sessions if i not in session_in]
    return res

def get_round_times(dt=None, date_delta=datetime.timedelta(minutes=10), to='down', interval=10):
    """
    Round a datetime object to a multiple of a timedelta
    dt : datetime.datetime object, default now.
    dateDelta : timedelta object, we round to a multiple of this, default 10 minutes.
    """
    round_to = date_delta.total_seconds()
    if dt is None:
        dt = datetime.datetime.now()

    seconds = (dt - dt.min).seconds

    if seconds % round_to == 0:
        rounding = (seconds + round_to / 2) // round_to * round_to
    else:
        if to == 'up':
            rounding = (seconds + round_to) // round_to * round_to
        elif to == 'down':
            rounding = seconds // round_to * round_to
        else:
            rounding = (seconds + round_to / 2) // round_to * round_to

    time = dt + datetime.timedelta(0, rounding - seconds, -dt.microsecond)

    time_start = time - datetime.timedelta(minutes=interval) - datetime.timedelta(minutes=10)
    time_start = time_start.strftime('%Y-%m-%d %H:%M:%S')

    time_end = time - datetime.timedelta(minutes=10)
    time_end = time_end.strftime('%Y-%m-%d %H:%M:%S')

    return (time_start, time_end)


# TESTING FUNCTIONS
if __name__ == "__main__":
    pass
    # # 1) TEST for append_session_id_to_file:
    # sessions = ['8447d4b473bf', '1247d447873b', '7447d4b473bf']
    # for session in sessions:
    #     append_session_id_to_file(session)

    # # 2) TEST for get_inserted_sessions_from_file:
    # data = ['d6bbb6a6a081', '4ed061397d87', 'cb4c5f287fac', '17d95c6eecc8', '0202ca31cc6a', 'b8bd105afdad', 'da19ef0caeed', 
    # '86d9afa44d31', 'fea2599d11e4', '7197eee85f2d', '6ed63614e7a8', '8241da6630da', 'aeeeaef1b86d', 'ecb821431033', 'a6afdad10a46', 
    # '3142f4990ab7', '947a80612309', '7d77b8560f1d', '468b3dd8f8d1', '6456eb15822a', '42153bd635b4', 'ddcf72cad272', '77ffd550cb7a', 
    # 'b409d31ff63b', 'd1b2f818dabf', 'ae92b28e3eaa', '8a746c1d4978', '49f6cf651125', 'eab32b8a9f9b', '6083ac1ad1a6', '430ebfbf0c1f',
    # '8447d4b473bf', '1247d447873b', '7447d4b473bf']
    
    # #get_inserted_sessions_from_file()
    # remove_inserted_sessions(data)
    

